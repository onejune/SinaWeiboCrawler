#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import sys
import time, re
import cookielib
from bs4 import BeautifulSoup
from bs4 import NavigableString

reload(__import__('sys' )).setdefaultencoding('utf-8')

class getWeiboPage:
    
    body = {
        '__rnd':'',
        '_k':'',
        '_t':'0',
        'count':'50',
        'end_id':'',
        'max_id':'',
        'page':1,
        'is_all':'1',
        'pagebar':'',
        'pre_page':'0',
        'uid':''
    }
    uid_list = []
    charset = 'utf8'
    
    def init(self):
        # 获取一个保存cookie的对象
        cj = cookielib.LWPCookieJar()
        # 将一个保存cookie对象，和一个HTTP的cookie的处理器绑定
        cookie_support = urllib2.HTTPCookieProcessor(cj)
        # 创建一个opener，将保存了cookie的http处理器，还有设置一个handler用于处理http的URL的打开
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        # 将包含了cookie、http处理器、http的handler的资源和urllib2对象板顶在一起
        urllib2.install_opener(opener)
     

    def getWeiboMsg(self):
        return
        
        
    def get_msg(self,uid):
        getWeiboPage.body['uid'] = uid
        url = self.get_url(uid)
        content = ''
        content += self.get_firstpage(url)
        content += self.get_secondpage(url)
        content += self.get_thirdpage(url)
        print 'get weibo page completely.....'
        return content
        
        
    def get_firstpage(self,url):
        getWeiboPage.body['pre_page'] = getWeiboPage.body['page']-1
        url = url + urllib.urlencode(getWeiboPage.body)
        print url
        req = urllib2.Request(url)
        result = urllib2.urlopen(req)
        text = result.read()
        #self.writefile('./output/text1',text)        
        #self.writefile('./output/result1',eval("u'''"+text+"'''"))
        
        return text
        
    def get_secondpage(self,url):
        getWeiboPage.body['count'] = '15'
    #    getWeiboPage.body['end_id'] = '3490160379905732'
    #    getWeiboPage.body['max_id'] = '3487344294660278'
        getWeiboPage.body['pagebar'] = '0'
        getWeiboPage.body['pre_page'] = getWeiboPage.body['page']

        url = url +urllib.urlencode(getWeiboPage.body)
        print url
        req = urllib2.Request(url)
        result = urllib2.urlopen(req)
        text = result.read()
        #self.writefile('./output/text2',text)        
        #self.writefile('./output/result2',eval("u'''"+text+"'''"))
        return text
    
    
    def extract_weibo_content(self, content):
        div_str = content.replace(r'\t', '')
        div_str = div_str.replace(r'\r', '')
        div_str = div_str.replace(r'\n', '')
        content = div_str.replace('\\', '')
        
        start = 0
        i = 1
        nick_name = ''
        weibo_list = []
        while start != -1:
            news_time = ''
            #get time
            start = content.find('<div class="WB_from S_txt2">', start)
            if start == -1:
                break
            end = content.find('</div>', start)
            if end == -1:
                break
            time_str = content[start: end + 6]
            soup = BeautifulSoup(time_str)
            tags = soup.find_all('a')
            for tag in tags:
                if 'date' in tag.attrs:
                    try:
                        news_time = tag.attrs['date'][0:-3]
                        tt = float(news_time)
                        x = time.localtime(tt)
                        x = time.strftime('%Y-%m-%d %H:%M:%S', x)
                        news_time = x
                    except:
                        continue
            
            start = content.find('<div class="WB_text W_f14" node-type="feed_list_content"', end)
            #print start
            if start == -1:
                break
            end = content.find('</div>', start)
            if end == -1:
                break
            
            weibo_text = content[start: end + 6]
            #get nick_name
            if nick_name == '':
                res = re.findall('nick-name="([^"]+)"', weibo_text)
                if len(res) != 0:
                    nick_name = res[0]
            
            soup = BeautifulSoup(weibo_text)
            txt = soup.text.strip()
            weibo_list.append(txt)
            
            print i, nick_name, news_time, txt.decode('utf-8')
            start = end + 6
            i += 1
        
        
    
    
    def get_thirdpage(self,url):
        getWeiboPage.body['count'] = '15'
        getWeiboPage.body['pagebar'] = '1'
        getWeiboPage.body['pre_page'] = getWeiboPage.body['page']

        url = url +urllib.urlencode(getWeiboPage.body)
        print url
        req = urllib2.Request(url)
        result = urllib2.urlopen(req)
        text = result.read()
        #self.writefile('./output/text3',text)        
        #self.writefile('./output/result3',eval("u'''"+text+"'''"))
        return text
        
    def get_url(self,uid):
        url = 'http://weibo.com/' + uid + '?from=otherprofile&wvr=3.6&loc=tagweibo&'
        return url
    
    def get_uid(self,filename):
        fread = file(filename)
        for line in fread:
            getWeiboPage.uid_list.append(line)
            print line
            time.sleep(1)
            
            
    def writefile(self,filename,content):
        fw = file(filename,'w')
        fw.write(content)
        fw.close()
        
    
    def get_my_home_page(self, url):
           
        req = urllib2.Request(url)
        result = urllib2.urlopen(req)
        content = result.read()
        #print content
        start = content.find('"domid":"v6_pl_content_homefeed"')
        end = content.find('</script>', start)
        
        content = content[start : end]
        print content
        
        start = content.find(r'<div node-type=\"homefeed\">')
        end = content.rfind(r'<\/div>')
        if end == -1:
            return
        div_str = content[start : end + 7]
        div_str = div_str.replace(r'\t', '')
        div_str = div_str.replace(r'\r', '')
        div_str = div_str.replace(r'\n', '')
        content = div_str.replace('\\', '')
        
        print start, end, content
        
        content = content.strip()
        #包含weibo内容的div
        start = content.find('<div node-type="homefeed"')
        end = content.rfind('</div>')
        content = content[start: end].strip()
        
        print start, end, content
        
        start = 0
        i = 1
        nick_name = ''
        weibo_list = []
        mid = ''
        while start != -1:
            news_time = ''
            nick_name = ''
            weibo_text = ''
            mid = ''
            start = content.find('<div   mrid=', start)
            end_1 = content.find('</div>', start)
            mid_div = content[start : end_1 + 6]
            #print mid_div
            
            soup = BeautifulSoup(mid_div)
            tags = soup.find(name = "div", mid = True, mrid = True)
            if tags != None:
                mid = tags.attrs['mid']
            
            start = content.find('<div class="WB_feed_detail clearfix"', start)
            #get nick-name
            start = content.find('<div class="WB_info">', start)
            if start == -1:
                break
            end = content.find('</div>', start)
            if end == -1:
                break
            nick_name_str = content[start: end + 6]
            soup = BeautifulSoup(nick_name_str)
            tags = soup.find_all('a')
            for tag in tags:
                if 'nick-name' in tag.attrs:
                    try:
                        nick_name = tag.attrs['nick-name']
                    except:
                        continue
            
            #get time
            start = content.find('<div class="WB_from S_txt2">', end)
            if start == -1:
                break
            end = content.find('</div>', start)
            if end == -1:
                break
            time_str = content[start: end + 6]
            soup = BeautifulSoup(time_str)
            tags = soup.find_all('a')
            for tag in tags:
                if 'date' in tag.attrs:
                    try:
                        news_time = tag.attrs['date'][0:-3]
                        tt = float(news_time)
                        x = time.localtime(tt)
                        x = time.strftime('%Y-%m-%d %H:%M:%S', x)
                        news_time = x
                    except:
                        continue
            #get weibo
            start = content.find('<div class="WB_text W_f14" node-type="feed_list_content"', end)
            #print start
            if start == -1:
                break
            end = content.find('</div>', start)
            if end == -1:
                break
            
            weibo_text = content[start: end + 6]           
            soup = BeautifulSoup(weibo_text)
            weibo_text = soup.text.strip()
            weibo_list.append(weibo_text)
            
            print i, mid, nick_name, news_time, weibo_text.decode('utf-8')
            start = end + 6
            i += 1
        
        
    
    
    