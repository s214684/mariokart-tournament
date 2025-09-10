# Mario Kart Tournament Manager

A comprehensive Flask-based web application for managing Mario Kart tournaments with intelligent matchmaking, flexible tournament formats, and detailed statistics tracking.

## ✨ Features

- **🏆 Tournament Management**: Create and manage multiple tournaments with status tracking
- **👥 Flexible Player Participation**: Support for any number of players with 4-player matches
- **🎯 Intelligent Matchmaking**: Performance-based algorithm ensures fair and competitive groupings
- **📊 Advanced Scoring System**: Position-based 1–4 point scale with automatic winner determination
- **🔄 Multiple Round Support**: Create unlimited rounds with championship-style matchups
- **🎮 Tournament Formats**: Optimized formats for different player counts (4 to 33+ players)
- **📈 Live Statistics**: Real-time player rankings, win rates, and performance metrics
- **🎨 Responsive UI**: Modern Bootstrap 5 interface with intuitive match visualization
- **💾 SQLite Database**: Lightweight, file-based database for easy deployment

## 🏗️ Tournament Formats

The application supports multiple tournament formats optimized for different player counts:

### 🏆 Micro Tournament (4 Players)

- **Duration**: 15 minutes
- **Format**: Single 4-player match
- **Best for**: Quick games and testing

### 🏆 Small Tournament (5-8 Players)

- **Duration**: 45 minutes
- **Format**: Multiple rounds with balanced groupings
- **Best for**: Balanced competition with multiple rounds

### 🏆 Medium Tournament (9-16 Players)

- **Duration**: 2 hours
- **Format**: Pool play with elimination rounds
- **Best for**: Structured competition with pools

### 🏆 Large Tournament (17-32 Players)

- **Duration**: 4-8 hours
- **Format**: Qualification + group stage + playoffs
- **Best for**: Major events with multiple phases

### 🏆 Mega Tournament (33+ Players)

- **Duration**: 8+ hours
- **Format**: Multi-phase tournament with breaks
- **Best for**: Large-scale events

## 🛠️ Tech Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: SQLite (file-based, no server required)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Architecture**: MVC pattern with clean separation of concerns

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- pip package manager

### Installation

1. **Clone and navigate to the repository**:

   ```bash
   git clone https://github.com/s214684/mariokart-tournament.git
   cd mariokart-tournament
   ```

2. **Set up virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   python app.py
   ```

5. **Open your browser**:
   Navigate to `http://127.0.0.1:5000`

## 🎮 How to Use

### Creating Your First Tournament

1. **Start a Tournament**: Enter a tournament name and click "Create"
2. **Add Players**: Register as many players as you want (minimum 4 to start matches)
3. **Generate Matches**: Click "Create New Match" to use intelligent matchmaking
4. **Record Scores**: Enter 1-10 scores for each player in every match
5. **View Results**: Monitor live standings and final tournament rankings

### Intelligent Matchmaking

The system automatically creates balanced matches by:

- **Performance Tracking**: Analyzes player scores and win history
- **Skill Balancing**: Groups similar skill levels together
- **Fair Distribution**: Ensures everyone plays roughly the same number of matches
- **Championship Rounds**: Features best-vs-best matchups in later rounds

### Scoring

Matches use finishing positions (1–4), which are mapped to points on a 1–4 scale:

- 1st place → 4 points
- 2nd place → 3 points
- 3rd place → 2 points
- 4th place → 1 point

This mapping is configurable in `constants.py` (`POSITION_POINTS`). Bots are supported via planned matches but excluded from standings and finals.

### Tournament Management

- **Multiple Rounds**: Create unlimited rounds as needed
- **Live Statistics**: View real-time player rankings and performance metrics
- **Manual Control**: Decide when to create matches and end tournaments
- **Flexible Formats**: Adapt to different player counts automatically

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

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Homepage - list tournaments and create new |
| `POST` | `/create_tournament` | Create a new tournament |
| `GET` | `/tournament/<id>` | View tournament details and matches |
| `POST` | `/tournament/<id>/add_player` | Add a player to tournament |
| `GET` | `/tournament/<id>/generate_bracket` | Create new matches with intelligent matchmaking |
| `POST` | `/tournament/<id>/record_result/<match_id>` | Record match scores and determine winner |
| `GET` | `/tournament/<id>/end_tournament` | End tournament and show final results |
| `GET` | `/tournament/<id>/results` | View tournament results and rankings |

