#-*- coding: UTF-8 -*-
import urllib2
import re
import json
import string

class GET_DATA:
    def __init__(self):
        #获取servertime ,nonce ,publey,rsakv的网址
        self.url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.11)&_=1398760051250'
        
    def get_data(self):
        data = urllib2.urlopen(self.url).read()
        p = re.compile('\((.*)\)')
        try:
            json_data = p.search(data).group(1)
            data = json.loads(json_data)
            servertime = str(data['servertime'])
            nonce = data['nonce']
            pubkey = data['pubkey']
            rsakv = data['rsakv']
            return nonce,rsakv,servertime,pubkey
        except:
            print '不能获取servertime 和 data'
            return None

