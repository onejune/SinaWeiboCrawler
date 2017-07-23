#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from urllib import *
import urllib2, urllib, random
import cookielib
import base64
import re
import json
import hashlib, traceback
import WeiboEncode
import WeiboSearch
from log_util import *


time_now = time.strftime('%Y%m%d', time.localtime(time.time()))
lf='./log/logging_login_' + time_now + '.log'
logger = Logger(log_level=1, logger="login", log_file = lf).get_logger()

class WeiboLogin:
    def __init__(self, account, enableProxy = False):
        "初始化WeiboLogin，enableProxy表示是否使用代理服务器，默认关闭"
        
        logger.info("Initializing WeiboLogin...")
        user, pwd = account
        self.userName = user
        self.passWord = pwd
        self.home_page_url = ''
        self.enableProxy = enableProxy
        print 'start login with:', user
        self.serverUrl = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.11)&_=1379834957683"
        self.loginUrl = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)"
        self.postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}
        
        proxy_file = "config/proxy.txt" 
        proxy_file = open(proxy_file, "r")
        proxy_list = self.LoadProxy(proxy_file)
        proxy_num = len(proxy_list)
        
        proxy_selected = random.randint(0, proxy_num-1)
        proxy_this = proxy_list[proxy_selected]
        proxy_handler = urllib2.ProxyHandler({'http':'http://' + proxy_this})
        print 'proxy:', proxy_this
        
        null_proxy_handler = urllib2.ProxyHandler({})
  
        if enableProxy:
            opener = urllib2.build_opener(proxy_handler)
        else:
            opener = urllib2.build_opener(null_proxy_handler)
        urllib2.install_opener(opener)
        
    
    def LoadProxy(self, file):
        proxyList = []
        for line in file:
            line = line.strip()
            proxyList.append(line)
        return proxyList


    def get_account(self, filename):
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
    
    
    def get_home_page_url(self):
        return self.home_page_url


    def Login(self):
        "登陆程序"  
        self.EnableCookie(self.enableProxy)#cookie或代理服务器配置

        serverTime, nonce, pubkey, rsakv = self.GetServerTime()#登陆的第一步
        postData = WeiboEncode.PostEncode(self.userName, self.passWord, serverTime, nonce, pubkey, rsakv)#加密用户和密码
        print "Post data length:", len(postData)

        req = urllib2.Request(self.loginUrl, postData, self.postHeader)
        print "Posting request..."
        result = urllib2.urlopen(req)#登陆的第二步——解析新浪微博的登录过程中3
        text = result.read().decode('GBK')
        #print text
        try:
            login_url = WeiboSearch.sRedirectData(text)#解析重定位结果
            #request = urllib.request.Request(login_url)
            response = urllib2.urlopen(login_url)
            page = response.read().decode('GBK')
            #print(page)
            p2 = re.compile(r'"userdomain":"(.*?)"')
            login_url = 'http://weibo.com/' + p2.search(page).group(1)
            #request = urllib.request.Request(login_url)
            response = urllib2.urlopen(login_url)
            final = response.read().decode('utf-8')
            #print final
        except:
            print 'Login error!'
            logger.error('login error for ' + self.userName)
            print traceback.print_exc()
            return False

        print '************************'
        print self.userName, 'Login sucess!'
        print '************************'
        logger.error('login successfully for ' + self.userName)
        return True
    
    
    def EnableCookie(self, enableProxy):
        "Enable cookie & proxy (if needed)."
    
        cookiejar = cookielib.LWPCookieJar()#建立cookie
        cookie_support = urllib2.HTTPCookieProcessor(cookiejar)
    
        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http':'http://xxxxx.pac'})#使用代理
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            print "Proxy enabled"
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    
        urllib2.install_opener(opener)#构建cookie对应的opener
    
    
    def GetServerTime(self):
        "Get server time and nonce, which are used to encode the password"
    
        print "Getting server time and nonce..."
        serverData = urllib2.urlopen(self.serverUrl).read()#得到网页内容
        print serverData
    
        try:
            serverTime, nonce, pubkey, rsakv = WeiboSearch.sServerData(serverData)#解析得到serverTime，nonce等
            return serverTime, nonce, pubkey, rsakv
        except:
            print 'Get server time & nonce error!'
            return None


