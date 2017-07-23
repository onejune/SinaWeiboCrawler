#coding=utf-8
import sys, os
import urllib
import urllib2
import cookielib
import base64
import re, time, datetime, json
import hashlib,random
from StringIO import StringIO
import gzip, traceback
from bs4 import BeautifulSoup
from bs4 import NavigableString
import const
import ConfigParser
import os, sys, json, time, datetime

def read_config():
    cf = ConfigParser.ConfigParser()
    cf.read("config/const_file.ini")
    
    section="redis"
    
    key="HOST"
    value=cf.get(section,key)
    setattr(const,key,value)

    key="PORT"
    value=cf.getint(section,key)
    setattr(const,key,value)


def downLoadPage(charset, req_url):  
    if req_url == '':
        return
    enable_proxy = True
    proxy_file = "config/proxy.txt" 
    proxy_file = open(proxy_file, "r")
    proxy_list = LoadProxy(proxy_file)
    proxy_num = len(proxy_list)
    
    proxy_selected = random.randint(0, proxy_num-1)
    proxy_this = proxy_list[proxy_selected]
    print proxy_this
    proxy_handler = urllib2.ProxyHandler({'http':'http://' + proxy_this})
    null_proxy_handler = urllib2.ProxyHandler({})
    if enable_proxy:
        opener = urllib2.build_opener(proxy_handler)
    else:
        opener = urllib2.build_opener(null_proxy_handler)
    urllib2.install_opener(opener)
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}
    
    request = urllib2.Request(req_url, headers = header)

    timeoutsecond = 30
    data = ''
    try:
        data = urllib2.urlopen(request, timeout = timeoutsecond).read()
    except:
        traceback.print_exc()
    print data
    return data


def LoadProxy(file):
    proxyList = []
    for line in file:
        line = line.strip()
        proxyList.append(line)
    return proxyList


