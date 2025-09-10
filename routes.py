from flask import render_template, request, redirect, url_for
from app import app, db
from models import Tournament, Player, Match
import random
from sqlalchemy import or_
from constants import POSITION_POINTS, BOT_PREFIX
from validators import sanitize_name, is_allowed_image, clamp_int
from services import (
    ensure_bots,
    human_distribution,
    take_distinct,
    player_in_any_match,
    filter_humans,
    totals_for_player_ids,
    top_n_players_by_totals,
    find_match_with_exact_players,
    compute_player_statistics,
)
from werkzeug.utils import secure_filename
import os

@app.route('/')
def index():
    tournaments = Tournament.query.all()
    return render_template('index.html', tournaments=tournaments)

@app.route('/create_tournament', methods=['POST'])
def create_tournament():
    name = sanitize_name(request.form.get('name'))
    if not name:
        return redirect(url_for('index', msg='Tournament name cannot be empty.', cat='danger'))
    tournament = Tournament(name=name)
    db.session.add(tournament)
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament.id))

@app.route('/tournament/<int:tournament_id>')
def tournament_detail(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = Player.query.filter_by(tournament_id=tournament_id).all()
    # Separate humans from bots for UI convenience
    human_players = filter_humans(players)
    bot_players = [p for p in players if p not in human_players]
    matches = Match.query.filter_by(tournament_id=tournament_id).order_by(Match.round).all()
    # Detect finals match: a match whose 4 players are the current top 4 humans by totals
    top4 = top_n_players_by_totals(human_players, matches, 4)
    top4_ids = [p.id for p in top4]
    finals_match = find_match_with_exact_players(matches, set(top4_ids)) if len(top4_ids) == 4 else None
    finals_exists = finals_match is not None
    champion_name = finals_match.winner.name if finals_match and finals_match.winner else None
    return render_template('tournament_detail.html', tournament=tournament, players=players, human_players=human_players, bot_players=bot_players, matches=matches, finals_exists=finals_exists, champion_name=champion_name)

@app.route('/tournament/<int:tournament_id>/add_player', methods=['POST'])
def add_player(tournament_id):
    name = sanitize_name(request.form.get('name'))
    if not name:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Player name cannot be empty.', cat='danger'))
    if name.startswith(BOT_PREFIX):
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Name cannot start with BOT prefix.', cat='danger'))
    # Handle optional image upload
    image_file = request.files.get('image')
    filename = None
    if image_file and image_file.filename:
        if not is_allowed_image(image_file):
            return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Invalid image file.', cat='danger'))
        safe = secure_filename(image_file.filename)
        # Prefix with tournament and player name to reduce collisions
        base, ext = os.path.splitext(safe)
        filename = f"t{tournament_id}_{base}{ext}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

    player = Player(name=name, tournament_id=tournament_id, image_filename=filename)
    db.session.add(player)
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))


@app.route('/tournament/<int:tournament_id>/player/<int:player_id>/upload', methods=['POST'])
def upload_player_image(tournament_id, player_id):
    """Upload/replace a player's photo."""
    player = Player.query.get_or_404(player_id)
    if player.tournament_id != tournament_id:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))
    image_file = request.files.get('image')
    if not image_file or not image_file.filename:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='No image selected.', cat='warning'))
    if not is_allowed_image(image_file):
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Invalid image file.', cat='danger'))
    safe = secure_filename(image_file.filename)
    base, ext = os.path.splitext(safe)
    filename = f"t{tournament_id}_p{player_id}{ext}"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)
    player.image_filename = filename
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Player photo updated.', cat='success'))

