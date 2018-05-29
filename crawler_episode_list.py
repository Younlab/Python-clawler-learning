import os

import requests
from bs4 import BeautifulSoup

# HTML 파일을 저장하거나 불러올 경로
file_path = 'data/episode_list.html'
# HTTP 요청을 보낼 주소
url_episode_list = 'http://comic.naver.com/webtoon/list.nhn'
# HTML 요청시 전달할 GET Paraneters
params = {
    'titleId':703845,
}

# HTML 파일이 로컬에 저장되어 있는지 검사
if os.path.exists(file_path):
    # 저장되어 있다면, 해당 파일을 읽어서 html 변수에 할당
    html = open(file_path, 'rt').read()
else:
    # 저장되어 있지 않다면, requsets 를 사용해 HTTP GET 요청
    response = requests.get(url_episode_list, params)
    # 요청 응답 객체의 text속성값을 html 변수에 할당
    html = response.text
    # 받은 텍스트 데이터를 HTML 파일로 저장
    open(file_path, 'wt').write(html)

# BeautifulSoup 클래스형 객체 생송 및 soup 변수에 할당
soup = BeautifulSoup(html, 'lxml')

h2_title = soup.select_one('div.detail > h2')
print(h2_title)