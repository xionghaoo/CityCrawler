# 抓取省、市、区数据

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


def output_to_file(filename, data_content):
    with codecs.open(filename, 'w') as f_obj:
        # 如果以utf8格式输出，ensure_ascii应该为True
        json.dump(data_content, f_obj, ensure_ascii=False)


headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

href_host = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019/'

page_format = 'gb18030'

r = requests.get('http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2017/index.html', headers=headers)
r.encoding = page_format
soup = BeautifulSoup(r.text, 'html.parser')

# print(soup.title)

# 省provincetr
# 市citytr
# 区countytr
province_list = soup.select('tr.provincetr > td > a')

data = []

for p in province_list:
    # 市
    city_request = requests.get(href_host + p['href'], headers=headers)
    city_request.encoding = page_format
    city_soup = BeautifulSoup(city_request.text.encode(city_request.encoding).decode(page_format), 'html.parser')
    city_list = city_soup.select('tr.citytr')
    city_data = {}
    city_data['cities'] = []
    for c in city_list:
        city_data['province_name'] = p.contents[0]

        city_html = c.contents
        # td > a > text
        try:
            city_html_number = city_html[0].contents[0].contents[0]
        except AttributeError:
            city_html_number = city_html[0].contents[0]

        try:
            tmp_city_html_name = city_html[1].contents[0].contents[0]
            city_href = city_html[1].contents[0]['href']
        except AttributeError:
            tmp_city_html_name = city_html[1].contents[0]

        # 将市辖区改成直辖市名称
        city_html_name = ''
        if tmp_city_html_name == '市辖区':
            city_html_name = p.contents[0][0:-1]
        else:
            city_html_name = tmp_city_html_name
        country_data = {}
        country_data['districts'] = []

        country_request = requests.get(href_host + city_href, headers=headers)
        country_request.encoding = page_format
        # print("country_request.encoding: " + country_request.encoding)
        if country_request.encoding is None:
            continue
        country_soup = BeautifulSoup(country_request.text.encode(country_request.encoding).decode(page_format), 'html.parser')
        country_list = country_soup.select('tr.countytr')
        for country in country_list:
            country_data['city_name'] = city_html_name
            country_data['city_code'] = city_html_number

            country_obj = {}
            country_tmp = country.contents
            try:
                country_html_number = country_tmp[0].contents[0].contents[0]
            except AttributeError:
                country_html_number = country_tmp[0].contents[0]
            try:
                country_html_name = country_tmp[1].contents[0].contents[0]
            except AttributeError:
                country_html_name = country_tmp[1].contents[0]
            country_obj['district_name'] = country_html_name
            country_obj['district_code'] = country_html_number
            country_data['districts'].append(country_obj)
        if not country_data['districts']:
            country_list = country_soup.select('tr.towntr')
            for country in country_list:
                country_data['city_name'] = city_html_name
                country_data['city_code'] = city_html_number

                country_obj = {}
                country_tmp = country.contents
                try:
                    country_html_number = country_tmp[0].contents[0].contents[0]
                except AttributeError:
                    country_html_number = country_tmp[0].contents[0]
                try:
                    country_html_name = country_tmp[1].contents[0].contents[0]
                except AttributeError:
                    country_html_name = country_tmp[1].contents[0]
                country_obj['district_name'] = country_html_name
                country_obj['district_code'] = country_html_number
                country_data['districts'].append(country_obj)
        city_data['cities'].append(country_data)
        print("已生成{0}{1}数据".format(city_data['province_name'], country_data['city_name']))
    # if (city_data['provinceName']):
    #     print("生成{}省份数据".format(city_data['provinceName']))
    #     output_to_file("json_file/province_{}.json".format(city_data['provinceName']), city_data)
    data.append(city_data)

# 手动添加的台湾和香港地区数据，如果不需要可以注释掉
taiwan = {}
taiwan['province_name'] = '台湾省'
taiwan['cities'] = []
t = {"city_name": "台北市", "city_code": "taiwan01"}
taiwan['cities'].append(t)
t = {"city_name": "新北市", "city_code": "taiwan02"}
taiwan['cities'].append(t)
t = {"city_name": "桃园市", "city_code": "taiwan03"}
taiwan['cities'].append(t)
t = {"city_name": "台中市", "city_code": "taiwan04"}
taiwan['cities'].append(t)
t = {"city_name": "台南市", "city_code": "taiwan05"}
taiwan['cities'].append(t)
t = {"city_name": "高雄市", "city_code": "taiwan06"}
taiwan['cities'].append(t)
data.append(taiwan)

hk = {}
hk['province_name'] = '香港'
hk['cities'] = []
t = {"city_name": "香港", "city_code": "hk01"}
hk['cities'].append(t)
data.append(hk)

aomen = {}
aomen['province_name'] = '澳门'
aomen['cities'] = []
t = {"city_name": "澳门", "city_code": "aomen01"}
aomen['cities'].append(t)
data.append(aomen)

output_to_file("json_file/china_area.json", data)