@app.route('/tournament/<int:tournament_id>/generate_bracket')
def generate_bracket(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = filter_humans(Player.query.filter_by(tournament_id=tournament_id).all())
    if len(players) < 4:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))

    # Get existing matches to track player pairings
    existing_matches = Match.query.filter_by(tournament_id=tournament_id).all()
    next_round = max([m.round for m in existing_matches], default=0) + 1

    # Calculate player statistics for balanced matching
    player_stats = {}
    for player in players:
        player_matches = [m for m in existing_matches if m.player1_id == player.id or m.player2_id == player.id or
                         m.player3_id == player.id or m.player4_id == player.id]

        total_score = 0
        wins = 0
        matches_played = len(player_matches)

        for match in player_matches:
            if match.player1_id == player.id and match.score1:
                total_score += match.score1
                if match.winner_id == player.id:
                    wins += 1
            elif match.player2_id == player.id and match.score2:
                total_score += match.score2
                if match.winner_id == player.id:
                    wins += 1
            elif match.player3_id == player.id and match.score3:
                total_score += match.score3
                if match.winner_id == player.id:
                    wins += 1
            elif match.player4_id == player.id and match.score4:
                total_score += match.score4
                if match.winner_id == player.id:
                    wins += 1

        avg_score = total_score / matches_played if matches_played > 0 else 0

        player_stats[player.id] = {
            'player': player,
            'matches_played': matches_played,
            'total_score': total_score,
            'avg_score': avg_score,
            'wins': wins
        }

    # Sort players by performance for balanced grouping
    sorted_players = sorted(player_stats.values(), key=lambda x: (x['total_score'], x['wins'], x['avg_score']), reverse=True)

    # For final round (if this is the championship round), pair best vs best, worst vs worst
    if next_round > 1 and len(sorted_players) >= 8:  # Only for championship rounds
        # Create championship matches: best vs best, worst vs worst
        top_players = sorted_players[:4]  # Top 4 players
        bottom_players = sorted_players[-4:]  # Bottom 4 players

        # Shuffle within groups to avoid same pairings
        import random
        random.shuffle(top_players)
        random.shuffle(bottom_players)

        # Create top bracket matches
        for i in range(0, len(top_players), 4):
            if i + 3 < len(top_players):
                match = Match(round=next_round,
                            player1_id=top_players[i]['player'].id,
                            player2_id=top_players[i+1]['player'].id,
                            player3_id=top_players[i+2]['player'].id,
                            player4_id=top_players[i+3]['player'].id,
                            tournament_id=tournament_id)
                db.session.add(match)

        # Create bottom bracket matches
        for i in range(0, len(bottom_players), 4):
            if i + 3 < len(bottom_players):
                match = Match(round=next_round,
                            player1_id=bottom_players[i]['player'].id,
                            player2_id=bottom_players[i+1]['player'].id,
                            player3_id=bottom_players[i+2]['player'].id,
                            player4_id=bottom_players[i+3]['player'].id,
                            tournament_id=tournament_id)
                db.session.add(match)
    else:
        # Regular round: Create balanced groups
        # Shuffle players to mix up groupings
        available_players = [p['player'] for p in sorted_players]
        random.shuffle(available_players)

        # Create matches with mixed skill levels
        for i in range(0, len(available_players), 4):
            if i + 3 < len(available_players):
                match = Match(round=next_round,
                            player1_id=available_players[i].id,
                            player2_id=available_players[i+1].id,
                            player3_id=available_players[i+2].id,
                            player4_id=available_players[i+3].id,
                            tournament_id=tournament_id)
                db.session.add(match)

    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))


@app.route('/tournament/<int:tournament_id>/plan_schedule', methods=['POST'])
def plan_schedule(tournament_id):
    """Create a group-stage schedule where each player gets N matches, using 4-player matches.
    Prefer matches with 3 humans + 1 bot. Fill with bots to 4. Avoid 1-human matches.
    """
    tournament = Tournament.query.get_or_404(tournament_id)
    try:
        games_per_player = int(request.form.get('games_per_player', '0'))
        games_per_player = clamp_int(games_per_player, 1, 20)
    except ValueError:
        games_per_player = 0

    players = Player.query.filter_by(tournament_id=tournament_id).all()
    # Allow planning with 2+ players; will fill with bots if needed
    if games_per_player <= 0 or len(players) < 2:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))

    existing_matches = Match.query.filter_by(tournament_id=tournament_id).all()
    next_round = max([m.round for m in existing_matches], default=0) + 1

    # Count already scheduled/played matches per player
    assigned = {p.id: 0 for p in players}
    for m in existing_matches:
        for pid in (m.player1_id, m.player2_id, m.player3_id, m.player4_id):
            if pid in assigned:
                assigned[pid] += 1

    # Determine target matches for each player
    base_target = {p.id: games_per_player for p in players}

    # Build a working list of player IDs repeated (target - assigned) times
    pool = []
    for p in players:
        need = max(0, base_target[p.id] - assigned[p.id])
        pool.extend([p.id] * need)

    random.shuffle(pool)

    bots = ensure_bots(tournament_id, 4)

    # Minimize matches, then prefer 3-human configuration
    total_appearances = len(pool)
    if total_appearances < 2:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))
    human_counts = human_distribution(total_appearances)

    matches_created = 0
    round_num = next_round
    for target in human_counts:
        if target <= 0:
            continue
        group = take_distinct(pool, min(target, 4))
        # If not enough distinct to reach target, try a smaller target >=2
        if len(group) < 2 and pool:
            # Put back and reshuffle to try later
            pool.extend(group)
            random.shuffle(pool)
            group = take_distinct(pool, 2)
        # Fill with bots to 4
        if len(group) < 4:
            bot_ids = [b.id for b in bots]
            bi = 0
            while len(group) < 4:
                group.append(bot_ids[bi % len(bot_ids)])
                bi += 1
        match = Match(round=round_num,
                      player1_id=group[0],
                      player2_id=group[1],
                      player3_id=group[2],
                      player4_id=group[3],
                      tournament_id=tournament_id)
        db.session.add(match)
        matches_created += 1
        # increment round after each match to separate visually
        round_num += 1

    # Any leftover appearances (due to distinct-constraint), drain with 3 or 2 humans, prefer 3
    while pool:
        target = 3 if len(pool) >= 3 else 2
        group = take_distinct(pool, target)
        if not group:
            break
        # Avoid 1-human matches
        if len(group) < 2:
            break
        bot_ids = [b.id for b in bots]
        bi = 0
        while len(group) < 4:
            group.append(bot_ids[bi % len(bot_ids)])
            bi += 1
        match = Match(round=round_num,
                      player1_id=group[0],
                      player2_id=group[1],
                      player3_id=group[2],
                      player4_id=group[3],
                      tournament_id=tournament_id)
        db.session.add(match)
        matches_created += 1
        round_num += 1

    if matches_created > 0:
        db.session.commit()

    return redirect(url_for('tournament_detail', tournament_id=tournament_id))


