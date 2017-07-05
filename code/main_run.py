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
from title_normalize3 import *


def process_weibo(weibo_list, hotword_dict, star_hotword_dict, star_dict):
    print '=========================  process_weibo  =========================='
    word_list = []
    time_now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    id_dict = get_all_id()
    fout = open('./result/crawl_result_' + time_now + '.dat', 'a')
    fout2 = open('./result/hotword_result_' + time_now + '.dat', 'a')
    fout3 = open('./result/hotword_star_' + time_now + '.dat', 'a')
    new_id_list = []
    for w in weibo_list:
        id = w['id']
        if id in id_dict:
            continue
        new_id_list.append(id)
        weibo_text = w['content']
        forward_text = w['forward_text']
        kws_lst = get_text_keyword(weibo_text + forward_text)
        #print weibo_text + forward_text, '===>', '|'.join(kws_lst)
        
        for key in kws_lst:
            if key in hotword_dict:
                fout2.write(key + '++++' + w['id'] + '\t' + w['name'] + '\t' + w['time'] + '\t' + w['url'] + '\t' + w['content'] + '\t' + w['forward_text'] + '\n')
                break
        #是否是明星
        is_star = False
        star = ''
        for key in kws_lst:
            if key in star_dict:
                is_star = True
                star = key
                print key, '+++', weibo_text
                fout3.write(star + '++++' + w['id'] + '\t' + w['name'] + '\t' + w['time'] + '\t' + w['url'] + '\t' + w['content'] + '\t' + w['forward_text'] + '\n')            
        
        word_list.append((weibo_text, kws_lst))
        fout.write(w['id'] + '\t' + w['name'] + '\t' + w['time'] + '\t' + w['url'] + '\t' + w['content'] + '\t' + w['forward_text'] + '\n')
    fout.close()
    fout2.close()
    fout3.close()
    
    fout = open('./weibo_id/' + time_now + '.dat', 'a')
    for id in new_id_list:
        fout.write(id + '\n')
    fout.close()
    print 'get', len(new_id_list), 'new weibo.'


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




if __name__ == "__main__":
    
    WBmsg = getWeiboPage()
    weiboCrawler = WeiboCrawler()
    filename = './config/account'#保存微博账号的用户名和密码，第一行为用户名，第二行为密码 
    account_list = get_account(filename)
    if len(account_list) == 0:
        exit()
    
    weibo_list = []
    for account in account_list:
        weiboLogin = WeiboLogin(account)
        if weiboLogin.Login() == False:
            continue
        #抓取自己的主页微博
        home_url = weiboLogin.get_home_page_url()
        #temp_list = weiboCrawler.get_my_home_page(home_url)
        
        #抓其他人的主页微博
        home_url = 'http://weibo.com/u/1549364094'
        home_url = 'http://weibo.com/p/1004061289997621/'
        id = 0

        #weibo_list, weibo_name = weiboCrawler.get_homepage_weibo(home_url)
        #mid = '4125365746092545'
        #根据weibo id抓取评论
        #weibo_comment = weiboCrawler.get_weibo_comment(weibo_list, weibo_name)
        #save_cmt(weibo_comment, weibo_name)
        
        #微博搜索
        key = ''
        weibo_list = weiboCrawler.weibo_search('宋慧乔')
        
        break

        
    print 'completely......'

    
    
    
