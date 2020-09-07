#!/usr/bin/env python
import requests
import urllib3
import re
import csv
urllib3.disable_warnings()
def get_page_num(price_low,price_high):
    #mw1是满五年，a3是70-90平，a4是90-110平，a5是110-130平，bp是价格下限，ep是价格上限,sf1是普通住宅
    url = 'https://sh.lianjia.com/chengjiao/mw1sf1a3a4a5bp' + price_low + 'ep' + price_high + '/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    req=requests.get(url,headers=headers,verify = False)
    req.encoding=req.apparent_encoding
    pattern=re.compile('<div class="total fl">共找到<span>(.*?)</span>套上海成交房源</div>',re.S)
    results=re.findall(pattern,req.text)
    page_num = int(results[0])//30+1
    return page_num
def get_single_urls(price_low,price_high):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    page_num = get_page_num(price_low,price_high)
    url_lists = []
    for i in range(0, page_num+1):
        i += 1
        # mw1是满五年，a3是70-90平，a4是90-110平，a5是110-130平，bp是价格下限，ep是价格上限,sf1是普通住宅
        url = 'https://sh.lianjia.com/chengjiao/pg' + str(i) + 'mw1sf1a3a4a5bp' + price_low + 'ep' + price_high + '/'
        url_lists.append(url)
    urls = []
    for url in url_lists:
        req = requests.get(url,headers=headers,verify=False)
        req.encoding=req.apparent_encoding
        pattern = re.compile('<div class="title"><a href="(.*?)" target="_blank">',re.S)
        results = re.findall(pattern,req.text)
        for result in results:
            urls.append(result)
    return urls
def get_single_info(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    req = requests.get(url,headers=headers,verify=False)
    req.encoding=req.apparent_encoding
    data_list = []
    #标题和成交时间
    pattern_title = re.compile('<div class="wrapper">(.*?) (.*?) (.*?)平米<span>(.*?) 成交</span>')
    titles = re.findall(pattern_title,req.text)
    for title in titles:
        data_list.append(title[0])
        data_list.append(title[1])
        data_list.append(title[2])
        data_list.append(title[3])
    #总价和单价
    pattern_price = re.compile('<div class="price"><span class="dealTotalPrice"><i>(.*?)</i>万</span><b>(.*?)</b>元/平</div>')
    prices = re.findall(pattern_price,req.text)
    for price in prices:
        data_list.append(price[0])
        data_list.append(price[1])
    #挂牌
    pattern_guapai = re.compile('<div class="msg"><span><label>(.*?)</label>.*?</span><span><label>(.*?)</label>.*?</span><span><label>(.*?)</label>.*?</span>')
    guapais = re.findall(pattern_guapai,req.text)
    for guapai in guapais:
        data_list.append(guapai[0])
        data_list.append(guapai[1])
        data_list.append(guapai[2])
    # 楼层
    pattern_floor = re.compile('<li><span class="label">所在楼层</span>(.*?)</li>')
    floor = re.findall(pattern_floor, req.text)
    data_list.append(floor[0].strip())
    # 建筑年代
    pattern_year = re.compile('<li><span class="label">建成年代</span>(.*?)</li>')
    year = re.findall(pattern_year, req.text)
    data_list.append(year[0])
    # 梯户比例
    pattern_room = re.compile('<li><span class="label">梯户比例</span>(.*?)</li>')
    room = re.findall(pattern_room, req.text)
    data_list.append(room[0].strip())
    data_list.append(url)
    return data_list
def main():
    #设置最低价和最高价
    price_low = input('请输入最低价：')
    price_high = input('请输入最高价：')
    #获取所有房源的链接
    urls = get_single_urls(price_low,price_high)
    #文件名
    csv_file = '链家二手房成交信息-'+price_low+'万至'+price_high+'万.csv'
    #打开csv文件并写入标题行
    with open(csv_file, 'w', newline='', encoding='utf_8_sig') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(['小区','房型','面积（平方米）','成交日期','总价（万元）','单价（元/平方）','挂牌价格（万元）','成交周期（天）','调价次数','楼层','建成年代','梯户比例','链接'])
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
    print('爬取完成，共计'+str(len(urls))+'条房源信息，已存入：'+csv_file)
if __name__ == '__main__':
    main()