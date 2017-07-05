# -*- coding:UTF-8 -*-
import datadeal
import urllib
import urllib2
import cookielib
import re

class log_in:
    def __init__(self,fileName):
        username, password = self.get_account(fileName)
        self.dd = datadeal.data_deal(username,password)
        self.url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)'

    def get_account(self,filename):  
        f = open(filename)  
        username = ''
        pwd = ''
        for line in f:  
            arr = line.split('\t')
            username = arr[0]
            pwd = arr[1]
        f.close()
        return username, pwd  
    
    #登录
    def login(self):
        cj = cookielib.LWPCookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cj)
        opener = urllib2.build_opener(cookie_support,urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        post_data = {
            'entry' : 'weibo',
            'gateway' : '1',
            'from'  : '',
            'savestate' : '7',
            'useticket' : '1',
            'pagerefer' : 'http://weibo.com/signup/signup.php',
            'vsnf'   : '1',
            'su'  : '',
            'service' : 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'rsa2',
            'rsakv' : '',
            'sp' :'',
            'encoding' : 'UTF-8',
            'prelt' : '115',
            'url' : 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype' : 'META'
            }
        post_data['servertime'] = self.dd.get_servername()
        post_data['nonce'] = self.dd.get_nonce()
        post_data['su'] = self.dd.get_username()
        post_data['sp'] = self.dd.get_pwd()
        post_data['rsakv'] = self.dd.get_rsakv()

        post_data = urllib.urlencode(post_data)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1;rv:26.0) Gecko/20100101 Firefox/26.0'}
        req = urllib2.Request(
                              url = self.url,
                              data = post_data,
                              headers = headers
                              )
        result = urllib2.urlopen(req)
        text = result.read()
        #print text
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        try:
            login_url = p.search(text).group(1)
            #print u'匹配url:'
            #print login_url
            html = urllib2.urlopen(login_url)
            data = html.read()
            print u'登录成功！'
            #print data
            return True
        except:
            print u'登录失败！'
            return False

            
