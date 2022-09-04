from flask import render_template, make_response
from flask_restful import Resource, reqparse
from models.user import UserModel
from models.book_list import BookListModel
from resources.user import UserRegister
import log
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time


class CreateGraph(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userRequest', type=dict)

    def get(self):
        """
        graph 이미지 rendering
        """
        return make_response(render_template('graph.html'))

    def post(self):
        """
        읽고 싶은 책 리스트 출력
        """
        data = CreateGraph.parser.parse_args()
        log.info_log(data)

        # 신규유저면 DB에 저장
        username = data['userRequest']['user']['id']
        UserRegister.check_id(username=username)
        user_id = UserModel.find_by_username(username).json()['id']

        books = BookListModel.find_by_status(1)

        book_list = pd.DataFrame()
        for book in books:
            n_book_list = pd.DataFrame.from_dict([book.json()])
            book_list = pd.concat(
                [book_list, n_book_list], ignore_index=True)
        print(book_list.head())
        book_list.drop(['review', 'rate', 'created_dt',
                       'modified_dt'], inplace=True, axis=1)

        cnt_status = book_list['user_id'].value_counts()
        users = cnt_status.index.tolist()
        values = cnt_status.tolist()
        avg = int(sum(values) / len(values))
        me_values = values[users.index(user_id)]

        rank = values.index(values[users.index(user_id)]) + 1

        n_values = []
        n_values.append(me_values)
        n_values.append(avg)
        n_values.append(max(values))
        print(n_values)

        x = np.arange(len(n_values))
        labels = ["me", "average", "maximum" ]
        print(labels)

        bar_colors = ['#edc5d2', '#e3a58f', '#79b05f']

        plt.axhline(avg, 0, len(n_values), color='red',
                    linestyle='--', linewidth=2)
        plt.text(n_values.index(me_values),
                 me_values+1, f'Me ⬇️️ {me_values}books', color='blue')
        plt.bar(x, n_values, align='center',
                tick_label=labels, width=0.4, color=bar_colors)
        plt.title('rank')
        plt.ylabel('Number of Books')

        plt.savefig('static/images/graph.png')
        

        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleImage": {
                            "imageUrl": "http://43.200.157.176/static/images/graph.png",
                            "altText": "분석 그래프"
                        }
                    },
                    {
                        "simpleText": {
                            "text": f"현재 {rank}등 입니다!😆."
                        }
                    }
                ]
            }
        }

        return response
