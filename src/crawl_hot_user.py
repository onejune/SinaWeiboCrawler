#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
从百度风云榜抓取热门用户
'''
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
from log_util import *

reload(__import__('sys')).setdefaultencoding('utf-8')

time_now = time.strftime('%Y%m%d', time.localtime(time.time()))
lf='./log/logging_crawl_user_' + time_now + '.log'
logger = Logger(log_level=1, logger="crawler", log_file = lf).get_logger()

#今日热点人物
def crawl_hot_person():
    req_url = 'http://top.baidu.com/buzz?b=258&c=9&fr=topcategory_c9'
    req = urllib2.Request(req_url)
    try:
        content = urllib2.urlopen(req, timeout = 10).read()
    except:
        traceback.print_exc()
        return None
    content = content.decode("gbk")
    div_str = content.replace('\t', '')
    div_str = div_str.replace('\r', '')
    div_str = div_str.replace('\n', '')
    content = div_str.replace('\\', '')
    #print content
    tags = BeautifulSoup(content).find_all('a', attrs={"class": "list-title"})
    if not tags:
        print 'get hot person failed.'
        logger.error('get hot person failed.')
        return None
    hot_person = []
    for tag in tags:
        people_name = tag.text.strip()
        if len(people_name) > 20:
            continue
        #print people_name
        logger.info(people_name)
        hot_person.append(people_name)
    logger.info('get ' + str(len(hot_person)) + ' hot person.')
    return hot_person

#根据名字搜索微博主页地址
def weibo_search(keyword):
    print 'search weibo homepage by name:', keyword

    req_url = 'http://s.weibo.com/weibo/%s' % (keyword)
    #print req_url
    req = urllib2.Request(req_url)
    try:
        content = urllib2.urlopen(req, timeout = 10).read().decode('unicode-escape')
    except:
        traceback.print_exc()
        return None, None
    div_str = content.replace('\t', '')
    div_str = div_str.replace('\r', '')
    div_str = div_str.replace('\n', '')
    content = div_str.replace('\\', '')
    #print content

    start = content.find('<div class="star_detail">')
    end = content.find('</div>', start)
    content = content[start : end + 6]
    #print start, end, content
    tag = BeautifulSoup(content).find(name = 'a', attrs = {'class':'name_txt'})
    if not tag:
        return None, None
    weibo_name = tag.text.strip()
    weibo_home = tag.get('href').split('?')[0].strip()
    print weibo_name, weibo_home
    
    return weibo_name, weibo_home


def load_all_user():
    p = './output/weibo_url.dat'
    if not os.path.exists(p):
        return {}
    fin = open(p)
    user_dict = {}
    for line in fin:
        arr = line.split('\t')
        home_url = arr[2].strip()
        name = arr[0].strip()
        weibo_name = arr[1].strip()
        user_dict[home_url] = name
    fin.close()
    return user_dict


def save_user_url(weibo_user_list):
    p = './output/weibo_url.dat'
    fout = open(p, 'a')
    time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for name in weibo_user_list:
        #name  weibo_name  home_url
        fout.write(name[0] + '\t' + name[2] + '\t' + name[1] + '\t' + time_now + '\n')
    fout.close()



if __name__ == '__main__':
    old_user = load_all_user()
    weibo_user_list = []

    person_list = crawl_hot_person()
    print 'crawl ' + str(len(person_list)) + ' users from baidu.'
    for name in person_list:
        try:
            weibo_name, weibo_home = weibo_search(name)
            time.sleep(60)
            if not weibo_home or weibo_home in old_user:
                continue
        except:
            traceback.print_exc()
            time.sleep(180)
            continue
        weibo_user_list.append((name, weibo_home, weibo_name))
        old_user[weibo_home] = weibo_name
        
    print 'crawl ' + str(len(weibo_user_list)) + ' users from weibo.'
    logger.info('crawl ' + str(len(weibo_user_list)) + ' users from weibo.')
    save_user_url(weibo_user_list)

    
    
