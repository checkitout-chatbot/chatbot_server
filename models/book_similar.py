from db import db


class BookSimilarModel(db.Model):
    __tablename__ = 'book_similar'

    book_id = db.Column(db.Integer, db.ForeignKey(
        'books.id'), primary_key=True)
    book_similar_id = db.Column(db.Integer, db.ForeignKey(
        'books.id'), primary_key=True)

    def __init__(self, book_id, book_similar_id):
        self.book_id = book_id
        self.book_similar_id = book_similar_id

    def json(self):
        return {'book_id': self.book_id, 'book_similar_id': self.book_similar_id}

    @classmethod
    def find_by_book_id(cls, book_id):
        """
        book id를 입력하면 해당 책과 유사한 책 전부 가져오기
        """
        return cls.query.filter_by(book_id=book_id).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
