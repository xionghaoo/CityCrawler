
# 灵活抓取各维度数据，2019年的地区数据
# 网页格式使用gb18030

import requests
import json
import codecs
from bs4 import BeautifulSoup
import re
import os


class ProvinceResult:
    def __init__(self, province_html_node, province_code):
        self.province_html_node = province_html_node
        self.province_code = province_code


page_format = 'gb18030'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}
url = "http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019/"

root_path = "json_file"


def output_to_file(filename, data_content):
    print("创建文件{}".format(filename))
    with codecs.open(filename, 'w') as f_obj:
        # 如果以utf8格式输出，ensure_ascii应该为True
        json.dump(data_content, f_obj, ensure_ascii=False)


# 抓取所有省份
def crawl_province():
    r = requests.get(url, headers=headers)
    r.encoding = page_format
    soup = BeautifulSoup(r.text, 'html.parser')
    province_list = soup.select('tr.provincetr > td > a')

    result = []
    province_data = {'provinces': []}
    index = 0
    for p in province_list:
        index += 1
        province_data['provinces'].append({
            'name': p.contents[0],
            'code': index
        })
        result.append(ProvinceResult(p, index))
    output_to_file("{}/province_list.json".format(root_path), province_data)
    return result


# 根据省份抓取城市
def crawl_city(p, province_code):
    folder = r"{0}/{1}".format(root_path, province_code)
    if not os.path.exists(folder):
        os.mkdir(folder)
    city_request = requests.get(url + p['href'], headers=headers)
    city_request.encoding = page_format
    city_soup = BeautifulSoup(city_request.text, 'html.parser')
    city_list = city_soup.select('tr.citytr')
    city_data = {'cities': []}
    for c in city_list:
        city_html = c.contents
        try:
            city_html_number = city_html[0].contents[0].contents[0]
        except AttributeError:
            city_html_number = city_html[0].contents[0]

        city_href = None
        try:
            tmp_city_html_name = city_html[1].contents[0].contents[0]
            city_href = city_html[1].contents[0]['href']
        except AttributeError:
            tmp_city_html_name = city_html[1].contents[0]

        # 将市辖区改成直辖市名称
        if tmp_city_html_name == '市辖区':
            city_html_name = p.contents[0][0:-1]
        else:
            city_html_name = tmp_city_html_name
        city_data['cities'].append({'city_name': city_html_name, 'city_code': city_html_number})
        # 生成市区路径
        if city_href:
            # 抓取当前城市的地区数据
            crawl_district(folder, city_href, city_html_name, city_html_number)
    output_to_file("{0}/{1}".format(folder, "city_list.json"), city_data)


# 根据城市抓取地区
def crawl_district(parent_path, city_href, city_name, city_code):
    folder = r"{0}/{1}".format(parent_path, city_code)
    # list_file = r"{0}/{1}".format(folder, "district_list.json")
    # if os.path.exists(list_file):
    #     return
    if not os.path.exists(folder):
        os.mkdir(folder)
    district_request = requests.get(url + city_href, headers=headers)
    district_request.encoding = page_format
    district_soup = BeautifulSoup(district_request.text, 'html.parser')
    district_list = district_soup.select('tr.countytr')

    district_data = {
        'districts': [],
        'city_name': city_name,
        'city_code': city_code
    }
    for d in district_list:
        district_tmp = d.contents
        try:
            district_html_code = district_tmp[0].contents[0].contents[0]
        except AttributeError:
            district_html_code = district_tmp[0].contents[0]
        try:
            district_html_name = district_tmp[1].contents[0].contents[0]
        except AttributeError:
            district_html_name = district_tmp[1].contents[0]
        district_obj = {
            'district_name': district_html_name,
            'district_code': district_html_code
        }
        district_data['districts'].append(district_obj)
    if not district_data['districts']:
        district_list = district_soup.select('tr.towntr')
        for d in district_list:
            district_tmp = d.contents
            try:
                district_html_code = district_tmp[0].contents[0].contents[0]
            except AttributeError:
                district_html_code = district_tmp[0].contents[0]
            try:
                district_html_name = district_tmp[1].contents[0].contents[0]
            except AttributeError:
                district_html_name = district_tmp[1].contents[0]
            district_obj = {
                'district_name': district_html_name,
                'district_code': district_html_code
            }
            district_data['districts'].append(district_obj)
    output_to_file("{0}/{1}".format(folder, "district_list.json"), district_data)


# 只抓取省份列表
p_list = crawl_province()

# 分别抓取各省的城市和地区数据，注意：需要先抓取省份列表才能抓取城市列表
# for p in p_list:
#     crawl_city(p.province_html_node, p.province_code)
