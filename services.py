from typing import List, Tuple, Dict, Optional, Set
from app import db
from models import Player, Match
from constants import BOT_PREFIX
from sqlalchemy import or_
import random


def ensure_bots(tournament_id: int, min_count: int = 4) -> List[Player]:
    bots = Player.query.filter(Player.tournament_id == tournament_id, Player.name.like(f"{BOT_PREFIX}%")).all()
    needed = max(0, min_count - len(bots))
    if needed:
        start_idx = len(bots) + 1
        for i in range(needed):
            bot = Player(name=f"{BOT_PREFIX} {start_idx + i}", tournament_id=tournament_id)
            db.session.add(bot)
        db.session.commit()
        bots = Player.query.filter(Player.tournament_id == tournament_id, Player.name.like(f"{BOT_PREFIX}%")).all()
    return bots


def human_distribution(total_appearances: int) -> List[int]:
    """Return a list of human counts per match that minimizes matches, prefers 3-human games,
    and never creates a 1-human match. Converts (4,2) -> (3,3)."""
    if total_appearances < 2:
        return []
    f = total_appearances // 4
    rem = total_appearances % 4
    counts = [4] * f
    if rem == 1 and f >= 1:
        counts.pop()
        counts.extend([3, 2])
    elif rem == 2:
        counts.append(2)
    elif rem == 3:
        counts.append(3)
    counts.sort()
    while 2 in counts and 4 in counts:
        counts.remove(2)
        counts.remove(4)
        counts.extend([3, 3])
    return counts


def take_distinct(pool: List[int], k: int) -> List[int]:
    """Pop up to k distinct player IDs from pool (in-place)."""
    group = []
    i = 0
    while i < len(pool) and len(group) < k:
        pid = pool[i]
        if pid not in group:
            group.append(pid)
            pool.pop(i)
        else:
            i += 1
    return group


def player_in_any_match(player_id: int) -> bool:
    return Match.query.filter(
        or_(
            Match.player1_id == player_id,
            Match.player2_id == player_id,
            Match.player3_id == player_id,
            Match.player4_id == player_id,
        )
    ).first() is not None


def is_bot_name(name: str) -> bool:
    return name.startswith(BOT_PREFIX)


def is_bot_player(player: Player) -> bool:
    return is_bot_name(player.name)


def filter_humans(players: List[Player]) -> List[Player]:
    return [p for p in players if not is_bot_player(p)]


def totals_for_player_ids(matches: List[Match], player_ids: Set[int]) -> Dict[int, int]:
    totals: Dict[int, int] = {pid: 0 for pid in player_ids}
    for m in matches:
        for pid, score in (
            (m.player1_id, m.score1),
            (m.player2_id, m.score2),
            (m.player3_id, m.score3),
            (m.player4_id, m.score4),
        ):
            if score is not None and pid in totals:
                totals[pid] += score
    return totals


def top_n_players_by_totals(players: List[Player], matches: List[Match], n: int) -> List[Player]:
    ids = {p.id for p in players}
    totals = totals_for_player_ids(matches, ids)
    return sorted(players, key=lambda p: totals.get(p.id, 0), reverse=True)[:n]


def find_match_with_exact_players(matches: List[Match], player_set: Set[int]) -> Optional[Match]:
    for m in matches:
        if {m.player1_id, m.player2_id, m.player3_id, m.player4_id} == player_set:
            return m
    return None


def compute_player_statistics(players: List[Player], matches: List[Match]) -> List[Dict]:
    stats = []
    for player in players:
        player_matches = [m for m in matches if player.id in {m.player1_id, m.player2_id, m.player3_id, m.player4_id}]
        total_score = 0
        wins = 0
        for m in player_matches:
            if m.player1_id == player.id and m.score1 is not None:
                total_score += m.score1
                if m.winner_id == player.id:
                    wins += 1
            elif m.player2_id == player.id and m.score2 is not None:
                total_score += m.score2
                if m.winner_id == player.id:
                    wins += 1
            elif m.player3_id == player.id and m.score3 is not None:
                total_score += m.score3
                if m.winner_id == player.id:
                    wins += 1
            elif m.player4_id == player.id and m.score4 is not None:
                total_score += m.score4
                if m.winner_id == player.id:
                    wins += 1
        matches_played = len(player_matches)
        avg_score = total_score / matches_played if matches_played > 0 else 0
        stats.append({
            'player': player,
            'matches_played': matches_played,
            'wins': wins,
            'total_score': total_score,
            'avg_score': avg_score,
            'win_rate': wins / matches_played if matches_played > 0 else 0
        })
    stats.sort(key=lambda x: (x['total_score'], x['wins'], x['avg_score']), reverse=True)
    return stats

