#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
抓取一个用户的所有微博、评论
'''
import sys, os
import urllib
import urllib2
import cookielib
import base64
import re, time, datetime, json
import hashlib,random
from StringIO import StringIO
import gzip, traceback
from bs4 import BeautifulSoup
from bs4 import NavigableString
from log_util import *

time_now = time.strftime('%Y%m%d', time.localtime(time.time()))
lf='./log/logging_crawl_weibo_' + time_now + '.log'
logger = Logger(log_level=1, logger="crawler", log_file = lf).get_logger()

class WeiboCrawler:
    def __init__(self):
        proxy_file = "config/proxy.txt" 
        proxy_file = open(proxy_file, "r")
        self.proxy_list = self.LoadProxy(proxy_file)
        self.MAX_WEIBO_PAGE = 100
        self.MAX_COMMENT_PAGE = 1000
        
    def downLoadPage(self, charset, req_url):  
        if req_url == '':
            return
        proxy_num = len(self.proxy_list)
        proxy_selected = random.randint(0, proxy_num-1)
        proxy_this = self.proxy_list[proxy_selected]
    
        #set proxy
        enable_proxy = False
        proxy_handler = urllib2.ProxyHandler({'http':'http://' + proxy_this +':50180'})
        null_proxy_handler = urllib2.ProxyHandler({})
        if enable_proxy:
            opener = urllib2.build_opener(proxy_handler)
        else:
            opener = urllib2.build_opener(null_proxy_handler)
        urllib2.install_opener(opener)
        request = urllib2.Request(req_url)
        
        timeoutsecond = 500
        data = None
        
        request.add_header('Accept-encoding', 'gzip')
        
        try:
            response = urllib2.urlopen(request,timeout=timeoutsecond)
            
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO( response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = f.read().decode(charset,'ignore')
            else:
                data = response.read()
        except urllib2.URLError, e:
            #print url, e.reason
            #logger.info(url + '\t' + str(e.reason))
            pass
        return data

    def LoadProxy(self, file):
        proxyList = []
        for line in file:
            line = line.strip()
            proxyList.append(line)
        return proxyList
    
    
    def get_all_id(self):
        id_dict = {}
        time_now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        file_name = './data/weibo_id.dat'
        if os.path.exists(file_name) == False:
            return id_dict
        fin = open(file_name)
        for line in fin:
            arr = line.strip().split('\t')
            uid = arr[0]
            wid = arr[1]
            id_dict[wid] = 1
        return id_dict

    
    def get_content(self, charset):
        content = self.downLoadPage(charset, self.url)
        return content
    
    def get_uid(self, url):
        arr = url.split('/')
        if len(arr) > 4:
            return arr[4]
        return None
    
    def get_personal_info(self, uid):
        try:
            url = 'http://weibo.com/p/%s/info?mod=pedit_more' % (uid)
            content = urllib2.urlopen(url).read()
            print content
            start = content.find('domid":"Pl_Official_PersonalInfo__62')
            #print start
            if start == -1:
                return None
            start = content.find('<div', start, -1)
            if start == -1:
                return None
            end = content.find('<!--\/\/模块-->', start, -1)
            content = content[start: end]
            print content
            start = content.find('WB_innerwrap')
            #print start
            if start == -1:
                return None
            end = content.find('<\/div>', start, -1)
            if start == -1:
                return None
            div_str = content[start + 19: end + 6]
            #print 'div_str:', div_str
            
            div_str = div_str.replace(r'\t', '')
            div_str = div_str.replace(r'\r', '')
            div_str = div_str.replace(r'\n', '')
            div_str = div_str.replace('\\', '')
            #print 'after replace:', div_str
            soup = BeautifulSoup(div_str)
            title_list = []
            value_list = []
            tags = soup.find(name="div").descendants
            i = 0
            for tag in tags:
                if isinstance(tag, NavigableString):
                    print tag
                    if i % 2 == 0:
                        title_list.append(tag)
                    else:
                        value_list.append(tag)
                    i += 1
            
#             title = soup.findAll(name ="span", attrs={'class':'pt_title S_txt2'})
#            
#             for t in title:
#                 print t, t.text
#                 title_list.append(t.text.strip())
#             
#             value = soup.findAll(name ="span", attrs={'class':'pt_detail'})
#             for t in value:
#                 print t, t.text
#                 value_list.append(t.text.strip())
                        
            i = 0
            info_dict = {}
            for i in range(0, len(title_list) - 1):
                title = title_list[i].encode('utf-8')
                title = title.replace('：', '')
                #print title, value_list[i]
                info_dict[title] = value_list[i].encode('utf-8')
            #uid = self.get_uid(url)
            info_dict['uid'] = uid
        except:
            traceback.print_exc()
            print url
            return None
        return info_dict
    
    
    def crawl_fans_uid(self, uid):

        uid_list = []
        first_page_url = 'http://weibo.com/p/%s/follow?relate=fans&from=100505&wvr=6&mod=headfans&current=fans&ajaxpagelet=1&ajaxpagelet_v6=1&__ref=/p/%s/info&_t=FM_146232968011639' % (uid, uid)
        next_page = 'http://weibo.com/p/%s/follow?pids=Pl_Official_HisRelation__64&relate=fans&page=%s&ajaxpagelet=1&ajaxpagelet_v6=1&__ref=/p/%s/follow&_t=FM_1462329680%s'
        number = 11647
        content = ''
        content = urllib2.urlopen(first_page_url).read()
        #print content
        content = content.replace(r'\t', '')
        content = content.replace(r'\r', '')
        content = content.replace(r'\n', '')
        content = content.replace('\\', '')
        reg = re.compile('action-data="uid=([0-9]+?)&fnick')       
        res = re.findall(reg, content)
        print 'res:', res
        for u in res:
            uid_list.append(u)
                
        page = 2
        while True:
            url = next_page % (uid, page, uid, number)
            print url
            content = urllib2.urlopen(url).read()
            content = content.replace(r'\t', '')
            content = content.replace(r'\r', '')
            content = content.replace(r'\n', '')
            content = content.replace('\\', '')
            print content
            reg = re.compile('action-data="uid=([0-9]+?)&fnick')       
            res = re.findall(reg, content)
            print 'res:', res
            for u in res:
                uid_list.append(u)
            if len(res) == 0:
                break
            page += 1
            number += 5
        print len(uid_list)
        return uid_list
    
    
    def get_uid_by_url(self, url):
        request = urllib2.Request(url) 
        response = urllib2.urlopen(request,timeout=500)
        content = response.read()
        #print content
        start = content.find('$CONFIG[\'page_id\']=')
      
        if start == -1:
            return None
        end = content.find('\'', start + 22)
        if end == -1:
            return None
        uid = content[start + 20 : end]
        return uid
    
    
    def get_read_num(self, url):
        request = urllib2.Request(url) 
        response = urllib2.urlopen(request,timeout=500)
        content = response.read()
        res = re.findall('阅读数：([0-9万\+]+)</span>', content)
        if len(res) != 0:
            return res[0]
        else:
            return 0
        
    def get_news(self):
        url = 'http://weibo.com/a/aj/transform/loadingmoreunlogin?ajwvr=6&page=0&category=0&__rnd=1465798941751'
        request = urllib2.Request(url) 
        response = urllib2.urlopen(request,timeout=500)
        content = response.read()
        if content == None or content == '':
            return None
        
        data = json.loads(content)['data']
        data = data.replace('\n', '')
        data = data.replace('\t', '')
        
        soup = BeautifulSoup(data)
        title_list = []
        url_list = []
        author_list = []
        time_list = []
        read_num_list = []
        
        title = soup.findAll(name ="a", attrs={'class':'W_autocut S_txt1'})
            
        for t in title:
            url = t.attrs['href'].strip()
            title = t.string.strip()
            read_num = self.get_read_num(url)
            print url, title, read_num
            title_list.append(t.text.strip())
            url_list.append(url)
            read_num_list.append(read_num)
        
        author = soup.findAll(name ="span", attrs={'class':'subinfo S_txt2'})
            
        for t in author:
            a = t.string.strip()
            print a
            if a.find('@') != -1:
                author_list.append(a)
            else:
                time_list.append(a)
    
    
    
    def extract_weibo_info(self, content):
        if content == None or len(content) == 0:
            print 'content is null'
            return None, None, None
        #print content
        div_str = content.replace(r'\t', '')
        div_str = div_str.replace(r'\r', '')
        div_str = div_str.replace(r'\n', '')
        content = div_str.replace('\\', '')
        
        start = content.find('<div node-type="homefeed">')
        end = content.rfind('</div>')
        if end == -1:
            return None, None, None
        #print start, end, content
        
        content = content[start: end].strip()
        #print start, end, content
        
        start = 0
        i = 1
        nick_name = ''
        weibo_list = []
        weibo_dict = {}
        mid = ''
        start_mid = ''
        end_mid = ''
        page = 0
        pre_page = 0
        page_bar = 0
        
        while start != -1:
            news_time = ''
            weibo_url = ''
            nick_name = ''
            weibo_text = ''
            forward_text = ''
            weibo_dict = {}
            start = content.find('<div   mrid=', start)
            end_1 = content.find('</div>', start)
            mid_div = content[start : end_1 + 6]
            #print mid_div
            
            soup = BeautifulSoup(mid_div)
            tags = soup.find(name = "div", mid = True, mrid = True)
            if tags != None:
                mid = tags.attrs['mid']
                if start_mid == '':
                    start_mid = mid
            
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
                        weibo_url = 'http://weibo.com' + tag.attrs['href']
                    except:
                        traceback.print_exc()
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
            
            #get forward content
            start_2 = content.find('<div class="WB_text" node-type="feed_list_reason"', end)
            start_1 = content.find('<div   mrid=', end)
            if start_2 != -1 and start_1 > start_2:
                end = content.find('</div>', start_2)
                if end != -1:
                    forward_text = content[start_2: end + 6]           
                    soup = BeautifulSoup(forward_text)
                    forward_text = soup.text.strip()
            
            weibo_dict['forward_text'] = forward_text
            weibo_dict['content'] = weibo_text
            weibo_dict['id'] = mid
            weibo_dict['name'] = nick_name
            weibo_dict['time'] = news_time
            if weibo_url != '':
                weibo_url = weibo_url.split('?')[0]
                weibo_dict['url'] =  weibo_url
            
            weibo_list.append(weibo_dict)
            
            print i, mid, nick_name, news_time, weibo_url, weibo_text.decode('utf-8'), 'forward:', forward_text.decode('utf-8')
            start = end + 6
            i += 1
            
        end_mid = mid
        return weibo_list, start_mid, end_mid
        
        
        
        
    def get_my_home_page(self, home_page_url):
        weibo_list = []
        req_url = 'http://weibo.com/aj/mblog/fsearch?ajwvr=6&end_id=%s&pre_page=%s&page=%s&min_id=%s&pagebar=%s'
        
        #第一次抓取，首页第一屏
        req = urllib2.Request(home_page_url)
        result = urllib2.urlopen(req).read()
        #print result
        weibo_list, mid1, mid2 = self.extract_weibo_info(result)
        print 'mid1:', mid1, 'mid2:', mid2
        if weibo_list == None:
            return None
        end_mid = mid1
        min_mid = mid2
        
        page = 1
        pre_page = 1
        page_bar = 0
        
        #抓5页
        while page < 30:
            page_bar = 0
            #每一页抓3屏
            while page_bar < 3:
                print '==========================================='
                print 'page:', page, ' page_bar:', page_bar
                url = req_url % (end_mid, pre_page, page, min_mid, page_bar)
                print url
                req = urllib2.Request(url)
                try:
                    result = urllib2.urlopen(req).read().decode("unicode-escape")
                    #print '1:', result
                except:
                    continue
                
                tmp_list, mid1, mid2 = self.extract_weibo_info(result)

                if len(tmp_list) == 0:
                    break
                weibo_list += tmp_list
                
                min_mid = mid2
                page_bar += 1
            page += 1
            
        return weibo_list
    
    
    #获取主页信息，包括page id，微博用户名
    def get_page_info(self, content):
        div_str = content.replace('\t', '')
        div_str = div_str.replace('\r', '')
        div_str = div_str.replace('\n', '')
        content = div_str.replace('\\', '')
        #print content
        #print content
        res = re.findall(r'CONFIG\[\'page_id\']=\'([^\']+)', content)
        if len(res) == 0:
            return None, None, None
        page_id = res[0]
        
        res = re.findall(r'CONFIG\[\'title_value\'\]=\'([^\']+)', content)
        if len(res) == 0:
            return None, None, None
        weibo_name = res[0].split('_')[0]
        
        pid = ''
        res = re.findall(r'CONFIG\[\'pid\'\]=\'([^\']+)', content)
        if len(res) == 0:
            res = re.findall(r'CONFIG\[\'domain\'\]=\'([^\']+)', content)
            if len(res) != 0:
                pid = res[0]
            else:
                pid = page_id[0:6]
        else:
            pid = res[0]
        print 'page id:', page_id, 'weibo name:', weibo_name, 'pid:', pid
        return page_id, weibo_name, pid
    
    
    def load_crawled_wid(self, uid):
        if not uid:
            return {}
        p = './output/' + uid +  '/' + uid + '_weibo.dat'
        if not os.path.exists(p):
            return {}
        wid_dict = {}
        fin = open(p)
        for line in fin:
            arr = line.split('\t')
            wid = arr[0].strip()
            wid_dict[wid] = 1
        fin.close()
        return wid_dict
    
    #抓取一个用户的所有微博
    def crawl_all_weibo_by_uid(self, home_page_url):
        page = 1
        pre_page = 1
        page_bar = 0
        uid = ''
        weibo_list = []
        #第一次抓取，首页第一屏
        req = urllib2.Request(home_page_url)
        try:
            result = urllib2.urlopen(req, timeout = 10).read()
        except:
            return None, None, None
        #获取页面信息
        uid, weibo_name, pid = self.get_page_info(result)
      
        weibo_list = self.extract_weibo_info_from_homepage(result)
        if weibo_list == None:
            return weibo_list, uid, weibo_name
        req_url = 'http://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=%s&domain_op=%s&id=%s&pre_page=%s&page=%s&pagebar=%s'
        #抓5页
        while page < self.MAX_WEIBO_PAGE:
            cnt = 0
            page_bar = 0
            #每一页抓3屏
            while page_bar < 3:
                #print 'page:', page, ' page_bar:', page_bar
                url = req_url % (pid, pid, uid, pre_page, page, page_bar)
                req = urllib2.Request(url)
                try:
                    result = urllib2.urlopen(req, timeout = 10).read()
                except:
                    traceback.print_exc()
                    break
                
                #tmp_list, mid1, mid2 = self.extract_weibo_info(result)
                tmp_list = self.extract_weibo_info_from_json(result)
                cnt += len(tmp_list)
                if not tmp_list:
                    break
                print 'crawled', len(tmp_list), 'weibo in', url
                weibo_list += tmp_list
                page_bar += 1
            if cnt == 0:
                break
            page += 1
        print 'crawled', page, 'pages,', len(weibo_list), 'weibo in', weibo_name
        logger.info('crawled ' +  str(page) + ' pages,' + str(len(weibo_list)) + ' weibo for ' + str(weibo_name))
        return weibo_list, uid, weibo_name
        
    
    #抓取微博
    def crawl_user_weibo(self, home_page_url):
        logger.info('get weibo for ' + home_page_url)
        new_weibo_list = []
        weibo_list, uid, weibo_name = self.crawl_all_weibo_by_uid(home_page_url)
        logger.info('get uid:' + str(uid) + ' weibo_name:' + str(weibo_name))
        self.home_url = home_page_url
        self.uid = uid
        self.weibo_name = weibo_name
        if weibo_list and uid and weibo_name:
            crawled_wid_dict = self.load_crawled_wid(uid) #已经抓取过的weibo id
            for weibo in weibo_list:
                wid = weibo['id']
                if wid not in crawled_wid_dict:
                    new_weibo_list.append(weibo)
            self.save_weibo(new_weibo_list)
        print 'crawled ' + str(len(new_weibo_list)) + ' new weibo for user ' + str(self.uid)
        logger.info('crawled ' + str(len(new_weibo_list)) + ' new weibo for user ' + str(self.uid))
        return weibo_list
    
    
    def extract_weibo_info_from_homepage(self, content):
        if content == None or len(content) == 0:
            print 'content is null'
            return None, None, None
        #print content
        div_str = content.replace('\t', '')
        div_str = div_str.replace('\r', '')
        div_str = div_str.replace('\n', '')
        content = div_str.replace('\\', '')
        
        start = content.find('<div class="WB_feed WB_feed_v3 WB_feed_v4')
        end = content.rfind('</div>')
        if end == -1:
            return None, None, None
        #print start, end, content
        
        content = content[start: end].strip()
        #print start, end, content
        
        start = 0
        i = 1
        nick_name = ''
        weibo_list = []
        weibo_dict = {}
        mid = ''
        start_mid = ''
        end_mid = ''
        page = 0
        pre_page = 0
        page_bar = 0
        
        while start != -1:
            news_time = ''
            weibo_url = ''
            nick_name = ''
            weibo_text = ''
            forward_text = ''
            weibo_dict = {}
            #print content
            start = content.find('<div class="WB_from S_txt2">', start)
      
            if start == -1:
                break
            end = content.find('</div>', start)
            if end == -1:
                break
            time_str = content[start: end + 6]
            #print time_str
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
                        weibo_url = 'http://weibo.com' + tag.attrs['href']
                        mid = tag.attrs['name']
                        if start_mid == '':
                            start_mid = mid
                        #print mid
                    except:
                        #traceback.print_exc()
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
            weibo_text = ' '.join(weibo_text.split())

            weibo_dict['content'] = weibo_text
            weibo_dict['id'] = mid

            if weibo_url != '':
                weibo_url = weibo_url.split('?')[0]
                weibo_dict['url'] =  weibo_url
            
            weibo_list.append(weibo_dict)
            #print i, mid, weibo_url, weibo_text.decode('utf-8')
            start = end + 6
            i += 1
            
        end_mid = mid
        return weibo_list
    
    
    def clear_content(self, content):
        content = content.decode("unicode-escape")
        div_str = content.replace('\t', '')
        div_str = div_str.replace('\r', '')
        div_str = div_str.replace('\n', '')
        content = div_str.replace('\\', '')
        return content
    
    #抓取翻页的或者翻屏微博
    def extract_weibo_info_from_json(self, content):
        if content == None or len(content) == 0:
            print 'content is null'
            return None, None, None
        content = self.clear_content(content)
         
        weibo_list = []
        weibo_dict = {}
        div_tags = BeautifulSoup(content).find_all('div', attrs={"action-type": "feed_list_item"})
        if not div_tags:
            return weibo_list
        for tag in div_tags:
            mid = tag.attrs.get('mid')
            if not mid:
                continue
            #print 'mid:', mid
            items = tag.find(name = 'div', attrs={"class": "WB_text W_f14", "node-type": "feed_list_content"})
            if items:
                weibo_text = items.text.strip()
                weibo_text = ' '.join(weibo_text.split())
            else:
                weibo_text = ''
            #print weibo_text
            weibo_dict = {}
            weibo_dict['content'] = weibo_text
            weibo_dict['id'] = mid
            weibo_list.append(weibo_dict)
        return weibo_list
    
    
    def is_wid_crawled(self, wid):
        p = './output/' + self.uid + '/' + wid + '_comment.dat'
        if os.path.exists(p):
            return True
        else:
            return False
    
    
    def crawl_weibo_comment(self, weibo_list):
        weibo_comment = {}
        cnt = 0
        for weibo in weibo_list:
            wid = weibo['id']
            if wid in weibo_comment:
                continue
            #判断是否已经抓过该微博的评论
            if self.is_wid_crawled(wid):
                continue
            cmt_list = self.get_comment_by_mid(wid)
            if not cmt_list:
                continue
            weibo_comment[wid] = cmt_list
            self.save_cmt(cmt_list, wid)
            cnt += len(cmt_list)
        return cnt
    
    #根据指定 的weibo id抓取评论
    def get_comment_by_mid(self, mid):
        if not mid:
            return []
        cmt_list = []
        page = 1
        while page < self.MAX_COMMENT_PAGE:
            req_url = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&root_comment_ext_param=&page=%d&filter=hot&filter_tips_before=1&from=singleWeiBo' % (mid, page)
            req = urllib2.Request(req_url)
            try:
                content = urllib2.urlopen(req, timeout=10).read().decode("unicode-escape")
            except:
                time.sleep(10)
                continue
            div_str = content.replace('\t', '')
            div_str = div_str.replace('\r', '')
            div_str = div_str.replace('\n', '')
            content = div_str.replace('\\', '')
            
            start = content.find('<div')
            end = content.rfind('</div>')
            if end <= start:
                break
            content = content[start: end].strip()
            soup = BeautifulSoup(content)
            tags = soup.find_all(name = 'div', attrs = {'class':'WB_text'})
            if len(tags) == 0:
                break
            for tag in tags:
                cmt = tag.text
                cmt = cmt.strip()
                cmt_list.append(cmt)
                #print cmt
            page += 1
        print 'crawled', len(cmt_list), 'comment for', mid
        logger.info('crawler ' + str(len(cmt_list)) + ' comments for ' + str(mid))
        return cmt_list
        
        
    def save_cmt(self, weibo_comment, wid):
        time_now = time.strftime('%Y%m%d', time.localtime(time.time()))
        p = './output/' + self.uid
        if not os.path.exists(p):
            os.makedirs(p)
        fout = open(p  + '/' + wid + '_comment.dat', 'a')
        for cmt in weibo_comment:
            if self.weibo_name and wid and cmt:
                fout.write(wid + '\t' + cmt + '\n')
        fout.close()
        
        
    def save_weibo(self, weibo_list):
        time_now = time.strftime('%Y%m%d', time.localtime(time.time()))
        p = './output/' + self.uid 
        if not os.path.exists(p):
            os.makedirs(p)
        fout = open(p + '/' + self.uid + '_weibo.dat', 'a')
        for weibo in weibo_list:
            if weibo['id'] and weibo['content']:
                fout.write(weibo['id'] + '\t' + weibo['content'] + '\n')
        fout.close()
    
    def save_user(self, weibo_cnt, cmt_cnt):
        time_now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        p = './output/weibo_user.dat'
        fout = open(p, 'a')
        fout.write(self.uid + '\t' + self.home_url + '\t' + self.weibo_name + '\t' + str(weibo_cnt) + '\t' + str(cmt_cnt) + '\t' + time_now + '\n')
        fout.close()
    
        
    def weibo_search(self, keyword):
        weibo_list = []
        print 'search weibo by keywords:', keyword
        page = 1
        while 1:
            req_url = 'http://s.weibo.com/weibo/%s&nodup=1&page=%s' % (keyword, page)
            print req_url
            req = urllib2.Request(req_url)
            try:
                content = urllib2.urlopen(req).read().decode("unicode-escape")
            except:
                break
            div_str = content.replace('\t', '')
            div_str = div_str.replace('\r', '')
            div_str = div_str.replace('\n', '')
            content = div_str.replace('\\', '')
            #print content
            start = content.find('<div class="search_feed">')
            if start == -1:
                break
            end = content.find('"})</script>', start)
            
            content = content[start : end - 12]
            #print start, end, content
            
            soup = BeautifulSoup(content)
            tags = soup.find_all(name = 'p', attrs = {'class':'comment_txt', 'node-type':'feed_list_content'})
            for tag in tags:
                name = tag.get('nick-name')
                weibo = tag.text
                weibo_list.append((name, weibo))
                #print tag.get('nick-name'), '----', tag.text
            page += 1
            if page % 3 == 0:
                time.sleep(1)
            
        print 'searched', len(weibo_list), 'weibo.'
        
        fout = open('./result/searched_weibo.dat', 'a')
        for weibo in weibo_list:
            fout.write(weibo[0] + '\t' + weibo[1] + '\n')
        fout.close()
        
        return weibo_list
    
    
        
        
    
