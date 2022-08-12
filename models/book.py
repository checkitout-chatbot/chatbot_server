from db import db

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

    isbn = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(80))
    author = db.Column(db.String(80))
    publisher = db.Column(db.String(80))
    summary = db.Column(db.String(255))
    img = db.Column(db.String(255))
    genre = db.Column(db.String(80))
    rate = db.Column(db.Float(precision=1))
    bestseller = db.Column(db.Integer)
    similarity = db.Column(db.String(255))
    pubDate = db.Column(db.Date)

    book_list = db.relationship('BookListModel', lazy='dynamic')

    def __init__(self, isbn, title, author, publisher, summary, img, genre, rate, bestseller, similarity, pubDate):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publisher = publisher
        self.summary = summary
        self.img = img
        self.genre = genre
        self.rate = rate
        self.bestseller = bestseller
        self.similarity = similarity
        self.pubDate = pubDate

    def json(self):
        return {'isbn': self.isbn, 'title': self.title, 'author': self.author,
                'publisher': self.publisher, 'summary': self.summary,
                'img': self.img, 'genre': self.genre, 'rate': self.rate,
                'bestseller': self.bestseller, 'similarity': self.similarity, 'pubDate': self.pubDate}

    @classmethod
    def find_by_isbn(cls, isbn):
        return cls.query.filter_by(isbn=isbn).first()

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()

    @classmethod
    def find_by_author(cls, author):
        return cls.query.filter_by(author=author).first()

    @classmethod
    def find_by_genre(cls, genre):
        return cls.query.filter_by(genre=genre).first()

    @classmethod
    def find_by_SenseCategory(cls, sense):
        return cls.query.filter_by(sense=sense).first()

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

