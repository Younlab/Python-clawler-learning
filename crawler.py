from utils import Webtoon, Episode
from bs4 import BeautifulSoup
from itertools import count
import requests

class SearchWebtoon:
    def __init__(self):
        self.search_list = None
        self.webtoon_id_list = None

    def search_webtoon(self, keyword):
        params = {'keyword': keyword}
        response = requests.get('https://comic.naver.com/search.nhn?', params)
        soup = BeautifulSoup(response.text, 'lxml')
        result_list = soup.select('ul.resultList > li')

        search_list = list()
        webtoon_id_list = list()
        for index, result in enumerate(result_list):
            try:
                if result.select_one('img').get('title').strip() == '웹툰':
                    search_list.append(result.select_one('img').find_next_sibling().contents[0])
                    webtoon_id_list.append(result.select_one('h5').a['href'].split('=')[-1])
                self.search_list = search_list
                self.webtoon_id_list = webtoon_id_list
            except AttributeError:
                break

        if search_list:
            for index, title, number in zip(count(), search_list, webtoon_id_list):
                print(f'{index+1}. {title} [{number}]')

        else:
            print('검색 결과가 없습니다. 다른 검색어를 입력해주세요')
            search_input = input('검색할 웹툰명을 입력해주세요 : ')
            return self.search_webtoon(search_input)


def search_main():
    search_input = input('검색할 웹툰명을 입력해주세요 : ')
    webtoon_find = SearchWebtoon()
    webtoon_find.search_webtoon(search_input)
    choice_input1 = input('선택 : ')
    print(f'현재 "{webtoon_find.search_list[int(choice_input1)-1]}" 웹툰이 선택되어 있습니다.')
    print('1. 웹툰 정보 보기')
    print('2. 웹툰 저장하기')
    print('3. 다른 웹툰 검색해서 선택하기')
    choice_input2 = input('선택 : ')
    while 1:
        if choice_input2 == '1':
            print('1번을 선택했습니다')
            webtoon1 = Webtoon(webtoon_find.webtoon_id_list[int(choice_input1)-1])
            webtoon1.webtoon_html()
            webtoon1.set_info()
            return search_main()

        elif choice_input2 == '2':
            print('2번은 선택했습니다')
            webtoon1 = Webtoon(webtoon_find.webtoon_id_list[int(choice_input1)-1])
            webtoon1.webtoon_html()
            webtoon1.set_info()
            for episode in webtoon1.crawler_episode_list():
                print(f'======{episode} 다운로드 중=====')
                episode.download_all()
            print('저장이 완료되었습니다.')
            return search_main()

        elif choice_input2 =='3':
            print('3번을 선택했습니다')
            return search_main()

        else:
            print('다시 선택해주세요')
            choice_input2 = input('선택 : ')


if __name__ == '__main__':
    print('안내) Ctrl+C로 종료합니다.')
    search_main()
