#! /usr/bin/env python
import requests
from bs4 import BeautifulSoup
import os
import time
import random
import re
import urllib3
#去除warning
urllib3.disable_warnings()
target = 'https://www.kyks.cc/0/59157/26752561.html'
#基础信息
urls = []
title = []
content_url = "https://www.kyks.cc/59/59157/"
content_url2 = "https://www.kyks.cc"
header = {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
          'Referer':'https://www.kyks.cc/'
          }  # 表示是一个浏览器
location = r'/usr/novel/'
book_name = '1.txt'  # 设置一个Default书名（虽然在后来肯定是会找到一个名字的）
count = 0
try:
    req = requests.get(content_url, headers=header, verify=False)  # 表示自己是一个浏览器
    req.raise_for_status()  # 如果有问题就会raise一个问题
    req.encoding = req.apparent_encoding  # 根据网页返回的编码 进行调整
    bf = BeautifulSoup(req.text, 'html.parser')
        #目录内容
    content_list = bf.find('ul',class_='list-group list-charts')
    chapter_list = content_list.find_all('li')
    #书名
    meta = bf.find('head').find(attrs={'property':"og:novel:book_name"})
    book_name=meta['content']+'.txt'
    for chapter in chapter_list:  # 整合得到所有跟内容有关的链接（会有哪些跟内容无关的章节的）
        if '章' in chapter.find('a').text:
            title.append(chapter.find('a').text)
            urls.append(content_url2 + chapter.find('a')['href'])
    first = True
    for i, url in enumerate(urls):
        r = requests.get(url, headers=header, verify=False)
        r.encoding = 'gbk'
        r.raise_for_status()
        bf_single = BeautifulSoup(r.text, 'html.parser')
        # 获取标题
        chapter_name = bf_single.find(attrs={"class": "panel-heading"})
        chapter_name_clean = re.sub(r'\n+', '', re.sub(r'\s', '', re.sub(r'<[^<]+?>', '', str(chapter_name))))
        # 获取正文
        content = bf_single.find(attrs={"class": "panel-body content-body content-ext"})
        content_clean = re.sub(r'\s+', '\n\n', re.sub(r'<[^<]+?>', '', str(content)))
        # 合并标题正文
        single_total = chapter_name_clean + '\n\n' + content_clean + '\n\n'
        if not os.path.exists(location):
            os.mkdir(location)  # 如果没有这个文件夹，就会创建一个
        if first:  # 如果是第一次写入的话，会将原来的内容清空，然后再写入
            first = False
            with open(location + book_name, 'w') as f:
                f.write(single_total)
                f.close()
        else:  # 反之，则直接在文章末尾处添加
            with open(location + book_name, 'a') as f:
                f.write(single_total)
                f.close()
        print(title[i],' 写入成功')
except:
    pass
