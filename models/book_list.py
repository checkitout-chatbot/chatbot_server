from enum import unique
from db import db


class BookListModel(db.Model):
    __tablename__ = 'book_list'

    isbn = db.Column(db.String(13), db.ForeignKey('books.isbn'), primary_key=True)
    username = db.Column(db.String(255), db.ForeignKey('users.username'), primary_key=True)
    status = db.Column(db.Integer)
    review = db.Column(db.String(255))
    rate = db.Column(db.Float(precision=1))

    # book = db.relationship('BookModel')
    # user = db.relationship('UserModel')

    def __init__(self, isbn, username, status, review, rate):
        self.isbn = isbn
        self.username = username
        self.status = status
        self.review = review
        self.rate = rate

    def json(self):
        return {'isbn': self.isbn, 'username': self.username, 'status': self.status, 
        'review': self.review, 'rate': self.rate}

    # 해당 유저의 책 리스트 중 상태가 status인 책 전부 찾기
    @classmethod
    def find_by_status(cls, username, status):
        return cls.query.filter_by(username=username, status=status).all()

    @classmethod
    def find_by_book(cls, isbn, username):
        return cls.query.filter_by(isbn=isbn, username=username).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
