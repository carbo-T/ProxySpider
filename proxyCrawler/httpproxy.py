__author__ = 'changchang.cc'
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
# import urllib2
import urllib.request as urllib2
# import httplib
import http.client as httplib
import threading
import time as timer
import os, shutil
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
import importlib
import sys

importlib.reload(sys)

inFile = open('proxy.txt')
sampleFile = open('proxiesToUse.txt')
outFile = open('verified.txt', 'w')
lock = threading.Lock()


def getProxyList(targeturl="https://www.kuaidaili.com/ops/proxylist/", req=None, start=500,
                 length=20):  # http://www.xicidaili.com/nn/"):
    countNum = 0
    proxyFile = open('proxy.txt', 'a')

    # "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
    # "(KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"
    requestHeader = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    # page numbers
    for page in range(start, start + length):
        url = targeturl + str(page)
        print(url)
        if req is None:
            request = urllib2.Request(url, headers=requestHeader)
            try:
                html_doc = urllib2.urlopen(request).read()
            except:
                html_doc = urllib2.urlopen(request).read()
        else:
            html_doc = req.read()

        soup = BeautifulSoup(html_doc, "html.parser")
        print(soup)
        # kuaidaili
        # trs = soup.find('div', id='list').find('table').find('tbody').find_all('tr')

        # xici
        trs = soup.find('table', id='ip_list').find_all('tr')

        # xici
        for tr in trs[1:]:
            tds = tr.find_all('td')
            # 国家
            if tds[1].find('img') is None:
                nation = '未知'
                locate = '未知'
            else:
                nation = tds[1].find('img')['alt'].strip()
                locate = tds[4].text.strip()
            ip = tds[2].text.strip()
            port = tds[3].text.strip()
            anony = tds[5].text.strip()
            protocol = tds[6].text.strip()
            speed = tds[7].find('div')['title'].strip()
            time = tds[9].text.strip()
            proxyFile.write('%s|%s|%s|%s|%s|%s|%s|%s\n' % (nation, ip, port, locate, anony, protocol, speed, time))

            # kuaidaili
            # for tr in trs[0:]:
            #     tds = tr.find_all('td')
            #     # 国家
            #     if tds[4].text is None:
            #         nation = '未知'
            #         # locate = '未知'
            #     else:
            #         nation = tds[4].text.strip()
            #         # locate = tds[4].text.strip()
            #     ip = tds[0].text.strip()
            #     port = tds[1].text.strip()
            #     anony = tds[2].text.strip()
            #     protocol = tds[3].text.strip()
            #     speed = tds[5].text.strip()
            #     time = tds[6].text.strip()

            # proxyFile.write('%s|%s|%s|%s|%s|%s|%s\n' % (nation, ip, port, anony, protocol, speed, time))
            # print('%s|%s|%s|%s|%s|%s|%s\n' % (nation, ip, port, anony, protocol, speed, time))
            print('%s=%s:%s' % (protocol, ip, port))
            countNum += 1
        print(page)
        if (page + 1) % 10 == 0:
            timer.sleep(10)
        else:
            timer.sleep(0.5)

    proxyFile.close()
    return countNum


def verifyProxyList():
    # '''
    # 验证代理的有效性
    # '''
    requestHeader = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    myurl = 'http://www.baidu.com/'
    while True:
        lock.acquire()
        ll = inFile.readline().strip()
        lock.release()
        if len(ll) == 0:
            break
        line = ll.strip().split('|')
        protocol = line[4]
        ip = line[1]
        port = line[2]

        try:
            conn = httplib.HTTPConnection(ip, port, timeout=10.0)
            conn.request(method='GET', url=myurl, headers=requestHeader)
            res = conn.getresponse()
            lock.acquire()
            print("+++Success:" + ip + ":" + port)
            outFile.write(ll + "\n")
            lock.release()
        except:
            print("---Failure:" + ip + ":" + port)


def getProxyListWithMultiProxy(myurl="", start=600, length=20):
    requestHeader = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    # print(myurl, str(start), str(length))
    if myurl == "":
        myurl = "http://www.xicidaili.com/nn/"
    lock.acquire()
    ll = sampleFile.readline().strip()
    lock.release()
    if len(ll) == 0:
        return
    line = ll.strip().split('|')
    protocol = line[4]
    ip = line[1]
    port = line[2]
    for j in range(start, start + length, 1):
        try:
            proxy_support = urllib2.ProxyHandler({protocol: ip + ":" + port})
            opener = urllib2.build_opener(proxy_support)
            opener.addheaders = [('User-Agent', "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                                                "(KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36")]
            print(myurl + str(i))
            res = opener.open(myurl + str(j))
            print(res)
            getProxyList(req=res, start=start, length=length)
        except Exception as e:
            print(e)


def mycopyfile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!" % srcfile)
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if os.path.exists(dstfile):
            os.remove(dstfile)
        if fpath is not None and fpath != "" and not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.copy2(srcfile, dstfile)  # 复制文件
        print("copy %s -> %s" % (srcfile, dstfile))


if __name__ == '__main__':
    # tmp = open('proxy.txt', 'w')
    # tmp.write("")
    # tmp.close()
    # proxynum = getProxyList("http://www.xicidaili.com/nn/")
    # print(u"国内高匿：" + str(proxynum))
    # proxynum = getProxyList("http://www.xicidaili.com/nt/")
    # print(u"国内透明：" + str(proxynum))
    # proxynum = getProxyList("http://www.xicidaili.com/wn/")
    # print(u"国外高匿：" + str(proxynum))
    # proxynum = getProxyList("http://www.xicidaili.com/wt/")
    # print(u"国外透明：" + str(proxynum))

    # proxynum = getProxyList("https://www.kuaidaili.com/free/inha/")
    # print(u"国内高匿：" + str(proxynum))
    # proxynum = getProxyList("https://www.kuaidaili.com/free/intr/")
    # print(u"国内普通：" + str(proxynum))

    print(u"\n验证代理的有效性：")
    all_thread = []
    # concurrent threads
    for i in range(100):
        t = threading.Thread(target=verifyProxyList)
        all_thread.append(t)
        t.start()

    # # swiftly get all proxies that you want
    # for i in range(10):
    #     t = threading.Thread(target=getProxyListWithMultiProxy,
    #                          args=("http://www.xicidaili.com/nn/", 1 + i * 50, 500 + i * 50))
    #     all_thread.append(t)
    #     t.start()
    # for i in range(10):
    #     t = threading.Thread(target=getProxyListWithMultiProxy,
    #                          args=("http://www.xicidaili.com/nt/", 1 + i * 50, 500 + i * 50))
    #     all_thread.append(t)
    #     t.start()
    # for i in range(10):
    #     t = threading.Thread(target=getProxyListWithMultiProxy,
    #                          args=("http://www.xicidaili.com/wn/", 1 + i * 50, 500 + i * 50))
    #     all_thread.append(t)
    #     t.start()
    # for i in range(10):
    #     t = threading.Thread(target=getProxyListWithMultiProxy,
    #                          args=("http://www.xicidaili.com/wt/", 1 + i * 50, 500 + i * 50))
    #     all_thread.append(t)
    #     t.start()

    for t in all_thread:
        t.join()
    outFile.close()
    # after validation, backup ips
    mycopyfile('verified.txt', 'usableProxies.txt')

    inFile.close()

    sampleFile.close()
    print("All Done.")
