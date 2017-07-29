# coding=utf8
import base64
import binascii
import cookielib
import json
import os
import random, traceback
import re
import rsa
import time
import urllib
import urllib2
import urlparse
import WeiboEncode
import WeiboSearch
from log_util import *
from urllib import unquote
 
__client_js_ver__ = 'ssologin.js(v1.4.18)'
 
 
class WeiboLogin2(object):
 
    """"Login assist for Sina weibo."""
 
    def __init__(self, account):
        username, password = account
        self.user = username
        self.username = self.__encode_username(username).rstrip()
        self.password = password
 
        cj = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
 
    @staticmethod
    def __encode_username(username):
        return base64.encodestring(urllib2.quote(username))
 
    @staticmethod
    def __encode_password(password, info):
        key = rsa.PublicKey(int(info['pubkey'], 16), 65537)
        msg = ''.join([
            str(info['servertime']),
            '\t',
            str(info['nonce']),
            '\n',
            str(password)
        ])
        return binascii.b2a_hex(rsa.encrypt(msg, key))
 
    def __prelogin(self):
        url = ('http://login.sina.com.cn/sso/prelogin.php?'
               'entry=weibo&callback=sinaSSOController.preloginCallBack&rsakt=mod&checkpin=1&'
               'su={username}&_={timestamp}&client={client}'
               ).format(username=self.username, timestamp=int(time.time() * 1000), client=__client_js_ver__)
 
        resp = urllib2.urlopen(url).read()
        return self.__prelogin_parse(resp)
 
    @staticmethod
    def __prelogin_parse(resp):
        p = re.compile('preloginCallBack\((.+)\)')
        data = json.loads(p.search(resp).group(1))
        return data
 
    @staticmethod
    def __process_verify_code(pcid):
        url = 'http://login.sina.com.cn/cgi/pin.php?r={randint}&s=0&p={pcid}'.format(
            randint=int(random.random() * 1e8), pcid=pcid)
        filename = './data/pin.png'
        if os.path.isfile(filename):
            os.remove(filename)
 
        urllib.urlretrieve(url, filename)
        if os.path.isfile(filename):  # get verify code successfully
            #  display the code and require to input
            from PIL import Image
            import subprocess
            print 'verify code file:', filename
            #proc = subprocess.Popen(['display', 'E:\\02-Workspace\\NLP\\00_SinaWeiboCrawler\\src\\' + filename])
            print '--------------input verify code-----------------'
            code = raw_input('please input verify code:')
            os.remove(filename)
            #proc.kill()
            return dict(pcid=pcid, door=code)
        else:
            return dict()
 
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
        
 
    def Login(self):
        self.EnableCookie(False)#cookie或代理服务器配置        
        info = self.__prelogin()
 
        login_data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': '',
            'service': 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'rsa2',
            'sp': '',
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': '',     
            'door': '2341',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        if 'showpin' in info and info['showpin']:  # need to input verify code
            login_data.update(self.__process_verify_code(info['pcid']))
            
        login_data['servertime'] = info['servertime']
        login_data['nonce'] = info['nonce']
        login_data['rsakv'] = info['rsakv']
        login_data['su'] = self.username
        login_data['sp'] = self.__encode_password(self.password, info)
 
        return self.__do_login(login_data)
 

    def __do_login(self, data):
        url = 'http://login.sina.com.cn/sso/login.php?client=%s' % __client_js_ver__
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
        req = urllib2.Request(url=url, data=urllib.urlencode(data), headers=headers)
        resp = urllib2.urlopen(req).read().decode('GBK')
 
        return self.__parse_real_login_and_do(resp)
    
 
    def __parse_real_login_and_do(self, resp):
        #print resp
        p = re.compile('replace\(["\'](.+)["\']\)')
        url = p.search(resp).group(1)
 
        # parse url to check whether login successfully
        query = urlparse.parse_qs(urlparse.urlparse(url).query)
        try:
            if int(query['retcode'][0]) == 0:  # successful
                login_url = WeiboSearch.sRedirectData(resp)#解析重定位结果
                #print 'login_url:', login_url
                #request = urllib.request.Request(login_url)
                response = urllib2.urlopen(login_url)
                page = response.read().decode('GBK')
                #print(page)
                p2 = re.compile(r'"userdomain":"(.*?)"')
                login_url = 'http://weibo.com/' + p2.search(page).group(1)
                #request = urllib.request.Request(login_url)
                response = urllib2.urlopen(login_url)
                final = response.read().decode('utf-8')
                print 'login success! account:', self.user
                return True
            else:  # fail
                print 'return code:', query['retcode'][0]
                print 'login failed:', query['reason'][0].decode('gbk')
                return False
        except:
            start = login_url.rfind('reason=')
            reason = login_url[start + 7:]
            print 'Login error:', unquote(reason).decode('gbk')
            print traceback.print_exc()
            return False
 
    def urlopen(self, url):
        return self.opener.open(url)
 
 
if __name__ == '__main__':
    weibo = WeiboLogin2('onejune@sina.cn', 'onejune$126.com')
    if weibo.login():
        print weibo.urlopen('http://weibo.com').read()
        # with open('weibo.html', 'w') as f:
        # print >> f, weibo.urlopen('http://weibo.com/kaifulee').read()
        
        