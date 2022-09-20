from db import db


class BookListModel(db.Model):
    __tablename__ = 'book_list'

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey(
        'books.id'), primary_key=True)
    status = db.Column(db.Integer)
    review = db.Column(db.String(255))
    rate = db.Column(db.Float(precision=1))
    created_dt = db.Column(db.DateTime)
    modified_dt = db.Column(db.DateTime)

    def __init__(self, user_id, book_id, status, review=None, rate=None, created_dt=None, modified_dt=None):
        self.user_id = user_id
        self.book_id = book_id
        self.status = status
        self.review = review
        self.rate = rate
        self.created_dt = created_dt
        self.modified_dt = modified_dt

    def json(self):
        return {'user_id': self.user_id, 'book_id': self.book_id, 'status': self.status,
                'review': self.review, 'rate': self.rate, 'created_dt': self.created_dt, 'modified_dt': self.modified_dt}

    @classmethod
    def find_by_user_status(cls, user_id, status):
        """
        user_id에 해당하고 status를 변수로 받아서 해당 상태의 책 전부 찾기
        """
        return cls.query.filter_by(user_id=user_id, status=status).all()

    @classmethod
    def find_by_user(cls, user_id):
        """
        user_id에 해당하고 status를 변수로 받아서 해당 상태의 책 전부 찾기
        """
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_by_status_isbn(cls, user_id, book_id, status):
        return cls.query.filter_by(user_id=user_id, book_id=book_id, status=status).first()

    @classmethod
    def find_by_user_book(cls, user_id, book_id):
        return cls.query.filter_by(user_id=user_id, book_id=book_id).first()

    @classmethod
    def find_by_status(cls, status):
        """
        입력받은 status의 책 전부 가져오기
        """
        return cls.query.filter_by(status=status).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
