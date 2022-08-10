from db import db


class UserSimilarModel(db.Model):
    __tablename__ = 'user_similar'

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey(
        'books.id'), primary_key=True)

    def __init__(self, user_id, book_id):
        self.user_id = user_id
        self.book_id = book_id

    def json(self):
        return {'user_id': self.user_id, 'book_id': self.book_id}

    @classmethod
    def find_by_user(cls, user_id):
        """
        해당 유저에게 추천할 책 전부 가져오기
        """
        return cls.query.filter_by(user_id=user_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
