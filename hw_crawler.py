import os

import requests
from bs4 import BeautifulSoup
from urllib import parse

# 변수모음
yumi = 651673
deth = 703845


class Episode:
    def __init__(self, webtoon_id, no, url_thumbnaile, title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnaile = url_thumbnaile
        self.title = title
        self.rating = rating
        self.created_date = created_date

    @property
    def url(self):
        url = 'http://comic.naver.com/webtoon/detail.nhn?'
        params = {
            'titleId': self.webtoon_id,
            'no': self.no,
        }

        episode_url = url + parse.urlencode(params)
        return episode_url

# q = episode_crawler(deth)

# 클래스는 클래스 내부에서 self로 접근이 가능하다.
class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        # 빈문자로 초기화 하는경우와 '' 빈 스트링으로 초기화는 다르다.
        self._title = None
        self._author = None
        self._description = None
        self.episode_list = list()
        self._html = ''
        self.set_info()

    # 인스턴스에 title 속성값이 존재하면 그걸 리턴
    # 없으면 set_info()호출 후에 인스턴스의 title값을 리턴
    @property
    def get_title(self):
        if not self._title:
            self.set_info()
        return self._title

    @property
    def get_author(self):
        if not self._author:
            self.set_info()
        return self._author

    @property
    def get_description(self):
        if not self._description:
            self.set_info()
        return self._description

    def update(self):
        """
        update 함수를 실행하면 해당 webtoon_id 에 따른 에피소드 정보들을 Episode 인스턴스로 저장
        :return:
        """
        result = self.episode_crawler
        self.episode_list = result

    @property
    def get_html(self):
        # 인스턴스의 html속성이 False(빈 문자열) 일 경우
        if not self._html:
            # get_html 의 결과 문자열을
            # 인스턴스가 갖고있을 수 있도록 설정
            # 1. 인스턴스가 html데이터를 갖고있지 않을 경우
            #    인스턴스의 html속성에 데이터를 할당
            # 2. 갖고있으면
            #    인스턴스의 html속성을 리턴
            # HTML 파일을 저장하거나 불러올 경로
            file_path = f'data/episode_list_{self.webtoon_id}.html'
            # HTTP 요청을 보낼 주소
            url_episode_list = 'http://comic.naver.com/webtoon/list.nhn'
            # HTML 요청시 전달할 GET Paraneters
            params = {
                'titleId': self.webtoon_id,
            }

            # HTML 파일이 로컬에 저장되어 있는지 검사
            if os.path.exists(file_path):
                # 저장되어 있다면, 해당 파일을 읽어서 html 변수에 할당
                html = open(file_path, 'rt').read()
            else:
                # 저장되어 있지 않다면, requsets 를 사용해 HTTP GET 요청
                response = requests.get(url_episode_list, params)
                print(response.url)
                # 요청 응답 객체의 text속성값을 html 변수에 할당
                html = response.text
                # 받은 텍스트 데이터를 HTML 파일로 저장
                open(file_path, 'wt').write(html)
            # self.html 로 할당하여 인스턴스 메소드로 지정
            self._html = html
            # self.html 의 값을 반환
            return self._html
        # self.html 에 해당하는 값이 있을경우 그대로 self.html을 반환
        return self._html

    def set_info(self):
        """
        자신의 html속성을 파싱한 결과를 사용해
        자신의 title, author, description속성갑을 할당
        :return:
        """

        # BeautifulSoup 클래스형 객체 생송 및 soup 변수에 할당
        soup = BeautifulSoup(self.get_html, 'lxml')

        # div.detail > h2dml
        # 0번째 자식: 제목 텍스트
        # 1번째 자식: 작가정보 span Tag
        #   Tag로부터 문자열을 가져올때는 get_text()
        h2_title = soup.select_one('div.detail > h2')
        title = h2_title.contents[0].strip()
        author = h2_title.contents[1].get_text(strip=True)

        # div.detail > p (설명)
        description = soup.select_one('div.detail > p').get_text(strip=True)

        # 자신의 html데이터를 사용해서(웹에서 받아오거나, 파일에서 읽어온 결과)
        # 자신의 속성들을 지정
        self._title = title
        self._author = author
        self._description = description

    def episode_crawler(self):
        """
        webtoon_id 를 입력받아서 webtoon_id, title, no, created_date 등등 이런 정보를 가져오는 크롤러
        :return:
        """
        # HTML 파일을 저장하거나 불러올 경로
        # file_path = f'data/episode_list_{self.webtoon_id}.html'


        # BeautifulSoup 클래스형 객체 생송 및 soup 변수에 할당
        soup = BeautifulSoup(self.get_html, 'lxml')

        # 에피소드 목록을 담고 있는 table
        table = soup.select_one('table.viewList')

        # table 내의 모든 tr요소 목록
        tr_list = table.select('tr')

        # list를 리턴하기 위해 선언
        # for 문을 다  실행하면 episode_list 에는 Episode 인스턴스가 들어가있음
        episode_list = list()

        # 첫번째 tr은 thead의 tr이므로 제외, tr_list의 [1:]부터 순회
        for index, tr in enumerate(tr_list[1:]):
            # 에피소드에 해당하는 tr은 클래스가 없으므로,
            # 현재 순회중인 tr요소가 클래스 속성값을 가진다면 continue
            if tr.get('class'):
                continue

            # 현재 tr의 첫 번째 td요소의 하위 img 태그의 'src'속성값
            url_thumbnaile = tr.select_one('td:nth-of-type(1) img').get('src')
            # 현재 tr의 첫 번째 td요소의 자식 a태그의 'href'속성값
            url_detail = tr.select_one('td:nth-of-type(1) a').get('href')
            # 현재 tr의 두 번째 td요소의 자식 a요소의 내용
            title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
            # 현재 tr의 세 번째 td요소의 하위 strong 태그의 내용
            rating = tr.select_one('td:nth-of-type(3) strong').get_text(strip=True)
            # 현재 tr의 네 번째 td요소의 내용
            created_date = tr.select_one('td:nth-of-type(4)').get_text(strip=True)

            url_full = url_detail
            url_parse = parse.urlsplit(url_full)
            url_qs = parse.parse_qs(url_parse.query)
            url_parse_push = dict(url_qs)
            no = url_parse_push['no'][0]

            # print(url_thumbnail)
            # print(url_detail)
            # print(title)
            # print(rating)
            # print(created_date)
            # print(no)

            # 매 에피소드 크롤링한 결과를 Episode 클래스의
            # new_episode =Episode 인스턴스(객채)
            new_episode = Episode(
                webtoon_id=self.webtoon_id,
                no=no,
                url_thumbnaile=url_thumbnaile,
                title=title,
                rating=rating,
                created_date=created_date,
            )

            # episode_list 에 인스턴스를 추가
            episode_list.append(new_episode)

        return episode_list

webtoon1 = Webtoon(703845)
print(webtoon1._title)
webtoon1.update()
if __name__ =='__main__':
    print(webtoon1._title)
    webtoon1.update()
    # for episode in webtoon1.episode_list:
    #     print(episode.url)
