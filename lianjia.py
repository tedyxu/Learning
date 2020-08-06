#!/usr/bin/env python
import requests
import urllib3
import re
import csv
urllib3.disable_warnings()
def get_page_num(price_low,price_high):
    #mw1是满五年，bt2是板楼，y4是20年以内，a3是70-90平，a4是90-110平，bp是价格下限，ep是价格上限
    url = 'https://sh.lianjia.com/ershoufang/mw1bt2y4a3a4bp' + price_low + 'ep' + price_high + '/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    req=requests.get(url,headers=headers,verify = False)
    req.encoding=req.apparent_encoding
    pattern=re.compile('<h2 class="total fl">共找到<span>(.*?)</span>套上海二手房</h2>',re.S)
    results=re.findall(pattern,req.text)
    page_num = int(results[0])//30+1
    return page_num

def get_single_urls(price_low,price_high):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    page_num = get_page_num(price_low,price_high)
    url_lists = []
    for i in range(0, page_num):
        i += 1
        # mw1是满五年，bt2是板楼，y4是20年以内，sf1是普通住宅，a3是70-90平，a4是90-110平，bp是价格下限，ep是价格上限
        url = 'https://sh.lianjia.com/ershoufang/pg' + str(i) + 'mw1bt2y4sf1a3a4bp' + price_low + 'ep' + price_high + '/'
        url_lists.append(url)
    urls = []
    for url in url_lists:
        req = requests.get(url,headers=headers,verify=False)
        req.encoding=req.apparent_encoding
        pattern = re.compile('<a class="" href="(.*?)" target="_blank"',re.S)
        results = re.findall(pattern,req.text)
        for result in results:
            urls.append(result)
    return urls

def get_single_info(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    req = requests.get(url,headers=headers,verify=False)
    req.encoding=req.apparent_encoding
    data_list = []
    #标题
    pattern_title = re.compile('<h1 class="main".*?>(.*?)</h1>')
    title = re.findall(pattern_title,req.text)
    data_list.append(title[0])
    #总价
    pattern_total_price = re.compile('<span class="total">(.*?)</span>')
    total_price = re.findall(pattern_total_price,req.text)
    data_list.append(total_price[0])
    #单价
    pattern_unit_price = re.compile('<div class="unitPrice"><span class="unitPriceValue">(.*?)<i>')
    unit_price = re.findall(pattern_unit_price,req.text)
    data_list.append(unit_price[0])
    #地区
    pattern_district = re.compile(
        '<span class="label">所在区域.*?target="_blank">(.*?)</a>.*?target="_blank">(.*?)</a>(.*?)</span>')
    districts = re.findall(pattern_district, req.text)
    for district in districts:
        data_list.append(district[0])
        data_list.append(district[1])
        data_list.append(re.sub('&nbsp;', '', district[2]))
    #小区名称
    pattern_xiaoqu = re.compile('<span class="label">小区名称</span><a.*?class="info ">(.*?)</a>')
    xiaoqu = re.findall(pattern_xiaoqu,req.text)
    data_list.append(xiaoqu[0])
    #面积、建筑年代
    pattern_area = re.compile('<div class="area"><div class="mainInfo">(.*?)平米</div><div class="subInfo">(.*?)年建.*?</div>')
    areas = re.findall(pattern_area, req.text)
    for area in areas:
        data_list.append(area[0])
        data_list.append(area[1])
    #挂牌时间
    pattern_date = re.compile('挂牌时间</span>.*?<span>(.*?)</span>',re.S)
    date = re.findall(pattern_date,req.text)
    data_list.append(date[0])
    #上次交易时间
    pattern_last_sale = re.compile('上次交易</span>.*?<span>(.*?)</span>',re.S)
    last_sale = re.findall(pattern_last_sale,req.text)
    data_list.append(last_sale[0])
    #房屋情况、楼层
    pattern_room = re.compile('<div class="room"><div class="mainInfo">(.*?)</div><div class="subInfo">(.*?)/共(.*?)层</div></div>')
    rooms = re.findall(pattern_room,req.text)
    for room in rooms:
        data_list.append(room[0])
        data_list.append(room[1])
        data_list.append(room[2])
    #朝向、户型结构、装修
    pattern_type = re.compile('<div class="type"><div class="mainInfo".*?>(.*?)</div><div class="subInfo">(.*?)/(.*?)</div>')
    types = re.findall(pattern_type,req.text)
    for type in types:
        data_list.append(type[0])
        data_list.append(type[1])
        data_list.append(type[2])
    #梯户比例、是否有电梯
    pattern_lift = re.compile('梯户比例</span>(.*?)</li>.*?配备电梯</span>(.*?)</li>',re.S)
    lifts = re.findall(pattern_lift,req.text)
    for lift in lifts:
        data_list.append(lift[0])
        data_list.append(lift[1])
    #交易权属
    pattern_quanshu = re.compile('交易权属</span>.*?<span>(.*?)</span>',re.S)
    quanshu = re.findall(pattern_quanshu,req.text)
    data_list.append(quanshu[0])
    data_list.append(url)
    return data_list

def main():
    #设置最低价和最高价
    price_low = input('请输入最低价：')
    price_high = input('请输入最高价')
    #获取所有房源的链接
    urls = get_single_urls(price_low,price_high)
    #文件名
    csv_file = 'lianjia.csv'
    #打开csv文件并写入标题行
    with open(csv_file, 'w', newline='', encoding='utf_8_sig') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['名称','总价（万）','单价（元/平方米）','区','地段','环线','小区名称','面积（平方米）','建筑年代','挂牌时间','上次交易时间','户型','楼层','楼层共计','朝向','结构','装修','梯户比例','电梯','交易权属','链接'])
        f.close()
    #一行行写入文件
    count = 1
    for url in urls:
        # 获取每一个link里的房源信息
        contents = get_single_info(url)
        #写入csv文件
        with open(csv_file, 'a', newline='',encoding='utf_8_sig') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(contents)
        print('\r已下载' + str(count) + '条房源信息,共计' + str(len(urls)) + '条房源信息，' + contents[0] + ' 写入成功')
        count+=1
    print('爬取完成，共计'+str(len(urls))+'条房源信息')

if __name__ == '__main__':
    main()
