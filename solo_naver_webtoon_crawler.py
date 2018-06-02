import os
from urllib import parse
import requests
from bs4 import BeautifulSoup

class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self._title = None
        self._author = None
        self._description = None
        self.webtoon_list = list()
        self._html = ''

    @property
    def url(self):
        """
        get webtoon html url
        :return:
        """
        if not self._html:
            webtoon_url = 'http://comic.naver.com/webtoon/list.nhn'
            params = {
                'titleId': self.webtoon_id,
            }
            file_path = 'data/webtoon_{}.html'.format(self.webtoon_id)

            if os.path.exists(file_path):
                html = open(file_path, 'rt').read()
            else:
                response = requests.get(webtoon_url, params)
                html = response.text
                open(file_path, 'wt').write(html)
            self._html = html
        return self._html

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
        soup = BeautifulSoup(self.url, 'lxml')

        h2_title = soup.select_one('div.detail > h2')
        title = h2_title.contents[0].strip()
        author = h2_title.contents[1].get_text(strip=True)
        description = soup.select_one('div.detail > p').get_text(strip=True)

        self._title = title
        self._author = author
        self._description = description

    def crawler(self):
        soup = BeautifulSoup(self.url, 'lxml')

        pass



if __name__ == '__main__':
    webtoon1 = Webtoon(670149)
    print(webtoon1.title)
    print(webtoon1.author)
    print(webtoon1.description)
