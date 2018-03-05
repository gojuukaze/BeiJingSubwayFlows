import requests
import re
from urllib import request
from bs4 import BeautifulSoup as bs
from datetime_helper import get_yesterday_date,datetime_to_str,str_to_date

save_flows_file = 'sub_flows.txt'
sub_data_js_file = 'sub_data.js'


def get_page_url(page):
    base_url = 'https://www.bjsubway.com/support/cxyd/klxx/index'
    if page == 1:
        return base_url + ".html"
    else:
        return base_url + "_" + str(page) + ".html"


def get_html(url):
    resp = request.urlopen(url)
    html_data = resp.read()
    return html_data

def get_flow_from_html(html):
    year = 2018

    soup = bs(html, 'html.parser')
    
    work_list = soup.find_all('div', class_='work_list')    
    data = work_list[0].find_all('li')

    s = data[0].get_text()
    try:
        m_pos = s.find('月')
        m = s[0:m_pos]
        d_pos = s.find('日')
        d = s[m_pos + 1:d_pos]

        f_start = s.find('运量为') + 3
        f_end = s.find('万人次')
        flow = s[f_start:f_end]

        return "%s.%s.%s,%s" % (year, m, d, flow)
    except:
        print("error: %s" % (s))
        return None


def get_html_from_sina():
    url='https://weibo.com/p/1008088aa1b647b52515da3acfee8879bd747e'
    headers={
        'Host':'weibo.com',
        'Connection':'keep-alive',
        'Cache-Control':'max-age=0',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36 QQBrowser/4.3.4986.400',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer':'http://s.weibo.com/weibo/%25E5%25AE%25A2%25E6%25B5%2581%25E8%25A7%2582%25E5%25AF%259F&Refer=index',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.8',
    }
    cookies={
        'SUB':'_2AkMtL0HNf8NxqwJRmPAcymPqZIV0zgnEieKbc7AWJRMxHRl-yT9kql06tRB6Bq9vIptsi0itG6AEcsGYeVX0F0WoBgob',
        'SUBP':'0033WrSXqPxfM72-Ws9jqgMF55529P9D9WWldK7b-QoN.la7Gp5smllK',
        'SINAGLOBAL':'3163792802659.2153.1517539069473',
        'YF-V5-G0':'cd5d86283b86b0d506628aedd6f8896e',
        '_s_tentry':'www.baidu.com',
        'UOR':',,www.baidu.com',
        'Apache':'4557240479899.627.1520217434514',
        'ULV':'1520217434521:6:2:1:4557240479899.627.1520217434514:1519971759990',
        'YF-Page-G0':'f70469e0b5607cacf38b47457e34254f'
    }

    r = requests.get(url,headers=headers,cookies=cookies)
    return r.content

def get_flow_from_sina_html(html):
    """
    新浪搜索出来的数据是通过script展示的，所以只能直接从script里爬数据，
    幸运的是script里直接就是html，可以直接解析
    """
    year=2018

    soup = bs(html, 'html.parser')
    scripts=soup.find_all('script')
    # data 数据所在的列表
    data=[]
    for s in scripts[-1:]:
        temp=s.text
        # 带有数据的那个标签是FM.view开头的
        if temp.startswith('FM.view'):
            temp=temp[8:-1]
            # 到这一步时，temp是这样的 ‘{"domid":"xx","css":["style/xx"],"html"="<div>..."}’
            try:
                temp=eval(temp)
            except :
                # 这里出错说明不是需要的那个标签
                continue
            if 'html' in temp:
                new_html=temp['html']
                new_html=new_html.replace('\/','/')
            else:
                continue
            new_soup=bs(new_html, 'html.parser')
            flows_div = new_soup.find_all('div', class_='WB_feed WB_feed_v3 WB_feed_v4')
            if flows_div:
                data=flows_div[0].find_all('div',class_='WB_feed_detail clearfix')
                if data:
                    break
   
    yesterday=get_yesterday_date()
    for d in data:
        from_name=d.find('div',class_='WB_info').find('a').get_text().strip()
        if from_name!="北京地铁":
            continue 
        content=d.find('div',class_='WB_text W_f14').get_text().strip()
        content=re.compile(r'#.*?#').sub('',content)
        content=re.compile(r'【.*?】').sub('',content)

        try:
            m_end = content.find('月')
            if m_end==1:
                m_start=0
            else:
                m_start=m_end-2

            month = content[m_start:m_end]
            month=re.findall("\d+",month)[0]

            d_end = content.find('日')
            day = content[m_end + 1:d_end]

            f_start = content.find('运量为') + 3
            f_end = content.find('万人次')
            flow = content[f_start:f_end]

            if month==str(yesterday.month) and day==str(yesterday.day):
                return "%s.%s.%s,%s" % (year, month, day, flow)
        except:
            print("error: %s" % (s))
    return None
            



def get_flows_from_file():
    with open(save_flows_file, 'r')as f:
        flows = f.readlines()
    temp = []
    for f in flows:
        f = f.split(',')
        d = str_to_date(f[0], '%Y.%m.%d')

        temp.append([d, float(f[1])])
    return temp


def get_cahrt_xy(flows):
    x = []
    y = []
    for f in flows:
        x.append("%s-%s-%s" % (f[0].year, f[0].month, f[0].day))
        y.append(f[1])

    s = "BASEX=%s;\nBASEY =%s;" % (x, y)

    return s


# html = get_html(get_page_url(1))
# d, flow = get_flow_from_html(html).split(',')

html=get_html_from_sina()
d, flow = get_flow_from_sina_html(html).split(',')
if get_yesterday_date() == str_to_date(d, "%Y.%m.%d"):
    with open(save_flows_file, 'a')as f:
        f.write("%s,%s\n" % (d, flow))

    flows = get_flows_from_file()
    flows = sorted(flows, key=lambda f: f[0])
    with open(sub_data_js_file, 'w')as f:
        f.write(get_cahrt_xy(flows))
