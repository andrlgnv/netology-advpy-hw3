import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import time
import json
from pprint import pprint

HOST = 'https://hh.ru/search/vacancy?text=python&area=1&area=2&page=0&hhtmFrom=vacancy_search_list'


def get_headers():
    return Headers(browser='firefox', os='win').generate()


# получаем количество страниц
resp = requests.get(url=HOST, headers=get_headers()).text
soup1 = BeautifulSoup(resp, 'lxml')
page_count = soup1.find('div', attrs={'class': 'pager'}).find_all('span', recursive=False)[-1].find('a').find(
    'span').text


def get_data():
    job_info = []
    # цикл по каждой странице
    for page in range(int(page_count)):
        url = 'https://hh.ru/search/vacancy?text=python&area=1&area=2&page={page}'
        response = requests.get(url, headers=get_headers()).text
        soup = BeautifulSoup(response, 'lxml')
        #
        job_data = soup.find_all(class_='serp-item')
        # итерация по каждой вакансии на странице
        for job in job_data:
            job_body = job.find('div', class_='vacancy-serp-item-body')
            job_link = job_body.find('a', class_='serp-item__title')['href'].split('?')[0]

            try:
                salary = job_body.find('span', class_='bloko-header-section-3').text.strip().replace('\u202f000', '000')
            except:
                salary = 'Зарплата не указана'

            company_name = job_body.find('a', class_='bloko-link bloko-link_kind-tertiary').text.replace('\xa0', ' ')

            city = \
                list(job_body.find('div', attrs={'class': 'bloko-text', 'data-qa': 'vacancy-serp__vacancy-address'}))[0]

            # по ссылке открывается вакансия, оттуда берется описание вакансии для поиска по ключевым словам
            job_html = requests.get(job_link, headers=get_headers()).text
            html_body = BeautifulSoup(job_html, 'lxml')
            try:
                descr = html_body.find('div', attrs={'class': 'g-user-content', 'data-qa': 'vacancy-description'}).text
            except AttributeError:
                descr = html_body.find('div', attrs={'class': 'vacancy-branded-user-content', 'data-qa': 'vacancy'
                                                                                                         '-description'}).text
            if 'django' in descr.lower() and 'flask' in descr.lower():
                job_info.append(
                    {
                        'link': job_link,
                        'company_name': company_name,
                        'city': city,
                        'salary': salary
                    }
                )
        time.sleep(1)
        print(f'Обработано страниц {page + 1}/{page_count}')

    # запись полученного списка в файл
    with open('hh-scrapping.json', 'w', encoding='utf-8') as file:
        json.dump(job_info, file, indent=4, ensure_ascii=False)


def main():
    get_data()


if __name__ == '__main__':
    main()