@app.route('/tournament/<int:tournament_id>/player/<int:player_id>/edit', methods=['POST'])
def edit_player(tournament_id, player_id):
    """Rename a non-bot player."""
    player = Player.query.get_or_404(player_id)
    if player.tournament_id != tournament_id:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))
    new_name = sanitize_name(request.form.get('name'))
    if not new_name:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Name cannot be empty.', cat='danger'))
    if new_name.startswith(BOT_PREFIX):
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Name cannot start with BOT prefix.', cat='danger'))
    # Don't allow renaming bots via UI route
    if player.name.startswith(BOT_PREFIX):
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Bot players cannot be renamed.', cat='warning'))
    player.name = new_name
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Player renamed.', cat='success'))


@app.route('/tournament/<int:tournament_id>/player/<int:player_id>/delete', methods=['POST'])
def delete_player(tournament_id, player_id):
    """Delete a non-bot player if they are not in any scheduled match."""
    player = Player.query.get_or_404(player_id)
    if player.tournament_id != tournament_id:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))
    if player.name.startswith(BOT_PREFIX):
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Bot players cannot be deleted.', cat='warning'))

    # Check if player is referenced in any match
    if player_in_any_match(player.id):
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Cannot delete player with scheduled matches. Reset matches first.', cat='danger'))

    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Player deleted.', cat='success'))

@app.route('/tournament/<int:tournament_id>/end_tournament')
def end_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = 'completed'
    db.session.commit()
    return redirect(url_for('tournament_results', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>/results')
def tournament_results(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    # Exclude BOTs from standings
    players = filter_humans(Player.query.filter_by(tournament_id=tournament_id).all())
    matches = Match.query.filter_by(tournament_id=tournament_id).all()

    # Calculate player statistics
    player_stats = compute_player_statistics(players, matches)

    return render_template('tournament_results.html', tournament=tournament,
                         player_stats=player_stats, matches=matches)


@app.route('/tournament/<int:tournament_id>/generate_finals')
def generate_finals(tournament_id):
    """Create a final match with the current top 4 players by points."""
    tournament = Tournament.query.get_or_404(tournament_id)
    # Only consider human players for finals
    players = filter_humans(Player.query.filter_by(tournament_id=tournament_id).all())
    matches = Match.query.filter_by(tournament_id=tournament_id).all()

    # Compute standings and get top 4
    totals = totals_for_player_ids(matches, {p.id for p in players})
    top4 = sorted(players, key=lambda p: totals.get(p.id, 0), reverse=True)[:4]
    if len(top4) < 4:
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))
    # Prevent duplicate finals: if a match already exists with these exact 4 players (any round), don't create another
    top4_set = {p.id for p in top4}
    if find_match_with_exact_players(matches, top4_set):
        return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Final already created.', cat='info'))

    existing_matches = Match.query.filter_by(tournament_id=tournament_id).all()
    next_round = max([m.round for m in existing_matches], default=0) + 1

    final_match = Match(round=next_round,
                        player1_id=top4[0].id,
                        player2_id=top4[1].id,
                        player3_id=top4[2].id,
                        player4_id=top4[3].id,
                        tournament_id=tournament_id)
    db.session.add(final_match)
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))


@app.route('/tournament/<int:tournament_id>/reset_matches', methods=['POST'])
def reset_matches(tournament_id):
    """Delete all matches for a tournament but keep players and tournament record."""
    tournament = Tournament.query.get_or_404(tournament_id)
    # Delete matches
    Match.query.filter_by(tournament_id=tournament_id).delete()
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='All matches removed.', cat='success'))


