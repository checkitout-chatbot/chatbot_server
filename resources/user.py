from flask_restful import Resource, reqparse
from models.user import UserModel
import log
from datetime import datetime


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="user id 입력은 필수입니다."
                        )

    @classmethod
    def check_id(cls, username):
        """
        username으로 등록된 유저 찾아서 없으면 저장
        """
        now = datetime.now()
        checking = UserModel.find_by_username(username=username)
        if checking == None:
            user = UserModel(username=username,
                             password=username, created_dt=now.date())
            user.save_to_db()
            log.info_log('User가 성공적으로 등록되었습니다.')
