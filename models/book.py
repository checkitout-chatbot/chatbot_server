#모듈 에러 보완
if __name__ == '__main__':
	if __package__ is None:
		import sys
		from os import path
		print(path.dirname( path.dirname( path.abspath(__file__) ) ))
		sys.path.append(path.dirname( path.dirname( path.abspath(__file__) ) ))
		from db import db
	else:
		from ..db import db


class BookModel(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True)
    title = db.Column(db.String(80))
    author = db.Column(db.String(80))
    publisher = db.Column(db.String(80))
    pubDate = db.Column(db.Date)
    summary = db.Column(db.String(255))
    img = db.Column(db.String(255))
    genre = db.Column(db.String(80))
    rate = db.Column(db.Float(precision=1))
    bestseller = db.Column(db.Integer)

    def __init__(self, isbn, title=None, author=None, publisher=None, pubDate=None, summary=None, img=None, genre=None, rate=None, bestseller=None):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publisher = publisher
        self.pubDate = pubDate
        self.summary = summary
        self.img = img
        self.genre = genre
        self.rate = rate
        self.bestseller = bestseller

    def json(self):
        return {'id': self.id, 'isbn': self.isbn, 'title': self.title, 'author': self.author,
                'publisher': self.publisher, 'pubDate': self.pubDate, 'summary': self.summary,
                'img': self.img, 'genre': self.genre, 'rate': self.rate,
                'bestseller': self.bestseller}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_isbn(cls, isbn):
        return cls.query.filter_by(isbn=isbn).first()

    @classmethod
    def find_by_genre(cls, genre):
        return cls.query.filter_by(genre=genre).first()

    @classmethod
    def find_by_bestseller(cls):
        return cls.query.filter_by(bestseller=1).all()

    @classmethod
    def find_by_keyword(cls, keyword):
        keyword = f'%{keyword}%'
        return cls.query.filter((BookModel.title.like(keyword)) | (BookModel.author.like(keyword)) | (BookModel.summary.like(keyword))).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


# if __name__ == '__main__':
#     book = BookModel.find_by_keyword('정의란')
#     print(book)

if __name__ == '__main__':
    book = BookModel.find_by_SenseCategory('love')
    print(book)

