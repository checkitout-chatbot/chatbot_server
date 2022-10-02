from db import db


class MusicModel(db.Model):
    __tablename__ = 'musics'

    id = db.Column(db.Integer, primary_key=True)
    melon_music_code = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(80))
    singer = db.Column(db.String(80))
    genre = db.Column(db.String(80))
    lyric = db.Column(db.String(255))

    def __init__(self, id, melon_music_code=None, title=None, singer=None, genre=None, lyric=None):
        self.id = id
        self.melon_music_code = melon_music_code
        self.title = title
        self.singer = singer
        self.genre = genre
        self.lyric = lyric

    def json(self):
        return {'id': self.id, 'melon_music_code': self.melon_music_code, 'title': self.title,
                'singer': self.singer, 'genre': self.genre, 'lyric': self.lyric}

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_melon_music_code(cls, melon_music_code):
        return cls.query.filter_by(melon_music_code=melon_music_code).first()

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
