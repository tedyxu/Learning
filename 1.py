import requests
import json
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import urllib3
import pandas as pd
import re
import datetime
#去除warning
urllib3.disable_warnings()

def get_report_numbers(start_date,to_date):
    # 披露易搜索网站的求情头
    header = {"origin": 'https://www.hkexnews.hk',
              "referer": 'https://www.hkexnews.hk/index_c.htm',
              "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
              }
    # 搜索的数据，中文，现有上市证券，标题类别，环境社会及管治报告，时间范围
    data = {"lang": 'ZH',
            "market": 'SEHK',
            "searchType": '1',
            "documentType": '',
            "t1code": '40000',
            "t2Gcode": '-2',
            "t2code": '40400',
            "stockId": '',
            "from": start_date,
            "to": to_date,
            "category": '0',
            "title": ''
            }
    #搜索网址
    hkexnews_search = 'https://www1.hkexnews.hk/search/titlesearch.xhtml'
    #获取网页信息
    req = requests.post(hkexnews_search,data=data,headers=header,verify = False).text
    pattern = re.compile('container-Mobile">.*?(\d+).*?(\d+).*?</div></div>',re.S)
    results = re.findall(pattern,req)
    for result in results:
        return result[1]
def get_info(from_date):
    origin_url = 'https://www1.hkexnews.hk/search/titleSearchServlet.do?'
    post_data = {'sortDir':'0',
               'sortByOptions':'DateTime',
               'category':'0',
                'market':'SEHK',
                'stockId':'-1',
                'documentType':'-1',
                'fromDate':from_date,
                'toDate':current_data_str,
                'title':'',
                'searchType':'1',
                't1code':'40000',
                't2Gcode':'-2',
                't2code':'40400',
                'rowRange':report_numbers,
                'lang':'zh'}
    total_url = origin_url + urlencode(post_data)
    req = requests.get(total_url,verify = False)
    soup = BeautifulSoup(req.text,'lxml')
    json_data = json.loads(json.loads(soup.text)['result'])
    return json_data
def get_dataframe():
    date_time =[]
    stock_code = []
    stock_name = []
    doc_name = []
    doc_link = []
    for items in get_info(from_date_str):
        date_time.append(items[u'DATE_TIME'])
        stock_code.append(items[u'STOCK_CODE'].split("<br/>",1)[0])
        stock_name.append(items[u'STOCK_NAME'].split("<br/>",1)[0])
        doc_name.append(re.sub('\n','',items[u'TITLE']))
        doc_link.append('https://www1.hkexnews.hk/' + items[u'FILE_LINK'])
    df = pd.DataFrame({'披露时间':date_time,'股票代码':stock_code,'股票简称':stock_name,'报告名称':doc_name,'报告链接':doc_link})
    df['披露时间'] = pd.to_datetime(df['披露时间'],format="%d/%m/%Y %H:%M")
    df_sort = df.sort_values(by=['披露时间'],ascending=True)
    return df_sort

if __name__ == '__main__':
    # 当年年份，起始查询日期为当年1月1日
    from_date = datetime.datetime.now()
    from_year = from_date.strftime('%Y')
    from_date_str = from_year + '0101'
    # 程序运行时当天日期，查询至当前日期
    current_data = datetime.datetime.now()
    current_data_str = current_data.strftime('%Y%m%d')
    table_name = from_year + '年香港上市公司ESG报告.csv'
    report_numbers = get_report_numbers(from_date_str, current_data_str)
    get_dataframe().to_csv(table_name, index=False, encoding='utf_8_sig')
    print(from_year+'年至目前共计'+report_numbers+'份ESG报告，已保存至文件：'+table_name)


