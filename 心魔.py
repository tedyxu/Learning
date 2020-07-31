#!/usr/bin/env python
import requests
import re
import urllib3
#去除warning
urllib3.disable_warnings()

def get_single_content(url,headers):
    req = requests.get(url,headers=headers,verify=False)
    req.encoding = req.apparent_encoding
    pattern = re.compile('<h1>(.*?)</h1>.*?"content">(.*?)</div>',re.S)
    results = re.findall(pattern,req.text)
    for result in results:
        title = result[0]
        content = re.sub('<br/><br/>','\n\n', result[1]).strip()
        single_content = str(title + '\n\n' + content +'\n\n')
        return single_content

def main():
    header = {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'}
    mulu_url = 'http://www.xbiquge.la/10/10614/'
    req = requests.get(mulu_url, headers=header, verify=False)
    req.encoding = req.apparent_encoding
    pattern = re.compile('<dd><a href=\'(.*?)\' >(.*?)</a></dd>', re.S)
    results = re.findall(pattern, req.text)
    titles = []
    urls = []
    for result in results:
        url = 'http://www.xbiquge.la' + result[0]
        title = result[1]
        if '章' in title:
            titles.append(title)
            urls.append(url)
    count = 1
    first = True
    for title, url in zip(titles, urls):
        content = get_single_content(url, header)
        if first:
            first = False
            with open('心魔.txt', 'w+', encoding='utf-8') as f:
                f.write(content)
                f.close()
        else:
            with open('心魔.txt', 'a+', encoding='utf-8') as f:
                f.write(content)
                f.close()
        print(title+'\s写入成功')
        print('\r已下载' + str(count) + '章,共计' + str(len(titles)) + '章', end='')
        count +=1

if __name__ == '__main__':
    main()
