import requests
import json

class Searching:
    def __init__(self):
        self.REST_API_KEY = 'c8981be15dbb94247a93cce5e564653b'
        self.url = "https://dapi.kakao.com/v3/search/book"

    def book(self, query):
        queryString = {"query": query}
        header = {'Authorization': f'KakaoAK {self.REST_API_KEY}'}
        r = requests.get(self.url, headers=header, params=queryString)
        books = json.loads(r.text)
        isbn = books['documents'][0]['isbn'].split()[1]
        return isbn

if __name__ == '__main__':
    #  title = input("찾고 싶은 책의 제목을 입력하세요: ")
    title = "나무"
    search = Searching()
    print(search.book(title))
