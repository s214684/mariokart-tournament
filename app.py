from flask import Flask
import os
from models import db
from validators import alert_category

app = Flask(__name__)

# Allow config via environment variables for production/Docker
db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///mariokart_tournament.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', os.path.join('static', 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', str(4 * 1024 * 1024)))  # 4MB default

# Ensure folders exist (uploads and SQLite directory if used)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if db_uri.startswith('sqlite:///'):
    db_path = db_uri.replace('sqlite:///', '')
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

# Jinja helpers
@app.context_processor
def inject_helpers():
    return dict(alert_cat=lambda v: alert_category(v))

db.init_app(app)

with app.app_context():
    db.create_all()

# Import routes after app is created to avoid circular imports
from routes import *

if __name__ == '__main__':
    app.run(debug=True)
