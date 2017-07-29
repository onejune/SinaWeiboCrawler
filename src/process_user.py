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

redis_local = redis.Redis(host = '192.168.1.102', port = 6379, db = 0)
redis_server = redis.Redis(host='112.126.67.205', port=6380, db=1, password='wanjun@1#7%sider')

if __name__ == '__main__':
    all_uid_dict= redis_local.hgetall('big_v_uid')
    crawl_cnt = redis_local.hgetall('crawl_cnt_uid')
    for uid in all_uid_dict:
        info = all_uid_dict[uid]
        record = crawl_cnt.get(uid)
        try:
            name, nick, url = info.split('\t')
        except:
            continue
        redis_server.hset('big_v_uid', uid, info)
        info2 = uid + '\t' + nick + '\t' + url
        redis_server.hset('big_v_name', name, info2)
        print info
        print info2
        if record == None:
            continue
        redis_server.hset('crawl_cnt_uid', uid, record)
    
        
    
