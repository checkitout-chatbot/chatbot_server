from db import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(2))
    interest = db.Column(db.String(255))
    name = db.Column(db.String(255))
    created_dt = db.Column(db.Date)

    def __init__(self, username, password, age=None, sex=None, interest=None, name=None, created_dt=None):
        self.username = username
        self.password = password
        self.age = age
        self.sex = sex
        self.interest = interest
        self.name = name
        self.created_dt = created_dt

    def json(self):
        return {'id': self.id, 'username': self.username, 'age': self.age, 'sex': self.sex, 'interest': self.interest, 'name': self.name}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
