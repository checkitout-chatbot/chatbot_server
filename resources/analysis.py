from flask import render_template, make_response
from flask_restful import Resource, reqparse
from models.user import UserModel
from models.book_list import BookListModel
from models.book import BookModel
from resources.user import UserRegister
from resources.response import Response, BlockID
from copy import deepcopy
import log
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os


class CreateGraph(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userRequest', type=dict)

    def get(self):
        """
        graph 이미지 rendering
        """
        imageList = os.listdir('static/images')
        imagelist = ['images/' + image for image in imageList]
        return make_response(render_template('graph.html', imagelist=imagelist))

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
        fontprop = fm.FontProperties(fname=font_path)

        # 막대 색 설정
        bar_colors = ['#edc5d2', '#e3a58f', '#79b05f']

        plt.axhline(avg, 0, len(n_values), color='red',
                    linestyle='--', linewidth=2)

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
        plt.ylabel('읽은 책 권수', fontproperties=fontprop)

        # 이미지 저장
        plt.savefig(f'static/images/graph_{user_id}.png')

        # 겹치는 책 추천
        cnt_status = book_list['book_id'].value_counts()
        books = cnt_status.index.tolist()
        users = cnt_status.tolist()
        print(books[0:5])

        blockid = BlockID()
        response = Response()
        itemList = response.itemList
        item = response.item
        button = response.button
        carousel_itemCard = response.carousel_itemCard
        simpleText = response.simpleText
        responseBody = response.responseBody

        items = []
        for book in books[0:5]:
            book = BookModel.find_by_id(book).json()
            item1 = deepcopy(item)
            item1['imageTitle']['title'] = book['title']
            item1['imageTitle']['imageUrl'] = book['img']

            itemLists = []
            itemList1 = deepcopy(itemList)
            itemList1['title'] = '지은이'
            itemList1['description'] = book['author']
            itemLists.append(itemList1)

            itemList2 = deepcopy(itemList)
            itemList2['title'] = '출판사'
            itemList2['description'] = book['publisher']
            itemLists.append(itemList2)

            itemList3 = deepcopy(itemList)
            itemList3['title'] = '출판일'
            itemList3['description'] = str(book['pubDate'])
            itemLists.append(itemList3)
            item1['itemList'] = itemLists

            buttons = []
            button1 = deepcopy(button)
            button1['action'] = 'webLink'
            button1['label'] = '책 정보'
            kyobo_url = f"https://www.kyobobook.co.kr/product/detailViewKor.laf?ejkGb=KOR&mallGb=KOR&barcode={book['isbn']}&orderClick=LEa&Kc="
            button1['webLinkUrl'] = kyobo_url
            buttons.append(button1)

            button2 = deepcopy(button)
            button2['action'] = 'block'
            button2['label'] = '책 저장'
            button2['blockId'] = blockid.save_menu
            button2['extra']['book_id'] = book['id']
            buttons.append(button2)
            item1['buttons'] = buttons

            items.append(item1)

        carousel_itemCard['carousel']['items'] = items
        simple_image = {
            "simpleImage": {
                "imageUrl": "http://43.200.157.176/static/images/graph.png",
                            "altText": "분석 그래프"
            }
        }

        simpleText['simpleText']['text'] = f"현재 {rank}등 입니다!😆.\n다른 유저들이 많이 읽은 책 입니다. 한 번 읽어 보세요~"

        outputs = [simple_image, simpleText, carousel_itemCard]
        responseBody['template']['outputs'] = outputs

        quickReplies = []
        quickReply = response.quickReply

        quickReply1 = deepcopy(quickReply)
        quickReply1['action'] = 'block'
        quickReply1['label'] = '뒤로가기'
        quickReply1['blockId'] = blockid.list_menu
        quickReplies.append(quickReply1)

        quickReply2 = deepcopy(quickReply)
        quickReply2['action'] = 'block'
        quickReply2['label'] = '도움말'
        quickReply2['blockId'] = blockid.howto
        quickReplies.append(quickReply2)

        responseBody['template']['quickReplies'] = quickReplies

        return responseBody
