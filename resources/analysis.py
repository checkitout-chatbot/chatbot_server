from flask import render_template, make_response
from flask_restful import Resource, reqparse
from models.user import UserModel
from models.book_list import BookListModel
from resources.user import UserRegister
import log
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np


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
        유저가 읽은 책을 그래프로 나타내고 등수 표시
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
        book_list.drop(['review', 'rate', 'created_dt',
                       'modified_dt'], inplace=True, axis=1)

        cnt_status = book_list['user_id'].value_counts()
        users = cnt_status.index.tolist()
        values = cnt_status.tolist()
        avg = int(sum(values) / len(values))
        me_value = values[users.index(user_id)]

        rank = values.index(values[users.index(user_id)]) + 1

        n_values = []
        n_values.append(me_value)
        n_values.append(avg)
        n_values.append(max(values))
        print(n_values)

        x = np.arange(len(n_values))
        labels = ["나는 요기", "평균 유저", "1등 유저"]

        # 한글 글꼴 설정
        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
        #  font = fm.FontProperties(fname=font_path).get_name()
        #  plt.rc('font', family=font)
        fontprop = fm.FontProperties(fname=font_path)

        # 막대 색 설정
        bar_colors = ['#edc5d2', '#e3a58f', '#79b05f']

        #  plt.axhline(avg, 0, len(n_values), color='red',
        #              linestyle='--', linewidth=2)

        bar = plt.bar(x, n_values, align='center', tick_label=labels,
                      width=0.4, color=bar_colors)
        plt.xticks(fontproperties=fontprop)

        # 막대 높이 가져오기
        height0 = bar[0].get_height()
        height1 = bar[1].get_height()
        height2 = bar[2].get_height()

        # 막대마다 권수 표시
        plt.text(0, height0, f'{me_value}권', ha='center',
                 va='bottom', color='gray', fontproperties=fontprop)
        plt.text(1, height1, f'{avg}권', ha='center',
                 va='bottom', color='gray', fontproperties=fontprop)
        plt.text(2, height2, f'{max(values)}권', ha='center',
                 va='bottom', color='gray', fontproperties=fontprop)

        plt.title('읽은 책 랭킹', fontproperties=fontprop)
        #  plt.ylabel('읽은 책 권수', fontproperties=fontprop)

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
