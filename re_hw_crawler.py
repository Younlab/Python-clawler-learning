import os
import requests
from bs4 import BeautifulSoup


webtoon_id = 667573
file_path = f'data/episode_list_{webtoon_id}.html'
url_episode_list = 'https://comic.naver.com/webtoon/list.nhn'
params = {
    'titleId':webtoon_id,
}

if os.path.exists(file_path):
    html = open(file_path, 'rt').read()
else:
    response = requests.get(url_episode_list, params)
    html = response.text
    open(file_path, 'wt').write(html)

soup = BeautifulSoup(html, 'lxml')

title = soup.select_one('div.detail > h2').get_text(strip=True)
title_except = soup.select_one('div.detail > p').get_text(strip=True)

table = soup.select_one('table.viewList')
tr_list = table.select('tr')

print(title)
print(title_except)

for index, tr in enumerate(tr_list[1:]):
    if tr.get('class'):
        continue

    webtoon_list = tr.select_one('td:nth-of-type(2) > a').get_text(strip=True)
    webtoon_img_link = tr.select_one('td:nth-of-type(2) > a').get('href')
    webtoon_img_src = tr.select_one('td:nth-of-type(1) > a > img').get('src')
    webtoon_date = tr.select_one('td:nth-of-type(4)').get_text(strip=True)

    print(webtoon_list)
    print(webtoon_img_link)
    print(webtoon_img_src)
    print(webtoon_date)
