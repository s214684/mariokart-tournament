from flask import render_template, request, redirect, url_for
from app import app, db
from models import Tournament, Player, Match
import math

@app.route('/')
def index():
    tournaments = Tournament.query.all()
    return render_template('index.html', tournaments=tournaments)

@app.route('/create_tournament', methods=['POST'])
def create_tournament():
    name = request.form['name']
    tournament = Tournament(name=name)
    db.session.add(tournament)
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament.id))

@app.route('/tournament/<int:tournament_id>')
def tournament_detail(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = Player.query.filter_by(tournament_id=tournament_id).all()
    matches = Match.query.filter_by(tournament_id=tournament_id).order_by(Match.round).all()
    return render_template('tournament_detail.html', tournament=tournament, players=players, matches=matches)

@app.route('/tournament/<int:tournament_id>/add_player', methods=['POST'])
def add_player(tournament_id):
    name = request.form['name']
    player = Player(name=name, tournament_id=tournament_id)
    db.session.add(player)
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>/generate_bracket')
def generate_bracket(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = Player.query.filter_by(tournament_id=tournament_id).all()
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
        import random
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

@app.route('/tournament/<int:tournament_id>/end_tournament')
def end_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    tournament.status = 'completed'
    db.session.commit()
    return redirect(url_for('tournament_results', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>/results')
def tournament_results(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    players = Player.query.filter_by(tournament_id=tournament_id).all()
    matches = Match.query.filter_by(tournament_id=tournament_id).all()

    # Calculate player statistics
    player_stats = []
    for player in players:
        player_matches = [m for m in matches if m.player1_id == player.id or m.player2_id == player.id or
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

        player_stats.append({
            'player': player,
            'matches_played': matches_played,
            'wins': wins,
            'total_score': total_score,
            'avg_score': avg_score,
            'win_rate': wins / matches_played if matches_played > 0 else 0
        })

    # Sort by total score, then by wins, then by average score
    player_stats.sort(key=lambda x: (x['total_score'], x['wins'], x['avg_score']), reverse=True)

    return render_template('tournament_results.html', tournament=tournament,
                         player_stats=player_stats, matches=matches)

@app.route('/tournament/<int:tournament_id>/record_result/<int:match_id>', methods=['POST'])
def record_result(tournament_id, match_id):
    match = Match.query.get_or_404(match_id)

    # Get scores from form
    score1 = int(request.form['score1'])
    score2 = int(request.form['score2'])
    score3 = int(request.form['score3'])
    score4 = int(request.form['score4'])

    # Update match with scores
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

    # Don't automatically create next round - let user decide when to create new matches

    return redirect(url_for('tournament_detail', tournament_id=tournament_id))
