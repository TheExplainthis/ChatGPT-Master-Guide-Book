import datetime
import requests
from bs4 import BeautifulSoup


class MovieCrawler():
    def __init__(self, area, days):
        self.url = 'https://movies.yahoo.com.tw/movie_intheaters.html?page='
        self.area = area
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62'
        }
        self.days = days

    def get_release_infos(self, url):
        res = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.find_all('div', 'release_info')

    def get_schedule_time(self, id, date):
        theaters = {}
        url = f'https://movies.yahoo.com.tw/ajax/pc/get_schedule_by_movie?movie_id={id}&date={date}'
        res = requests.get(url, cookies={'over18': '1'}, headers=self.headers)
        view = res.json()['view']
        soup = BeautifulSoup(view, 'html.parser')
        area_timebox = soup.find_all('div', class_='area_timebox')
        for schedule_info in area_timebox:
            area_title = schedule_info.find('div', attrs={'class': 'area_title'}).text.strip()
            if area_title in self.area:
                theater_time_details = schedule_info.find_all('ul', {'class': 'area_time _c jq_area_time'})
                infos = []
                for theater_time_detail in theater_time_details:
                    name = theater_time_detail.find('li', 'adds').find('a').text
                    phone = theater_time_detail.find('li', 'adds').find('span').text
                    taps = theater_time_detail.find_all('li', 'taps')
                    movie_start_times = {}
                    for tap in taps:
                        type_name = tap.find('span', 'tapR').text.strip()
                        elements = tap.find_next_sibling('li', 'time _c').find('div', class_='input_picker jq_input_picker')
                        start_time = ', '.join([el.text for el in elements.find_all('label')])
                        movie_start_times[type_name] = start_time
                    infos.append({'theater_name': name, 'theater_phone': phone, 'movie_start_times': movie_start_times})
                theaters[area_title] = infos
        return theaters

    def get_movie_info(self, url):
        res = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        image_url = soup.find('div', 'movie_intro_foto').find('img')['src']
        movie_intro_info_r = soup.find('div', 'movie_intro_info_r')
        level_name = [level.a.text.strip() for level in movie_intro_info_r.find_all('div', 'level_name')]

        key_map = {
            '上映日期': 'release_date',
            '片　　長': 'movie_length',
            '發行公司': 'company',
            'IMDb分數': 'imdb_rate',
            '導演': 'director',
            '演員': 'cast',
            '官方連結': 'link'
        }
        release_info = {}
        spans = movie_intro_info_r.find_all('span')
        for span in spans:
            key_value_pair = span.text.strip().split('：')
            if len(key_value_pair) == 2:
                key, value = key_value_pair
                release_info[key_map[key]] = value.strip().replace('\n', '').replace(' ', '')

        rated_mapping = {
            'icon_0': '普遍級',
            'icon_6': '保護級',
            'icon_12': '輔十二級',
            'icon_15': '輔十五級',
            'icon_18': '限制級'
        }
        rated = rated_mapping[movie_intro_info_r.find('div')['class'][0]] if len(movie_intro_info_r.find('div')['class']) != 0 else '無分級資訊'
        story = soup.find('span', id='story').text.strip()
        return {'movie_type': level_name, 'image_url': image_url, 'release_info': release_info, 'rated': rated, 'story': story}

    def get_movies(self, page):
        movies_info = []
        for i in range(1, page+1):
            release_infos = self.get_release_infos(f'{self.url}{i}')
            for release_info in release_infos:
                name = release_info.find('div', 'release_movie_name').a.text.strip()
                eng_name = release_info.find('div', 'en').a.text.strip()
                release_time = release_info.find('div', 'release_movie_time').text.split('：')[-1].strip()
                anticipation = release_info.find('div', 'leveltext').text.replace(' ', '').replace('\n', '').replace('網友想看', '') if release_info.find('div', 'leveltext') is not None else ''
                detailed_link = release_info.find('div', 'release_btn').find_all('a')
                movie_detailed = self.get_movie_info(detailed_link[0]['href'])
                id = detailed_link[3]['href'].split('/id=')[1] if detailed_link[3]['href'] else None
                first_day = datetime.datetime.today()
                last_day = first_day + datetime.timedelta(days=self.days)
                schedule_times = {}
                if id:
                    while first_day < last_day:
                        date = first_day.strftime('%Y-%m-%d')
                        schedule_times[date] = self.get_schedule_time(id, date)
                        first_day += datetime.timedelta(days=1)
                movies_info.append({'movie_name': name, 'movie_english_name': eng_name, 'website_url': detailed_link[0]['href'], 'release_time': release_time, 'anticipation': anticipation, 'movie_detailed': movie_detailed, 'movie_schedule_time': schedule_times})
        return movies_info


# area = ['新竹', '台南', '彰化', '新北市', '花蓮', '嘉義', '雲林', '台北市', '澎湖', '屏東', '台中', '高雄', '南投', '桃園', '苗栗', '基隆', '宜蘭', '金門', '台東']
area = ['台北市']
movie_crawler = MovieCrawler(area=area, days=1)
