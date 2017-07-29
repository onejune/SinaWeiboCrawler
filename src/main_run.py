#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
微博内容抓取主程序
'''
import urllib2, time, datetime, sys, os, redis, random, types
import cookielib, traceback
#from WeiboLogin import *
from WeiboLogin2 import *
from login import *
from WeiboCrawler import *
from get_weibo_page import *
from time import sleep
from log_util import *
from utils import *

time_now = time.strftime('%Y%m%d', time.localtime(time.time()))
lf='./log/logging_crawl_weibo_' + time_now + '.log'
logger = Logger(log_level=1, logger="main", log_file = lf).get_logger()


def update_monitor(key, value):
    time_now1 = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    cur_hour = time.strftime('%H', time.localtime(time.time()))
    json_str = redis_monitor .hget(time_now1, cur_hour)
    json_total = redis_monitor .hget(time_now1, 'total' )
    record_dic = {}
    total_dic = {}
    if type(value) == types.StringType:
        if value.isdigit():
            value = int(value)
        else:
            return
    if type(value) != types.IntType:
        print "update_monitor: type error"
        return
    if json_str == None:
        record_dic[key] = value
    else:
        record_dic = json.loads(json_str)
        if key in record_dic:
            record_dic[key] += value
        else:
            record_dic[key] = value
    if json_total == None:
        total_dic[key] = value
    else:
        total_dic = json.loads(json_total)
        if key in total_dic:
            total_dic[key] += value
        else:
            total_dic[key] = value  
       
    json_str = json.dumps(record_dic)
    json_total = json.dumps(total_dic)
    redis_monitor.hset(time_now1, cur_hour, json_str)
    redis_monitor.hset(time_now1, 'total', json_total)



def get_account():
    filename = './config/account' 
    account_list = []
    f = open(filename)  
    username = ''
    pwd = ''
    for line in f:  
        arr = line.split('\t')
        if len(arr) < 2:
            break
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

#从本地文件加载所有微博用户的主页url
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

#获取所有用户的抓取记录数，挑选待抓取uid
def get_crawl_url():
    crawl_queue = []
    all_uid_info = redis_server.hgetall('big_v_uid')
    crawled_count = redis_server.hgetall('crawl_cnt_uid')
    for uid in all_uid_info:
        info = all_uid_info[uid]
        try:
            name, nickname, url = info.split('\t')
        except:
            continue
        cmt_cnt = crawled_count.get(uid)
        if not cmt_cnt:
            #crawl_queue.append((name, nickname, url, uid, 0, 0))
            continue
        d = cmt_cnt.split('\t')
        weibo_cnt = int(d[0])
        cmt_cnt = int(d[1])
        if cmt_cnt < 500000:
            crawl_queue.append((name, nickname, url, uid, weibo_cnt, cmt_cnt))
    random.shuffle(crawl_queue) 
    return crawl_queue


def get_crawl_url2():
    crawl_queue = []
    fout = open('./data/crawl_queue.dat')
    for line in fout:
        arr = line.split('\t')
        name, nickname, url, uid, weibo_cnt, cmt_cnt = arr
        crawl_queue.append((name, nickname, url, uid, weibo_cnt, cmt_cnt))
    fout.close()
    random.shuffle(crawl_queue) 
    return crawl_queue


if __name__ == "__main__":
    global redis_server, redis_monitor
    init()
    read_config()
    print 'redis config:',const.HOST, const.PORT   
    redis_server = redis.Redis(host = const.HOST, port = const.PORT, db = 1, password='wanjun@1#7%sider')
    redis_monitor = redis.Redis(host= const.HOST, port = const.PORT, db = 2, password='wanjun@1#7%sider')

    #login in and get cookies
    print 'start login....'
    print '--------------- start login --------------'
    while 1:
        account = get_account()
        logger.info('start login....')
        weiboLogin = WeiboLogin2(account)
        if weiboLogin.Login() == False:
            #time.sleep(30)
            continue
        else:
            break
    print '---------------- login success -----------------'    
    print '---------------- start crawl -------------------'
        
    while 1:
        #load all bigV home url which crawled from baidu.
        all_user_url = get_crawl_url()
        #all_user_url.sort(key = lambda d:d[5], reverse = True)
        
        if len(all_user_url) < 10:
            break
        
        print 'load', len(all_user_url), 'user urls from redis.'
        logger.info('load ' + str(len(all_user_url)) + ' user urls.')
        #load all bigV uid.
        old_user_dict = load_all_user()
        new_user_list = []
        
        weiboCrawler = WeiboCrawler()
    
        #抓其他人的主页微博
        start_time = datetime.datetime.now()
        w_cnt = 0
        c_cnt = 0
        for data in all_user_url:
            name, nickname, home_url, uid, weibo_cnt, cmt_cnt = data
    
            logger.info('start crawl:' + str(uid) + '\t' + str(weibo_cnt) + '\t' + str(cmt_cnt))
            print 'start crawl:' + str(uid), '\t', home_url, '\t', weibo_cnt, '\t', cmt_cnt
            try:
                weibo_list = weiboCrawler.crawl_user_weibo(home_url)
                if not weibo_list:
                    continue
                cmt_cnt = weiboCrawler.crawl_weibo_comment(weibo_list)
                if cmt_cnt == 0:
                    time.sleep(10)
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
                old_user_dict[uid] = nickname
            
        end_time = datetime.datetime.now()
        waste = (end_time - start_time).seconds * 1.0 / 3600
        print 'crawl weibo over, spend', waste, 'hour.', 'crawled users:', len(all_user_url), 'all weibo count:', w_cnt, 'all comment count:', c_cnt
        logger.info('crawl weibo over, spend ' + str(waste) + 'hours.')
            
        print 'crawl completely......'
        time.sleep(1800)

    
    
    