@app.route('/tournament/<int:tournament_id>/delete_all', methods=['POST'])
def delete_all(tournament_id):
    """Permanently delete tournament, its players, and matches."""
    tournament = Tournament.query.get_or_404(tournament_id)
    # Remove related matches and players first
    Match.query.filter_by(tournament_id=tournament_id).delete()
    Player.query.filter_by(tournament_id=tournament_id).delete()
    # Delete tournament
    db.session.delete(tournament)
    db.session.commit()
    return redirect(url_for('index', msg='Tournament deleted', cat='warning'))


@app.route('/tournament/<int:tournament_id>/edit', methods=['POST'])
def edit_tournament(tournament_id):
    """Rename a tournament from the front page."""
    tournament = Tournament.query.get_or_404(tournament_id)
    new_name = sanitize_name(request.form.get('name'))
    if not new_name:
        return redirect(url_for('index', msg='Tournament name cannot be empty.', cat='danger'))
    tournament.name = new_name
    db.session.commit()
    return redirect(url_for('index', msg='Tournament renamed.', cat='success'))

@app.route('/tournament/<int:tournament_id>/record_result/<int:match_id>', methods=['POST'])
def record_result(tournament_id, match_id):
    match = Match.query.get_or_404(match_id)

    # Support new position-based scoring; fallback to direct scores if provided
    pos1 = request.form.get('pos1')
    pos2 = request.form.get('pos2')
    pos3 = request.form.get('pos3')
    pos4 = request.form.get('pos4')

    if pos1 and pos2 and pos3 and pos4:
        # Convert positions to integer points
        try:
            p1 = int(pos1)
            p2 = int(pos2)
            p3 = int(pos3)
            p4 = int(pos4)
        except ValueError:
            return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Positions must be integers.', cat='danger'))

        # Validate positions: must be 1..4 and unique
        positions = [p1, p2, p3, p4]
        if any(p < 1 or p > 4 for p in positions):
            return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Positions must be between 1 and 4.', cat='danger'))
        if len(set(positions)) != 4:
            return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Positions must be unique for each player.', cat='danger'))
        score1 = POSITION_POINTS.get(p1, 0)
        score2 = POSITION_POINTS.get(p2, 0)
        score3 = POSITION_POINTS.get(p3, 0)
        score4 = POSITION_POINTS.get(p4, 0)

        match.score1 = score1
        match.score2 = score2
        match.score3 = score3
        match.score4 = score4

        # Winner is position 1 (highest points by mapping)
        match.winner_id = match.player1_id if p1 == 1 else (
            match.player2_id if p2 == 1 else (
                match.player3_id if p3 == 1 else (
                    match.player4_id if p4 == 1 else None)))
    else:
        # Backward-compatible: read direct 1-10 scores
        try:
            score1 = int(request.form['score1'])
            score2 = int(request.form['score2'])
            score3 = int(request.form['score3'])
            score4 = int(request.form['score4'])
        except (ValueError, KeyError):
            return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Scores must be integers between 1 and 10.', cat='danger'))

        # Validate scores range and uniqueness
        scores_list = [score1, score2, score3, score4]
        if any(s < 1 or s > 10 for s in scores_list):
            return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Scores must be between 1 and 10.', cat='danger'))
        if len(set(scores_list)) != 4:
            return redirect(url_for('tournament_detail', tournament_id=tournament_id, msg='Scores must be unique for each player.', cat='danger'))

        match.score1 = score1
        match.score2 = score2
        match.score3 = score3
        match.score4 = score4

        # Determine winner (highest score)
        scores = [(score1, match.player1_id), (score2, match.player2_id),
                  (score3, match.player3_id), (score4, match.player4_id)]
        max_score = max(scores, key=lambda x: x[0])
        match.winner_id = max_score[1]

    db.session.commit()

    # If this match is the finals (top 4 humans), auto-complete and go to results
    tournament = Tournament.query.get_or_404(tournament_id)
    players = filter_humans(Player.query.filter_by(tournament_id=tournament_id).all())
    matches = Match.query.filter_by(tournament_id=tournament_id).all()
    totals = totals_for_player_ids(matches, {p.id for p in players})
    top4_ids = [pid for pid, _ in sorted(totals.items(), key=lambda x: x[1], reverse=True)[:4]]
    if len(top4_ids) == 4:
        final_set = set([match.player1_id, match.player2_id, match.player3_id, match.player4_id])
        if set(top4_ids) == final_set:
            tournament.status = 'completed'
            db.session.commit()
            return redirect(url_for('tournament_results', tournament_id=tournament_id))

    # Don't automatically create next round - let user decide when to create new matches
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))
