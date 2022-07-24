from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.book import Book
from resources.book_list import BookList
from resources.recommend import Today, Similar, Sense, Social
from resources.search import Barcode, Keyword
from resources.edit_list import SaveWanted, SaveReview

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://chatbot:checkitOut-2022@chatbotdb.c3hrvk4wz2vi.ap-northeast-2.rds.amazonaws.com:3306/test_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'jun'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWT(app, authenticate, identity)  # /auth

api.add_resource(UserRegister, '/register')
api.add_resource(Book, '/book/<string:isbn>')

# 책 추천 방식
# today, similar, sense(알잘딱깔센), social
api.add_resource(Today, '/recommend/today')
api.add_resource(Similar, '/recommend/similar')
api.add_resource(Sense, '/recommend/sense')
api.add_resource(Social, '/recommend/social')

# 저장한 책 리스트 확인
# 0: 읽고 싶은 책 1: 읽은 책
api.add_resource(BookList, '/booklist/<string:status>')

# 책 리스트 저장
api.add_resource(SaveWanted, '/save/0')
api.add_resource(SaveReview, '/save/1')

# 책 검색
api.add_resource(Keyword, '/search/keyword')
api.add_resource(Barcode, '/search/barcode')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
