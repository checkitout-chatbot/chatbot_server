from flask_restful import Resource, reqparse
from models.user import UserModel
import logging

logging.basicConfig(level=logging.INFO)


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="user id 입력은 필수입니다."
                        )

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "해당 user id는 이미 존재합니다."}, 400

        user = UserModel(data['username'], data['username'])
        user.save_to_db()

        return {"message": "User가 성공적으로 등록되었습니다."}, 201

    def check_id(self, user_id):
        checking = UserModel.find_by_username(user_id)
        if checking == None:
            user = UserModel(user_id, user_id)
            user.save_to_db()
            logging.info(f"USER {user_id}를 저장했습니다.")
