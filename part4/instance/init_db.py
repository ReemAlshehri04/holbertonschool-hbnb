from app import create_app, db
import os

app = create_app()

with app.app_context():
    
    print("Database path:", app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()
    print("Tables created successfully!")