## 🗂️ Project Structure

```text
mariokart-tournament/
├── app.py                 # Main Flask application & database setup
├── models.py              # SQLAlchemy database models
├── routes.py              # Flask routes and tournament logic
├── requirements.txt       # Python dependencies
├── TOURNAMENT_PLAN.md     # Tournament format strategies
├── .github/
│   └── copilot-instructions.md  # AI agent guidelines
├── instance/
│   └── mariokart_tournament.db  # SQLite database
├── templates/
│   ├── base.html          # Base HTML template
│   ├── index.html         # Homepage
│   ├── tournament_detail.html  # Tournament management
│   └── tournament_results.html # Results and rankings
├── static/                # Static assets (CSS, JS, images)
└── README.md              # This file
```

## 🗃️ Database Schema

### Tournament Model

- `id`: Primary key
- `name`: Tournament name (max 100 chars)
- `created_at`: Creation timestamp
- `status`: 'active' or 'completed'

### Player Model

- `id`: Primary key
- `name`: Player name (max 100 chars)
- `tournament_id`: Foreign key to Tournament

### Match Model

- `id`: Primary key
- `round`: Round number
- `player1_id` through `player4_id`: Foreign keys to Players
- `score1` through `score4`: Points (1–4, nullable)
- `winner_id`: Foreign key to winning Player
- `tournament_id`: Foreign key to Tournament

## 🔧 Development

### Database Changes

For schema modifications:

```bash
# 1. Update models in models.py
# 2. Delete existing database
rm instance/mariokart_tournament.db
# 3. Restart application (auto-creates new schema)
python app.py
```

### Testing

```bash
# Run tournament format tests
python test_formats.py

# Manual testing with different player counts
# Create tournaments with 4, 8, 16, 32+ players
# Verify matchmaking and statistics calculations
```

### Code Quality

- **Linting**: Follow PEP 8 Python style guidelines
- **Error Handling**: Validate all user inputs and database operations
- **Security**: Sanitize user inputs to prevent injection attacks
- **Performance**: Optimize database queries for large tournaments

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

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork the repository**
2. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
4. **Test thoroughly** with different tournament sizes
5. **Commit your changes**:

   ```bash
   git commit -m "Add: brief description of your changes"
   ```

6. **Push to your branch**:

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

### Guidelines

- **Code Style**: Follow PEP 8 Python conventions
- **Testing**: Test with various player counts (4, 8, 16, 32+)
- **Documentation**: Update README for new features
- **Database**: Document any schema changes
- **UI/UX**: Ensure responsive design on mobile devices


### Planned Features

- [ ] **Real-time Updates**: WebSocket integration for live tournament tracking
- [ ] **User Authentication**: Login system for tournament organizers
- [ ] **Advanced Statistics**: Detailed analytics and performance insights
- [ ] **Tournament Templates**: Pre-configured formats for common scenarios
- [ ] **Mobile App**: Companion app for score recording
- [ ] **Bracket Visualization**: Interactive tournament bracket displays
- [ ] **Team Support**: Team-based tournament management
- [ ] **Export Features**: PDF reports and data export capabilities

- [ ] **API Enhancement**: RESTful API for external integrations
- [ ] **Database Optimization**: Query optimization for large tournaments
- [ ] **Caching**: Implement Redis for improved performance
- [ ] **Testing Suite**: Comprehensive unit and integration tests
- [ ] **CI/CD**: Automated testing and deployment pipeline

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Built with Flask and SQLAlchemy
- UI powered by Bootstrap 5
- Tournament format strategies inspired by competitive gaming best practices

---

**🎮 Ready to start your Mario Kart tournament?** Follow the Quick Start guide above and create your first tournament in minutes!
