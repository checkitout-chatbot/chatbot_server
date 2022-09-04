#csv 파일 insert
# 데이터 불러오기
import pandas as pd


data = pd.read_csv("C:/Users/YEBIN/Desktop/한이음/영화csv-1/2000.csv")


pd.set_option('display.max_row', 100)
pd.set_option('display.max_columns', 100)

# ProgrammingError: nan can not be used with MySQL 에러 방지
# MySQL이 파이썬의 NaN을 받아들이지 못하므로, 모두 None로 변경한다.
data = data.where((pd.notnull(data)), None)

# len(data.columns)

# 1. pymysql 불러오기
import pymysql

# 2. 데이터베이스 연결
db = pymysql.connect(host='chatbotdb.c3hrvk4wz2vi.ap-northeast-2.rds.amazonaws.com', port=3306, user='chatbot', password='checkitOut-2022',
                     db='test_db', charset='utf8')   # charset: 인코딩 설정

# 3. curosr 사용
cursor = db.cursor() 


# 4. 쿼리문 작성
# 컬럼명: 테이블의 컬럼명과 동일하게 입력
# %s 개수: 컬럼 개수만큼 입력

#열 : 13개

sql = 'INSERT INTO movies(openYear, n_code, title, genre, nation, runningTime, age, openDate, rate, participate, directors, actors, story, blank) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

# 5. 데이터 import
for idx in range(len(data)):
    cursor.execute(sql, tuple(data.values[idx]))

# 6. 데이터베이스 업데이트 및 작업 종료
db.commit() 

# 7. 데이터베이스 닫기 
db.close() 



