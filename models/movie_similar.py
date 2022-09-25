from db import db


class MovieSimilarModel(db.Model):
    __tablename__ = 'movie_similar'

    movie_id = db.Column(db.Integer, db.ForeignKey(
        'movies.id'), primary_key=True)
    movie_similar_id = db.Column(db.Integer, db.ForeignKey(
        'movies.id'), primary_key=True)

    def __init__(self, movie_id, movie_similar_id):
        self.movie_id = movie_id
        self.movie_similar_id = movie_similar_id

    def json(self):
        return {'movie_id': self.movie_id, 'movie_similar_id': self.movie_similar_id}

    @classmethod
    def find_by_movie_id(cls, movie_id):
        """
        movie id를 입력하면 해당 책과 유사한 책 전부 가져오기
        """
        return cls.query.filter_by(movie_id=movie_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
