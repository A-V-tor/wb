import requests
import pandas as pd
import csv
from bs4 import BeautifulSoup
import time
import asyncio
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import aiofiles as aiof
from idslist import datalist


REGIONS_RUSSIA = [
    "Белгородская область",
    "Брянская область",
    "Владимирская область",
    "Воронежская область",
    "Ивановская область",
    "Калужская область",
    "Костромская область",
    "Курская область",
    "Липецкая область",
    "Московская область",
    "Орловская область",
    "Рязанская область",
    "Смоленская область",
    "Тамбовская область",
    "Тверская область",
    "Тульская область",
    "Ярославская область",
    "Москва",
    "Республика Адыгея",
    "Республика Калмыкия",
    "Республика Крым",
    "Краснодарский край",
    "Астраханская область",
    "Волгоградская область",
    "Ростовская область",
    "Севастополь",
    "Республика Карелия",
    "Республика Коми",
    "Архангельская область",
    "Вологодская область",
    "Калининградская область",
    "Ленинградская область",
    "Мурманская область",
    "Новгородская область",
    "Псковская область",
    "Ненецкий автономный округ",
    "Санкт-Петербург",
    "Республика Саха (Якутия)",
    "Камчатский край",
    "Приморский край",
    "Хабаровский край",
    "Амурская область",
    "Магаданская область",
    "Сахалинская область",
    "Еврейская автономная область",
    "Чукотский автономный округ",
    "Республика Алтай",
    "Республика Бурятия",
    "Республика Тыва",
    "Республика Хакасия",
    "Алтайский край",
    "Забайкальский край",
    "Красноярский край",
    "Иркутская область",
    "Кемеровская область",
    "Новосибирская область",
    "Омская область",
    "Томская область",
    "Курганская область",
    "Свердловская область",
    "Тюменская область",
    "Челябинская область",
    "Ханты-Мансийский автономный округ — Югра",
    "Ямало-Ненецкий автономный округ",
    "Республика Башкортостан",
    "Республика Марий Эл",
    "Республика Мордовия",
    "Республика Татарстан",
    "Удмуртская Республика",
    "Чувашская Республика",
    "Кировская область",
    "Нижегородская область",
    "Оренбургская область",
    "Пензенская область",
    "Ульяновская область",
    "Самарская область",
    "Саратовская область",
    "Республика Дагестан",
    "Республика Ингушетия",
    "Кабардино-Балкарская Республика",
    "Карачаево-Черкесская Республика",
    "Республика Северная Осетия — Алания",
    "Чеченская Республика",
    "Ставропольский край"
]


class Point:
    """ПВЗ."""

    file_name = 'fileNewLink2.csv'
    headers = {
    'authority': 'static-basket-01.wb.ru',
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'origin': 'https://www.wildberries.ru',
    'pragma': 'no-cache',
    'referer': 'https://www.wildberries.ru/services/besplatnaya-dostavka?desktop=1',
    'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
}
    main_url = 'https://static-basket-01.wb.ru/vol0/data/all-poo-fr-v2.json'
    main_url_2 = 'https://static-basket-01.wb.ru/vol0/data/all-poo-fr-v3.json' # версия id совпадают с https://www.wildberries.ru/webapi/poo/byids
    data_list_for_csv = [['Номер', 'ID', 'Рабочее время', 'Кол-во примерочных', 'Адрес', 'Координаты']]
    recording_resolution = False
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    browser = Chrome(options=options)

    def get_main_data_by_points(self):
        """Получить список ПВЗ."""

        response =  requests.get(self.main_url_2, headers=self.headers, timeout=10)
        for num, point in enumerate(response.json()[0]['items']):
            num = num + 1
            id = point.get('id')
            work_time = point.get('workTime')
            fitting_rooms = point.get('fittingRooms')
            address = point.get('address')
            coordinates = point.get('coordinates')
            self.data_list_for_csv.append([num, id, work_time, fitting_rooms, address, coordinates])
    
        self.recording_resolution = True

    async def data_to_csv(self):
        """Запись данных в файл."""
    
        if not self.recording_resolution:
            raise Exception('Сначало надо получить данные')

        async with aiof.open(self.file_name, "w") as f:
            writer = csv.writer(f)
            for row in self.data_list_for_csv:
                await writer.writerow(row)

    def sort_by_coord(self):
        """Сортировка по координатам."""

        data = pd.read_csv(self.file_name, delimiter=',')
        data = data.sort_values('Координаты')

        data.to_csv('sorted_data_by_coord.csv', encoding='utf-8', index=False)

    def get_more_information(self):
        """Получить дополнительную: статус ПВЗ."""
        # недоделан
    
        self.browser.get('https://www.wildberries.ru/services/besplatnaya-dostavka?desktop=1#terms-delivery')
        time.sleep(15)
        input_element = self.browser.find_element(By.CLASS_NAME, 'ymaps-2-1-79-searchbox-input__input')

        input_element.send_keys("Краснодарский край")
        input_element.send_keys(Keys.ENTER)
        time.sleep(20)
        main_page = self.browser.page_source
        soup = BeautifulSoup(main_page, 'html.parser')
        d = soup.find_all('div', class_='address-item')
        adress = [i.find('span', class_='address-item__name-text').text for i in d]
        type_point = [i.find('div', class_='address-item__type-text').text for i in d if i.find('div', class_='address-item__type-text')]
        ids = [i['data-id'] for i in soup.find_all(attrs={"data-id": True})][11:] # вырезать 11 первых
        res = zip(adress, type_point, ids)
        print(ids)
        return list(res)

    def get_all_id_and_to_file(self):
        """Получить id - ники всех точек и записать в файл."""

        try:
            response =  requests.get(self.main_url, headers=self.headers, timeout=10)
            list_ids = [str(i['id']) for i in response.json()[0]['items']]
            with open('ids_all.py', 'w') as f:
                f.write(','.join(list_ids))
            return True
    
        except Exception as e:
            return str(e)
    
    def get_comment_path(self):
        """Получить описание дороги к ПВЗ."""
    
        response = requests.post('https://www.wildberries.ru/webapi/poo/byids', headers=self.headers, json=datalist)
        csv_file = pd.read_csv(self.file_name, delimiter=',')
        new_data = [(key, i.get('wayInfo')) if i else (key,'') for key, i in response.json()["value"].items()]
       
        for key, value in new_data:
            if int(key) in csv_file['ID'].values:
                csv_file.loc[csv_file['ID'] == int(key), 'PATH'] = value
        
        csv_file.to_csv(self.file_name, encoding='utf-8', index=False) 


async def main():
    """Получить данные и записать в файл."""

    pt = Point()
    pt.get_main_data_by_points()
    await pt.data_to_csv()
    pt.sort_by_coord()



if __name__ == '__main__':
    # pt = Point()
    # pt.get_comment_path()
    # pt.get_more_information()
    # pt.sort_by_coord()
    # print(pt.get_more_information())
    # pt.sort_by_coord()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
