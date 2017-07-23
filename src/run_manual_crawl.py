#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
手动挑选抓取失败的用户重新抓取
'''
import urllib2, time, datetime, sys, os
import cookielib, traceback
from WeiboLogin import *
from login import *
from WeiboCrawler import *
from get_weibo_page import *
from time import sleep
from log_util import *

time_now = time.strftime('%Y%m%d', time.localtime(time.time()))
lf='./log/logging_crawl_weibo_' + time_now + '.log'
logger = Logger(log_level=1, logger="main", log_file = lf).get_logger()

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


def init():
    sys_path = [
         './output/',
         './result/',
         './log/',
         './data/',
         './conf/'
         ]
    for p in sys_path:
        if not os.path.exists(p):
            os.makedirs(p)
    
def load_all_user():
    p = './output/weibo_user.dat'
    if not os.path.exists(p):
        return {}
    fin = open(p)
    user_dict = {}
    for line in fin:
        arr = line.split('\t')
        uid = arr[0].strip()
        home_url = arr[1].strip()
        weibo_name = arr[2].strip()
        user_dict[uid] = weibo_name
    fin.close()
    return user_dict

#加载所有微博用户的主页url
def load_all_url():
    if len(sys.argv) >= 2:
        p = sys.argv[1]
    else:
        p = './output/weibo_url.dat'
    if not os.path.exists(p):
        return {}
    fin = open(p)
    user_dict = {}
    for line in fin:
        arr = line.split('\t')
        home_url = arr[2].strip()
        name = arr[1].strip()
        weibo_name = arr[1].strip()
        user_dict[home_url] = name
    fin.close()
    return user_dict


if __name__ == "__main__":
    init()
    weibo_person_list = [
            'http://weibo.com/u/1288739185',
            'http://weibo.com/guojingming',
            'http://weibo.com/langxianpinghk',
            'http://weibo.com/zhangshaohan',
            'http://weibo.com/douxiao'
            ]
    
    #load all bigV home url which crawled from baidu.
    all_user_url = load_all_url()
    print 'load', len(all_user_url), 'user urls.'
    logger.info('load ' + str(len(all_user_url)) + ' user urls.')
    #load all bigV uid.
    old_user_dict = load_all_user()
    new_user_list = []
    
    weiboCrawler = WeiboCrawler()
    account = get_account()
    print 'start running....'
    logger.info('start running.')
    weiboLogin = WeiboLogin(account)
    if weiboLogin.Login() == False:
        exit()

    #抓其他人的主页微博
    start_time = datetime.datetime.now()
    w_cnt = 0
    c_cnt = 0
    for home_url in weibo_person_list:
        #user_name = all_user_url[home_url]
        uid = weiboCrawler.get_uid_by_url(home_url)
        if not uid:
            logger.error('get uid failed for ' + home_url)
            print 'get uid failed.'
            continue
        #if uid in old_user_dict:
        #    continue
        logger.info('start crawl:' + str(uid))
        print 'start crawl:' + str(uid)
        try:
            weibo_list = weiboCrawler.crawl_user_weibo(home_url)
            cmt_cnt = weiboCrawler.crawl_weibo_comment(weibo_list)
            weibo_cnt = len(weibo_list)
            w_cnt += weibo_cnt
            c_cnt += cmt_cnt
        except:
            traceback.print_exc()
            time.sleep(300)
            continue
        #save user uid
        if uid:
            weiboCrawler.save_user(weibo_cnt, cmt_cnt)
            old_user_dict[uid] = weiboCrawler.weibo_name
        
    end_time = datetime.datetime.now()
    waste = (end_time - start_time).seconds * 1.0 / 3600
    print 'crawl weibo over, spend', waste, 'hour.', 'crawled users:', len(all_user_url), 'all weibo count:', w_cnt, 'all comment count:', c_cnt
    logger.info('crawl weibo over, spend ' + str(waste) + 'hours.')

    print 'crawl completely......'

    
    
    
