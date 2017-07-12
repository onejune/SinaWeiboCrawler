#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
微博内容抓取主程序
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

def get_account(filename):
    account_list = []
    f = open(filename)  
    username = ''
    pwd = ''
    for line in f:  
        arr = line.split('\t')
        username = arr[0]
        pwd = arr[1]
        url = arr[2]
        account_list.append((username, pwd, url))
    f.close()
    return account_list


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
            'http://weibo.com/u/2713968254',  #swaggyT-ao
            'http://weibo.com/p/1003061665256992/',
            'http://weibo.com/p/1003062060419113/',
            'http://weibo.com/p/1003062713968254/',  #swaggyT-ao
            'http://weibo.com/p/1004062706896955/',
            'http://weibo.com/p/1004061234692083/',
            'http://weibo.com/p/1003061506711913/',
            'http://weibo.com/p/1003061350995007/',
            'http://weibo.com/p/1005051788283193/',
            'http://weibo.com/p/1004061537790411/'
            #'http://weibo.com/p/1003061195230310/',
            #'http://weibo.com/p/1004061191220232/',
            #'http://weibo.com/p/1003061669879400/',
            #'http://weibo.com/p/1003061291477752/',
            #'http://weibo.com/p/1003061195230310/',
            #'http://weibo.com/p/1004061816618865/',
            #'http://weibo.com/u/1549364094'
            ]
    
    #load all bigV home url which crawled from baidu.
    all_user_url = load_all_url()
    print 'load', len(all_user_url), 'user urls.'
    logger.info('load ' + str(len(all_user_url)) + ' user urls.')
    #load all bigV uid.
    old_user_dict = load_all_user()
    new_user_list = []
    
    weiboCrawler = WeiboCrawler()
    filename = './config/account' 
    account_list = get_account(filename)
    if len(account_list) == 0:
        logger.error('account is null.')
        exit()
    print 'start running....'
    logger.info('start running.')
    for account in account_list:
        weiboLogin = WeiboLogin(account)
        if weiboLogin.Login() == False:
            continue

        #抓其他人的主页微博
        start_time = datetime.datetime.now()
        for home_url in all_user_url:
            user_name = all_user_url[home_url]
            uid = weiboCrawler.get_uid_by_url(home_url)
            if not uid:
                logger.error('get uid failed for ' + home_url)
                continue
            logger.info('start crawl:' + str(uid))
            print 'start crawl:' + str(uid)
            try:
                weibo_list = weiboCrawler.crawl_user_weibo(home_url)
                cmt_cnt = weiboCrawler.crawl_weibo_comment(weibo_list)
                weibo_cnt = len(weibo_list)
            except:
                traceback.print_exc()
                time.sleep(300)
            #save user uid
            if uid not in old_user_dict:
                weiboCrawler.save_user(weibo_cnt, cmt_cnt)
                old_user_dict[uid] = weiboCrawler.weibo_name
            
        end_time = datetime.datetime.now()
        waste = (end_time - start_time).seconds * 1.0 / 3600
        print 'crawl weibo over, spend', waste, 'hour.'
        logger.info('crawl weibo over, spend ' + str(waste) + 'hours.')

        break

        
    print 'crawl completely......'

    
    
    
