import os
import requests
from bs4 import BeautifulSoup
from urllib import parse

class Webtoon:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.title = None
        self.author = None
        self.description = None
        self.no = None
        self.page_number = None
        self.episode_list = list()
        self._html = ''

    def webtoon_html(self, page_number=None):
        if page_number is None:
            page_number = 1

        if not self._html:
            file_path = f'data/webtoon_{self.title}_{self.webtoon_id}_{self.page_number}.html'
            webtoon_url = 'https://comic.naver.com/webtoon/list.nhn'
            params = {
                'titleId': self.webtoon_id,
                'page': self.page_number,
            }

            if os.path.exists(file_path):
                html = open(file_path, 'rt').read()
            else:
                response = requests.get(webtoon_url, params)
                html = response.text
                open(file_path, 'wt').write(html)
            self._html = html
        return self._html

    def set_info(self):
        soup = BeautifulSoup(self.webtoon_html(), 'lxml')
        find_div = soup.select_one('div.detail > h2')
        title = find_div.contents[0].strip()
        author = find_div.contents[1].get_text(strip=True)
        description = soup.select_one('div.detail > p').get_text(strip=True)

        tr_list = soup.select_one('table.viewList > tr')
        episode_list = list()
        for index, tr in enumerate(tr_list[1:]):
            if tr.get('class'):
                continue
            url = tr.select_one('td:nth-of-type(1) > a').get('href')
            query_string = parse.parse_qs(url).query
            query_dict = parse.parse_qs(query_string)
            self.no = query_dict['no'][0]
            episode_list.append(self.no)

        # print(f'제목 : {self.title}\n'
        #       f'작가 : {self.author}\n'
        #       f'스토리 : {self.description}\n')

        self.title = title
        self.author = author
        self.description = description
        print(title)
        print(author)
        print(description)

    def crawler_episode_list(self):
        soup = BeautifulSoup(self.webtoon_html(), 'lxml')
        self.page_number = soup.select_one('div.page_wrap > a').get_text(strip=True)
        episode_list = list()
        for no in range(1, int(self.page_number)+1):
            self.webtoon_html(no)
            table = soup.select_one('table.viewList')
            tr_list = table.select('tr')
            for index, tr in enumerate(tr_list[1:]):
                if tr.get('class'):
                    continue
                url = 'https://comic.naver.com'+tr.select_one('td:nth-of-type(1) > a').get('href')
                title = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
                query_string = parse.urlsplit(url).query
                query_dict = parse.parse_qs(query_string)
                episode_no = query_dict['no'][0]
                new_episode = Episode(
                    webtoon_id = self,
                    title = title,
                    url = url,
                    episode_no = episode_no,
                )

                episode_list.append(new_episode)
        return episode_list


class Episode:
    def __init__(self, webtoon_id, title, url, episode_no):
        self.webtoon_id = webtoon_id
        self.title = title
        self.url = url
        self.episode_no = episode_no

    def __repr__(self):
        return f'{self.title}'

    def get_images_url(self):
        file_path = f'data/webtoon_{self.title}_{self.webtoon_id.webtoon_id}_{self.episode_no}.html'
        if os.path.exists(file_path):
            html = open(file_path, 'rt').read()
        else:
            response = requests.get(self.url)
            html = response.text
            open(file_path, 'wt').write(html)
        soup = BeautifulSoup(html, 'lxml')
        images = soup.select('div.wt_viewer > img')
        return [img.get('src') for img in images]

    def download_all(self):
        for url in self.get_images_url():
            self.download(url)
        print(f'{self} Saved')

    def download(self, url_img):
        url_referer = f'http://comic.naver.com/webtoon/list.nhn?titleId={self.webtoon_id.webtoon_id}'
        headers = {
            'Referer': url_referer
        }
        response = requests.get(url_img, headers=headers)
        file_name = url_img.rsplit('/', 1)[-1]
        dir_path = f'data/{self.webtoon_id.webtoon_id}/{self.episode_no}'
        os.makedirs(dir_path, exist_ok=True)
        file_path = f'{dir_path}/{file_name}'
        open(file_path, 'wb').write(response.content)

if __name__ =='__main__':
    webtoon1 = Webtoon(557676)
    webtoon1.set_info()
