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
        self._episode_list = list()
        self._html = ''

    @property
    def get_url(self):
        if not self._html:
            file_path = 'data/webtoon_{webtoon_id}.html'.format(webtoon_id=self.webtoon_id)
            url_episode = 'https://comic.naver.com/webtoon/list.nhn'
            prams = {
                'titleId': self.webtoon_id,
            }
            if os.path.exists(file_path):
                html = open(file_path, 'rt').read()
            else:
                response = requests.get(url_episode, prams)
                html = response.text
                open(file_path, 'wt').write(html)
            self._html = html
        return self._html

    def _get_info(self, name):
        if not getattr(self, name):
            self.set_info()
        return getattr(self, name)

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
        soup = BeautifulSoup(self.get_url, 'lxml')
        h2_title = soup.select_one('div.detail > h2')
        title = h2_title.contents[0].strip()
        author = h2_title.contents[1].get_text(strip=True)
        description = soup.select_one('div.detail > p').get_text(strip=True)

        self._title = title
        self._author = author
        self._description = description


    def crawler(self):
        soup = BeautifulSoup(self.get_url, 'lxml')
        table = soup.select_one('table.viewList')
        tr_list = table.select('tr')
        episode_list = list()
        for index, tr in enumerate(tr_list[1:]):
            if tr.get('class'):
                continue
            url_thum = tr.select_one('td:nth-of-type(1) img').get('src')
            url_detail = tr.select_one('td:nth-of-type(1) > a').get('href')
            query_string = parse.urlsplit(url_detail).query
            query_dict = parse.parse_qs(query_string)
            print(query_dict)
            no = query_dict['no'][0]

            title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
            rating = tr.select_one('td:nth-of-type(3) strong').get_text(strip=True)
            date = tr.select_one('td:nth-of-type(4)').get_text(strip=True)

            new_episode = Episode(
                webtoon_id = self.webtoon_id,
                no = no,
                url_thumbnail = url_thum,
                title = title,
                rating = rating,
                date = date,
            )
            episode_list.append(new_episode)
        self._episode_list = episode_list

    @property
    def episode_list(self):
        if not self._episode_list:
            self.crawler()
        return self._episode_list

class Episode:
    def __init__(self, webtoon_id, no, url_thumbnail, title, rating, date):
        self.webtoon_id = webtoon_id
        self.no = no
        self.url_thumbnail = url_thumbnail
        self.title = title
        self.rating = rating
        self.date = date

    @property
    def get_episode_url(self):
        url = 'http://comic.naver.com/webtoon/detail.nhn?'
        params = {
            'titleId': self.webtoon_id,
            'no': self.no
        }
        episode_url = url + parse.urlencode(params)
        return episode_url

    def get_imgage_url_list(self):
        file_path = f'data/{self.title}_{self.webtoon_id}_{self.no}.html'
        if os.path.exists(file_path):
            html = open(file_path, 'rt').read()
        else:
            response = requests.get(self.get_episode_url)
            html = response.text
            open(file_path, 'wt').write(html)
        soup = BeautifulSoup(html, 'lxml')
        img_list = soup.select('div.wt_viewer > img')
        return [img.get('src') for img in img_list]

    def download_image(self):
        for url in self.get_imgage_url_list():
            self.download(url)

    def download(self, url_img):
        url_referer = f'http://comic.naver.com/webtoon/list.nhn?titleId={self.webtoon_id}'
        headers = {
            'Referer': url_referer,
        }
        response = requests.get(url_img, headers = headers)
        file_name = url_img.rsplit('/', 1)[-1]

        dir_path = f'data/{self.webtoon_id}_{self.title}/{self.no}'
        os.makedirs(dir_path, exist_ok=True)

        file_path = f'{dir_path}/{file_name}'
        open(file_path, 'wb').write(response.content)


if __name__ == '__main__':
    webtoon1 = Webtoon(183559)
    print(webtoon1.title)
    print(webtoon1.author)
    print(webtoon1.description)
    e1 = webtoon1.episode_list[0]
    e1.download_image()
