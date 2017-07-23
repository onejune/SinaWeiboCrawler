#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
从百度风云榜抓取热门用户
'''
import urllib2, time, datetime, sys, os, redis
import cookielib, traceback
from WeiboLogin import *
from login import *
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

redis_server = redis.Redis(host = '192.168.1.101', port = 6379, db = 0)

#今日热点人物
def crawl_hot_person():
    req_url_list = [
               'http://top.baidu.com/buzz?b=258&c=9&fr=topcategory_c9',
               'http://top.baidu.com/buzz?b=618&fr=topbuzz_b258_c9',
               'http://top.baidu.com/buzz?b=18&c=9&fr=topbuzz_b618',
               'http://top.baidu.com/buzz?b=17&c=9&fr=topbuzz_b18_c9',
               'http://top.baidu.com/buzz?b=16&c=9&fr=topbuzz_b1395_c9',
               'http://top.baidu.com/buzz?b=15&c=9&fr=topbuzz_b15_c9',
               'http://top.baidu.com/buzz?b=1396&c=9&fr=topbuzz_b15_c9',
               'http://top.baidu.com/buzz?b=260&c=9&fr=topbuzz_b1396_c9',
               'http://top.baidu.com/buzz?b=454&c=9&fr=topbuzz_b260_c9',
               'http://top.baidu.com/buzz?b=255&c=9&fr=topbuzz_b454_c9',
               'http://top.baidu.com/buzz?b=3&c=9&fr=topbuzz_b255_c9',
               'http://top.baidu.com/buzz?b=22&c=9&fr=topbuzz_b3_c9',
               'http://top.baidu.com/buzz?b=493&c=9&fr=topbuzz_b22_c9',
               'http://top.baidu.com/buzz?b=261&c=9&fr=topbuzz_b491_c9',
               'http://top.baidu.com/buzz?b=257&c=9&fr=topbuzz_b261_c9',
               'http://top.baidu.com/buzz?b=612&c=9&fr=topbuzz_b257_c9'
               ]
    hot_person = []
    for req_url in req_url_list:
        req = urllib2.Request(req_url)
        try:
            content = urllib2.urlopen(req, timeout = 30).read()
        except:
            print req_url
            traceback.print_exc()
            return hot_person
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
            return hot_person
    
        for tag in tags:
            people_name = tag.text.strip()
            if len(people_name) > 20:
                continue
            #print people_name
            logger.info(people_name)
            hot_person.append(people_name)
    hot_person = list(set(hot_person))
    logger.info('get ' + str(len(hot_person)) + ' hot person.')
    print 'crawl', len(hot_person), 'hot person from baidu.'
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
        fout.write(name[0] + '\t' + name[2] + '\t' + name[1] + '\t' + name[3] + '\t' + time_now + '\n')
    fout.close()


def get_uid_by_url(url):
    try:
        request = urllib2.Request(url) 
        response = urllib2.urlopen(request,timeout=500)
        content = response.read()
    except:
        return None
    #print content
    start = content.find('$CONFIG[\'page_id\']=')
  
    if start == -1:
        return None
    end = content.find('\'', start + 22)
    if end == -1:
        return None
    uid = content[start + 20 : end]
    return uid


def get_account():
    filename = './config/account' 
    account_list = []
    f = open(filename)  
    username = ''
    pwd = ''
    for line in f:  
        arr = line.split('\t')
        if len(arr) < 2:
            continue
        username = arr[0]
        pwd = arr[1]
        account_list.append((username, pwd))
    f.close()
    num = len(account_list)
    account_selected = random.randint(0, num-1)
    account = account_list[account_selected]
    return account


if __name__ == '__main__':
    old_user = load_all_user()
    weibo_user_list = []
    account = get_account()
    print 'start running....'
    print 'login with account:', account[0]
    weiboLogin = WeiboLogin(account)
    if weiboLogin.Login() == False:
        exit()
    person_list = crawl_hot_person()
    print 'crawl ' + str(len(person_list)) + ' users from baidu.'
    for name in person_list:
        try:
            weibo_name, weibo_home = weibo_search(name)
            uid = get_uid_by_url(weibo_home)
            if not uid or not weibo_home or not weibo_name:
                time.sleep(30)
                continue
            p = name + '\t' + weibo_name + '\t' + weibo_home
            redis_server.hset('big_v_uid', uid, p)
            p = uid + '\t' + weibo_name + '\t' + weibo_home
            redis_server.hset('big_v_name', name, p)
            print weibo_home, uid
            time.sleep(30)
            if not weibo_home or weibo_home in old_user:
                continue
        except:
            traceback.print_exc()
            time.sleep(180)
            continue
        weibo_user_list.append((name, weibo_home, weibo_name, uid))
        old_user[weibo_home] = weibo_name
        
    print 'crawl ' + str(len(weibo_user_list)) + ' users from weibo.'
    logger.info('crawl ' + str(len(weibo_user_list)) + ' users from weibo.')
    save_user_url(weibo_user_list)

    
    
