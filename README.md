# CityCrawler
> 抓取国家统计局的地址信息，生成json文档

[国家统计局 - 关于更新全国统计用区划代码和城乡划分代码的公告](http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2019/index.html)

### 环境
python3

### crawler.py
单独抓取各个维度的数据：

1. 只抓取省份 生成单独的json文件
2. 只抓取城市和区域 生成单独json文件

### crawler_city.py
抓取国家统计局 省、市区 二级数据数据生成json文件

### crawler_district.py
抓取国家统计局 省、市区、区域 三级数据生成json文件

### 运行方式

在根目录执行：
```shell
% python3 crawler_district.py 
```