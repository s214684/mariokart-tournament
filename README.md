# Mario Kart Tournament Manager

A Flask-based web application for managing Mario Kart tournaments with single-elimination brackets.

## Features

- **Tournament Management**: Create and manage multiple tournaments with status tracking
- **Flexible Player Participation**: Multiple players can participate in tournaments, but only 4 play per match
- **4-Player Matches**: Each match features exactly 4 players competing simultaneously
- **Scoring System**: Players score 1-10 points per match (10 being highest)
- **Multiple Match Support**: Create multiple matches/rounds within a single tournament
- **Manual Tournament Control**: Manually create new matches and end tournaments when desired
- **Automatic Winner Determination**: Player with highest score advances automatically
- **Match Tracking**: Record match scores and view complete tournament history
- **Responsive UI**: Clean, Bootstrap-styled interface with enhanced visual design
- **SQLite Database**: Lightweight, file-based database for easy deployment

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, Bootstrap 5
- **Deployment**: Local development server

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Setup

1. **Clone the repository** (if applicable):

   ```bash
   git clone https://github.com/s214684/mariokart-tournament.git
   cd mariokart-tournament
   ```

2. **Create and activate virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   python app.py
   ```

5. **Access the application**:
   Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

### Creating a Tournament

1. Navigate to the homepage
2. Enter a tournament name in the "Create New Tournament" form
3. Click "Create" to add the tournament

### Managing Players

1. Click on a tournament name to view its details
2. Use the "Add Player" form to register as many players as you want
3. Once you have at least 4 players, you can start creating matches

### Creating Matches

1. On the tournament detail page, click "Create New Match"
2. The system uses a fair matchmaking algorithm to create balanced groups:
   - Players are mixed by skill level to ensure competitive matches
   - Championship rounds feature best vs best and worst vs worst matchups
   - Everyone gets roughly equal playing opportunities
3. You can create multiple matches/rounds as needed

### Recording Results

1. On the tournament detail page, you'll see all created matches
2. Each match displays 4 players in a visually appealing card layout
3. For each match, enter scores (1-10) for all 4 players
4. Click "Record Scores" to save and automatically determine the winner (highest score)
5. Create additional matches as needed for more rounds

### Viewing Standings

1. Click "View Current Standings" to see live tournament statistics
2. View player rankings, win rates, and performance metrics
3. Monitor tournament progress with real-time statistics

### Ending a Tournament

1. When you're ready to finish the tournament, click "End Tournament"
2. View the final results page with:
   - 1st, 2nd, and 3rd place podium display
   - Complete player rankings table
   - Tournament summary statistics
   - Individual player performance metrics

## Project Structure

```text
mariokart-tournament/
├── app.py                 # Main Flask application
├── models.py              # Database models (Tournament, Player, Match)
├── routes.py              # Flask routes and business logic
├── requirements.txt       # Python dependencies
├── instance/
│   └── mariokart_tournament.db  # SQLite database file
├── templates/
│   ├── base.html          # Base HTML template
│   ├── index.html         # Homepage template
│   ├── tournament_detail.html  # Tournament detail template
│   └── tournament_results.html # Tournament results and rankings
├── static/                # Static files (CSS, JS, images)
└── README.md              # This file
```

## Database Schema

### Tournament

- `id`: Primary key
- `name`: Tournament name (string, max 100 chars)
- `created_at`: Creation timestamp
- `status`: Tournament status ('active', 'completed')

### Player

- `id`: Primary key
- `name`: Player name (string, max 100 chars)
- `tournament_id`: Foreign key to Tournament

### Match

- `id`: Primary key
- `round`: Round number (integer)
- `player1_id`: Foreign key to Player (required)
- `player2_id`: Foreign key to Player (required)
- `player3_id`: Foreign key to Player (required)
- `player4_id`: Foreign key to Player (required)
- `score1`: Score for player 1 (1-10, optional until recorded)
- `score2`: Score for player 2 (1-10, optional until recorded)
- `score3`: Score for player 3 (1-10, optional until recorded)
- `score4`: Score for player 4 (1-10, optional until recorded)
- `winner_id`: Foreign key to Player (determined by highest score)
- `tournament_id`: Foreign key to Tournament

## API Endpoints

- `GET /`: Homepage - list tournaments and create new
- `POST /create_tournament`: Create a new tournament
- `GET /tournament/<id>`: View tournament details
- `POST /tournament/<id>/add_player`: Add a player to tournament
- `GET /tournament/<id>/generate_bracket`: Create new matches for tournament
- `POST /tournament/<id>/record_result/<match_id>`: Record match result
- `GET /tournament/<id>/end_tournament`: End the tournament
- `GET /tournament/<id>/results`: View tournament results and rankings

## Development

### Running in Debug Mode

The application runs in debug mode by default. To disable:

```python
app.run(debug=False)
```

### Database Migrations

If you need to modify the database schema:

1. Update the models in `models.py`
2. Delete the existing database file: `instance/mariokart_tournament.db`
3. Restart the application to recreate the database

### Adding Features

- **Enhanced Bracket Visualization**: Integrate JavaScript libraries like jquery-bracket
- **User Authentication**: Add login system for tournament organizers
- **Real-time Updates**: Implement WebSockets for live tournament tracking
- **Statistics**: Add player win/loss tracking and tournament analytics

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Future Enhancements

- [ ] Integrate jquery-bracket for visual bracket display
- [ ] Add tournament types (double-elimination, round-robin)
- [ ] Implement user accounts and permissions
- [ ] Add tournament statistics and leaderboards
- [ ] Support for team-based tournaments
- [ ] Mobile app companion
- [ ] Real-time notifications for match updates
