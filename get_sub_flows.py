from urllib import request
from bs4 import BeautifulSoup as bs
from datetime_helper import str_to_date, get_yesterday_date

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


html = get_html(get_page_url(1))

d, flow = get_flow_from_html(html).split(',')

if get_yesterday_date() == str_to_date(d, "%Y.%m.%d"):
    with open(save_flows_file, 'a')as f:
        f.write("%s,%s\n" % (d, flow))

    flows = get_flows_from_file()
    flows = sorted(flows, key=lambda f: f[0])
    with open(sub_data_js_file, 'w')as f:
        f.write(get_cahrt_xy(flows))
