import os
from urllib import parse
import requests
from bs4 import BeautifulSoup
from io import BytesIO


# webtoon_id 을 인자로 받는 Class
class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self._title = None
        self._author = None
        self._description = None
        self._episode_list = list()
        self._html = ''

    def _get_info(self, attr_name):
        """
        내용 참조, webtoon class 초기화에서 title, author, description 내용이 없을 경우 set_info 에서 매칭되는 값 내용을 불러온다.
        :return:
        """
        if not getattr(self, attr_name):
            self.set_info()
        return getattr(self, attr_name)

    # 읽기 전용 속성
    # webtoon class 에 self.title 할 경우 () 없이도 해당하는 값을 가져올수 있다.
    @property
    def title(self):
        return self._get_info('_title')

    @property
    def author(self):
        return self._get_info('_author')

    @property
    def description(self):
        return self._get_info('_description')


    def set_info(self):
        """
        webtoon class 초기화 title, author, description 에 파싱한 결과를 할당
        :return:
        """
        soup = BeautifulSoup(self.html, 'lxml')

        h2_title = soup.select_one('div.detail > h2')
        title = h2_title.contents[0].strip()
        author = h2_title.contents[1].get_text(strip=True)
        description = soup.select_one('div.detail > p').get_text(strip=True)

        self._title = title
        self._author = author
        self._description = description

    # webtoon url 설정
    @property
    def html(self):
        if not self._html:
            # data 폴더에 webtoon_id로된 html파일
            file_path = 'data/episode_list-{webtoon_id}.html'.format(webtoon_id=self.webtoon_id)

            # HTTP 요청을 보낼 네이버웹툰 주소
            url_episode_list = 'http://comic.naver.com/webtoon/list.nhn'

            # HTTP 요청시 전달할 파라미터
            params = {
                'titleId': self.webtoon_id,
            }

            # 파일 유무 검사, 있을때는 읽기모드로 불러오고 변수에 할당, 없을때는 불러온다음 쓰기모드로 불러온 값을 작성하고 변수에 할당
            if os.path.exists(file_path):
                html = open(file_path, 'rt').read()
            else:
                response = requests.get(url_episode_list, params)
                html = response.text
                open(file_path, 'wt').write(html)
            self._html = html
        # html값 반환
        return self._html

    def crawler_episode_list(self):
        """
        webtoon_id에 해당하는 HTML 문서의 episode 목록을 생성
        :return:
        """

        soup = BeautifulSoup(self.html, 'lxml')

        table = soup.select_one('table.viewList')
        tr_list = table.select('tr')
        episode_list = list()

        for index, tr in enumerate(tr_list[1:]):
            if tr.get('class'):
                continue
            url_thumbnail = tr.select_one('td:nth-of-type(1) img').get('src')
            url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')

            # ???
            query_string = parse.urlsplit(url_detail).query
            query_dict = parse.parse_qs(query_string)
            no = query_dict['no'][0]

            # 웹툰 정보 찾기
            title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
            rating = tr.select_one('td:nth-of-type(3) strong').get_text(strip=True)
            created_date = tr.select_one('td:nth-of-type(4)').get_text(strip=True)

            # 매 에피소드 정보를 Episode 인스턴스로 생성
            # new_episode = Episode 인스턴스
            new_episode = Episode(
                webtoon_id = self.webtoon_id,
                no = no,
                url_thumbnail = url_thumbnail,
                title = title,
                rating = rating,
                created_date = created_date,
            )

            # episode_list를 Episode 인스턴스들 추가
            episode_list.append(new_episode)
        self._episode_list = episode_list

    @property
    def episode_list(self):
        # self.episode_list가 빈리스트가 아니라면 self.episode_list를 반환
        if not self._episode_list:
            self.crawler_episode_list()
        return self._episode_list

class Episode:
    def __init__(self, webtoon_id, no, url_thumbnail, title, rating, created_date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.created_date = created_date

    @property
    def url(self):
        """
        self.webtoon_id, self.no 요소를 사용하여 에피소드페이지(만화 화수 있는곳) 주소 리턴
        :return:
        """
        # url 주소 뒤에 입력한 파라미터 값을 연결해준다. 쿼리스트링 parse.urlencode(params)
        url = 'http://comic.naver.com/webtoon/detail.nhn?'
        params = {
            'titleId': self.webtoon_id,
            'no': self.no,
        }


        episode_url = url + parse.urlencode(params)
        return episode_url

    def get_image_url_list(self):
        file_path = 'data/episode_detail-{webtoon_id}-{episode_no}.html'.format(
            webtoon_id=self.webtoon_id,
            episode_no=self.no,
        )

        # file_path에 해당하는 파일이 있는지 검사
        if os.path.exists(file_path):
            print('파일이 존재합니다.')
            html = open(file_path, 'rt').read()
        else:
            print('파일이 없습니다. 해당하는 파일을 생성 후 불러온 값을 저장합니다.')
            response = requests.get(self.url)
            html = response.text
            open(file_path, 'wt').write(html)

        soup = BeautifulSoup(html, 'lxml')
        img_list = soup.select('div.wt_viewer > img')

        # img_list 에 있는 src 값을 가져온다. img_list에 반복값
        return [img.get('src') for img in img_list]

    def download_all(self):
        for url in self.get_image_url_list():
            self.download(url)

    def download(self, url_img):
        url_referer = f'http://comic.naver.com/webtoon/list.nhn?titleId={self.webtoon_id}'
        headers = {
            'Referer': url_referer,
        }
        response = requests.get(url_img, headers = headers)
        # 이미지 URL에서 이미지명을 가져옴
        file_name = url_img.rsplit('/', 1)[-1]

        dir_path = f'data/{self.webtoon_id}/{self.no}'
        os.makedirs(dir_path, exist_ok=True)

        file_path = f'{dir_path}/{file_name}'
        open(file_path, 'wb').write(response.content)

if __name__ == '__main__':
    #570503 연애혁명
    webtoon1 = Webtoon(570503)
    print(webtoon1.title)
    print(webtoon1.author)
    print(webtoon1.description)
    e1 = webtoon1.episode_list[0]
    e1.download_all()