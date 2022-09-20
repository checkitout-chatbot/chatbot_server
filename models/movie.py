#  from turtle import st
from db import db


class MovieModel(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    openYear = db.Column(db.Integer)
    n_code = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    genre = db.Column(db.String(80))
    nation = db.Column(db.String(80))
    runningTime = db.Column(db.String(80))
    age = db.Column(db.String(80))
    openDate = db.Column(db.String(50))
    rate = db.Column(db.String(50))
    participate = db.Column(db.String(50))
    directors = db.Column(db.String(80))
    actors = db.Column(db.String(80))
    story = db.Column(db.String(255))
    blank = db.Column(db.String(50))
    img = db.Column(db.String(255))

    def __init__(self, id, n_code, openYear=None, title=None, genre=None, nation=None, runningTime=None, age=None, openDate=None, rate=None, participate=None, directors=None, actors=None, story=None, blank=None, img=None):
        self.id = id
        self.openYear = openYear
        self.n_code = n_code
        self.title = title
        self.genre = genre
        self.nation = nation
        self.runningTime = runningTime
        self.age = age
        self.openDate = openDate
        self.rate = rate
        self.participate = participate
        self.directors = directors
        self.actors = actors
        self.story = story
        self.blank = blank
        self.img = img

    def json(self):
        return {'id': self.id, 'openYear': self.openYear, 'n_code': self.n_code, 'title': self.title,
                'genre': self.genre, 'nation': self.nation, 'runningTime': self.runningTime,
                'age': self.age, 'openDate': self.openDate, 'rate': self.rate,
                'participate': self.participate, 'directors': self.directors, 'actors': self.actors, 'story': self.story, 'blank': self.blank, 'img': self.img}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_n_code(cls, n_code):
        return cls.query.filter_by(n_code=n_code).first()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


# if __name__ == '__main__':
#     book = BookModel.find_by_keyword('정의란')
#     print(book)
