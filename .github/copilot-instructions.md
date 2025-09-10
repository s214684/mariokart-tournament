# Mario Kart Tournament - AI Agent Instructions

## 🏗️ Architecture Overview

**Flask MVC Structure**: Routes handle business logic, models define data relationships, templates render UI. Core files:
- `routes.py`: All tournament logic, matchmaking algorithms, statistics calculations
- `models.py`: SQLAlchemy models with tournament/player/match relationships
- `app.py`: Minimal Flask setup with database initialization

## 🎯 Critical Patterns

### Tournament Flow Control
- **Manual Match Creation**: Use `generate_bracket` endpoint to create matches, never auto-generate
- **Status Tracking**: Tournament status ('active'/'completed') controls UI behavior
- **Round System**: Each match belongs to a round, displayed in tournament_detail.html

### Matchmaking Algorithm (`routes.py:generate_bracket`)
```python
# Performance-based sorting for balanced groups
player_stats = calculate_player_statistics(existing_matches)
sorted_players = sorted(player_stats.values(), key=lambda x: (x['total_score'], x['wins'], x['avg_score']), reverse=True)

# Championship rounds: best vs best, worst vs worst
if next_round > 1 and len(sorted_players) >= 8:
    top_players = sorted_players[:4]
    bottom_players = sorted_players[-4:]
```

### Scoring & Winner Determination
- **1-10 Scale**: All scores must be integers 1-10
- **Auto-Winner**: Highest score wins automatically (no ties handled)
- **Statistics Tracking**: Recalculated in `tournament_results()` for rankings

## 🔧 Development Workflow

### Database Schema Changes
```bash
# Delete existing database to recreate with new schema
rm instance/mariokart_tournament.db
python app.py  # Recreates tables automatically
```

### Virtual Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Testing Tournament Logic
- Use `test_formats.py` for algorithm validation
- Test with different player counts (4, 8, 16+) to verify matchmaking
- Verify statistics calculations match manual expectations

## 🎨 UI Conventions

### Match Display Pattern (`tournament_detail.html`)
- **Card Layout**: Each match in Bootstrap card with player grid (2x2)
- **Score Badges**: Blue badges for recorded scores, winner alerts in green
- **Status Indicators**: Different styling for active/completed tournaments

### Bootstrap 5 Patterns
- **Grid System**: 4-column player cards, 6-column match cards
- **Color Coding**: Primary=blue (active), Success=green (completed), Info=blue (scores)
- **Responsive**: Mobile-first design with col-md-* breakpoints

## 📊 Data Relationships

### Player Statistics Calculation
```python
# Pattern used in multiple functions
for player in players:
    player_matches = [m for m in matches if player_in_match(player, m)]
    total_score = sum(player_score_in_match(player, m) for m in player_matches)
    wins = sum(1 for m in player_matches if m.winner_id == player.id)
    avg_score = total_score / len(player_matches) if player_matches else 0
```

### Foreign Key Navigation
- `tournament.players` → all players in tournament
- `tournament.matches` → all matches in tournament
- `match.player1/player2/player3/player4` → player objects
- `match.winner` → winning player object

## 🚨 Common Pitfalls

- **Don't auto-create matches**: Always require manual `generate_bracket` calls
- **Validate player count**: Minimum 4 players before match creation
- **Handle incomplete matches**: Some matches may lack scores/winners
- **Database recreation**: Required for any model changes (no migrations)
- **Score validation**: Must be 1-10 integers, no floats or nulls in winner determination

## 📈 Key Functions to Understand

- `generate_bracket()`: Complex matchmaking with performance balancing
- `tournament_results()`: Statistics calculation and ranking logic
- `record_result()`: Score validation and winner determination
- Tournament status transitions in `end_tournament()`

## 🔍 Debugging Commands

```bash
# View database contents
sqlite3 instance/mariokart_tournament.db ".tables"
sqlite3 instance/mariokart_tournament.db "SELECT * FROM tournament;"

# Check player statistics
sqlite3 instance/mariokart_tournament.db "SELECT name, COUNT(*) as matches FROM player p JOIN match m ON p.id IN (m.player1_id, m.player2_id, m.player3_id, m.player4_id) GROUP BY p.id;"
```</content>
<parameter name="filePath">/Users/oliver/Desktop/mariokart-tournament/.github/copilot-instructions.md
