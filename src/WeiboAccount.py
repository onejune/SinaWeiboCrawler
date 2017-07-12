#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
发微博

'''

import urllib2, time, datetime
import cookielib, traceback
from WeiboLogin import *
from WeiboCrawler import *
from time import sleep

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


def send_weibo(username):
    postData =  {'text':'若说孩子长大之后会变成怎样，答案当然是只会变成无趣的大人。即使长大成人，等待着他们的既不是荣耀，也不是喜剧，而是悲剧性的暧昧人生。 ——宫崎骏',  
                'pic_id':'',  
                'rank':0,  
                'rankid':'',  
                '_surl':'',  
                'hottopicid':'',  
                'location':'home',  
                'module':'stissue',  
                '_t':0,  
        } 
    print "Post data length:", len(postData)
    postHeader = {'Referer':'http://weibo.com/%(username)s?wvr=5&wvr=5&lf=reg' % {'username': username}}
    stamp = time.mktime(datetime.datetime.now().timetuple())
    loginUrl = 'http://weibo.com/aj/mblog/add?_wv=5&__rnd=' + str(stamp)
    postData = urllib.urlencode(postData)
    req = urllib2.Request(loginUrl, postData, postHeader)
    result = urllib2.urlopen(req)
    text = result.read().decode('GBK')
    print text
    

if __name__ == "__main__":
    filename = './config/account'#保存微博账号的用户名和密码，第一行为用户名，第二行为密码 
    account_list = get_account(filename)
    if len(account_list) == 0:
        exit()
    for account in account_list:
        weiboLogin = WeiboLogin(account)
        if weiboLogin.Login() == False:
            continue
        send_weibo(account[0])
        
        
        
        
    