from pprint import pprint


class Response:
    def __init__(self):
        self.responseBody = {
            "version": "2.0",
            "template": {
                "outputs": []
            }
        }
        self.simpleText = {
            "simpleText": {
                "text": ""
            }
        }
        self.itemList = {
            "title": "",
            "description": ""
        }
        self.button = {
            "label": "",
            "action": "",
            "extra": {
                "isbn": ""
            }
        }
        self.item = {
            "imageTitle": {
                "title": "",
                "imageUrl": ""
            },
            "itemList": [
            ],
            "itemListAlignment": "right",
            "buttons": [
            ]
        }
        self.carousel_itemCard = {
            "carousel": {
                "type": "itemCard",
                "items": [
                ]
            }
        }
        self.quickReply = {
            "messageText": "",
            "action": "",
            "label": ""
        }
        self.itemCard = {
            "itemCard": {
                "imageTitle": {
                    "title": "",
                    "imageUrl": "",
                },
                "itemList": [
                ],
                "itemListAlignment": "right",
                "buttons": [
                ],
                "buttonLayout": "horizontal"
            }
        }
        self.carousel_listCard = {
            "carousel": {
                "type": "listCard",
                "items": [
                ]
            }
        }
        self.listItem = {
            "header": {
                "title": ""
            },
            "items": [
            ],
            "buttons": [
            ]
        }


class BlockID:
    def __init__(self):
        self.home = '62c9057128d63278024c16a2'
        self.list_menu = '62c90931903c8b5a8004448c'
        self.recom_menu = '62c7e7ade262a941bbdca4ea'
        self.search_menu = '62dd372c28d63278024d6104'
        self.save_want = '62dd402d903c8b5a80058543'
        self.save_review = '62dd404bc7d05102c2ccffb4'
        self.howto = '62dd3d75c7d05102c2ccffa4'
        self.save_menu = '62e28d6e0326e262b80b4183'


if __name__ == "__main__":
    #  response = Response()
    #  itemList = response.itemList
    #  item = response.item
    #  button = response.button
    #  carousel_itemCard = response.carousel_itemCard
    #  simpleText = response.simpleText
    #  responseBody = response.responseBody
    #
    #  itemLists = []
    #  itemList1 = itemList.copy()
    #  itemList1['title'] = '지은이'
    #  itemList1['description'] = '존 브룩스'
    #  itemLists.append(itemList1)
    #
    #  itemList2 = itemList.copy()
    #  itemList2['title'] = '출판사'
    #  itemList2['description'] = '쌤앤파커스'
    #  itemLists.append(itemList2)
    #  item['itemList'] = itemLists
    #
    #  buttons = []
    #  button1 = button.copy()
    #  button1['action'] = 'webLink'
    #  button1['label'] = '책 정보'
    #  button1['webLinkUrl'] = 'kybo URL'
    #  buttons.append(button1)
    #
    #  button2 = button.copy()
    #  button2['action'] = 'block'
    #  button2['label'] = '책 저장'
    #  button2['blockId'] = '블록 아이디'
    #  button2['extra']['isbn'] = "98391289381203"
    #  buttons.append(button2)
    #  item['buttons'] = buttons
    #
    #  items = []
    #  item1 = item.copy()
    #  item1['imageTitle']['title'] = '경영의 모험'
    #  item1['imageTitle']['imageUrl'] = '이미지 주소'
    #  items.append(item1)
    #  carousel_itemCard['carousel']['items'] = items
    #
    #  simpleText['simpleText']['text'] = '고심해서 고른 책이에요 어떠세요??'
    #  outputs = [simpleText, carousel_itemCard]
    #  responseBody['template']['outputs'] = outputs
    #
    #  pprint(responseBody, depth=10, indent=2, sort_dicts=False)

    response = Response()
    itemList = response.itemList
    listItem = response.listItem
    button = response.button
    carousel_listCard = response.carousel_listCard
    simpleText = response.simpleText
    responseBody = response.responseBody

    itemLists = []
    itemList1 = itemList.copy()
    itemList1['title'] = '경영의 모험'
    itemList1['description'] = '존 브룩스'
    itemList1['imageUrl'] = 'http://이미지 주소'
    itemList1['action'] = 'block'
    itemList1['blockId'] = '48198249018209'
    extra = {'isbn': '1232131'}
    itemList1['extra'] = extra
    itemLists.append(itemList1)
    listItem['itemList'] = itemLists

    listItems = []
    listItem1 = listItem.copy()
    listItem1['header']['title'] = '읽고 싶은 책 목록1'
    listItems.append(listItem1)
    carousel_listCard['carousel']['items'] = listItems

    simpleText['simpleText']['text'] = '고심해서 고른 책이에요 어떠세요??'
    outputs = [simpleText, carousel_listCard]
    responseBody['template']['outputs'] = outputs

    pprint(responseBody, depth=10, indent=2, sort_dicts=False)
