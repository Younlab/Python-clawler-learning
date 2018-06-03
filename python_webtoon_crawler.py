import requests
import os
from bs4 import BeautifulSoup

class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.title = None
        self.author = None
        self.description = None
        self._html = ''


    def get_url(self):
        pass

    def get_info(self):
        pass

    @property
    def file_search(self):

        if not self._html:
            file_path = f'deta/webtoon_list_{self.webtoon_id}.html'
            webtoon_list_url = 'https://comic.naver.com/webtoon/list.nhn'
            webtoon_list_id = {
                'titleId': self.webtoon_id
            }
            if os.path.exists(file_path):
                html = open(file_path, 'rt').read()
            else:
                response = requests.get(webtoon_list_url, webtoon_list_id)
                html = response.text
                open(file_path, 'wt').write(html)
            self._html = html
        return self._html


    def crawler(self):
        soup = BeautifulSoup(self.file_search, 'lxml')
        h2_title = soup.select_one('div.detail > h2')
        title = h2_title.contents[0].strip()
        self.title = title
        print(title)

class Episode:
    def __init__(self):
        pass


class Episode_image:
    def __init(self):
        pass


if __name__ == '__main__':
    webtoon1 = Webtoon(667573)
    webtoon1.crawler()