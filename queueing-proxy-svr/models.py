from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    status = db.Column(db.String(20)) # queued, separating, transcribing, done
    original_file_path = db.Column(db.String(200))
    vocals_file_path = db.Column(db.String(200))
    instrumental_file_path = db.Column(db.String(200))
    lyrics_json = db.Column(db.JSON)
    lyrics_text = db.Column(db.Text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    # lastname = db.Column(db.String(100))
    # firstname = db.Column(db.String(100))
    