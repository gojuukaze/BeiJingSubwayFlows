# BeiJingSubwayFlows
北京地铁客流量统计（py爬虫+js统计图） 

---
<img src="https://github.com/gojuukaze/BeiJingSubwayFlows/blob/master//tu.png?raw=true">

# 结果：
https://www.ikaze.cn/sub_flows.html  

# 其他：
* 使用python3爬数据，echart统计图  
* 爬虫的结果直接存到了文件中，因为项目比较小，就不用数据库了  
* 爬虫脚本只是爬昨天的数据的，需要所有的要改一下`get_flow_from_html()`函数
```python
def get_flow_from_html(html):

    # 需要根据页数调整年份
    year = 2018

    soup = bs(html, 'html.parser')
    work_list = soup.find_all('div', class_='work_list')
    data = work_list[0].find_all('li')
    for d in data:
        s = data.get_text()
        ...
```

然后直接循环跑就行：
```python
page=200
while page>0:
    html = get_html(get_page_url(page))
    get_flow_from_html(html)
    ...
```

