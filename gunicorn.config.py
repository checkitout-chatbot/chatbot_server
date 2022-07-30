import multiprocessing

# master 프로세스가 fork하는 worker 프로세스 수
workers = multiprocessing.cpu_count() * 2 + 1

# 실행 모듈
wsgi_app = 'run:app'

# code가 변경될 때 마다 worker가 재시작
reload = True

# port 주소
bind = '0.0.0.0:5000'

# errorlog의 level
loglevel = 'info'
# gunicorn access log파일 경로
accesslog = 'log/gunicorn.log'
