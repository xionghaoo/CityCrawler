import requests
import json
import codecs
from bs4 import BeautifulSoup
import re


def crawler_country(c, country_list):
    country_data = {}
    country_data['countries'] = []
    for country in country_list:
        if not re.match('[\\d]+', country.contents[0]):
            country_data['cityName'] = c.contents[0]
            country_data['countries'].append(country.contents[0])
    return country_data


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

href_host = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/'

r = requests.get('http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html', headers=headers)
r.encoding = 'gb2312'
soup = BeautifulSoup(r.text, 'html.parser')

# print(soup.title)

# 省provincetr
# 市citytr
# 区countytr
province_list = soup.select('tr.provincetr > td > a')

data = {}
data['provinces'] = []

for p in province_list:
    # 市
    city_request = requests.get(href_host + p['href'], headers=headers)
    # city_request.encoding = 'gb2312'
    city_soup = BeautifulSoup(city_request.text.encode(city_request.encoding).decode('gbk'), 'html.parser')
    city_list = city_soup.select('tr.citytr > td > a')
    city_data = {}
    city_data['cities'] = []
    for c in city_list:
        if not re.match('[\\d]+', c.contents[0]):
            city_data['provinceName'] = p.contents[0]
            # 区
            country_request = requests.get(href_host + c['href'], headers=headers)
            # country_request.encoding = 'gb2312'
            country_soup = BeautifulSoup(country_request.text.encode(country_request.encoding).decode('gbk'), 'html.parser')
            country_list = country_soup.select('tr.countytr > td > a')

            country_data = {}
            country_data['countries'] = []
            for country in country_list:
                if not re.match('[\\d]+', country.contents[0]):
                    country_data['cityName'] = c.contents[0]
                    country_data['countries'].append(country.contents[0])
            if not country_data['countries']:
                country_list = country_soup.select('tr.towntr > td > a')
                for country in country_list:
                    if not re.match('[\\d]+', country.contents[0]):
                        country_data['cityName'] = c.contents[0]
                        country_data['countries'].append(country.contents[0])

            if not country_data['countries']:
                # 瀍河回族区
                print("has empty city data")
            print(country_data)
            city_data['cities'].append(country_data)
    data['provinces'].append(city_data)


with codecs.open('D:\\SVNRepo\\JZWealth\\app\\src\\main\\assets\\countries.json', 'w') as f_obj:
    json.dump(data, f_obj, ensure_ascii=True)




