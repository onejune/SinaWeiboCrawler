# coding=utf-8

import urllib2, jieba
import jieba.posseg
import jieba.analyse
import numpy as np
import json
import time, re, os, logging, types, datetime, thread, threading, hashlib, sys, traceback, random, math
from json import JSONEncoder
from urlparse import *
from time import sleep
from types import NoneType


thread_data = {}


def find_lcs_len(s1, s2): 
  m = [ [ 0 for x in s2 ] for y in s1 ] 
  for p1 in range(len(s1)): 
    for p2 in range(len(s2)): 
      if s1[p1] == s2[p2]: 
        if p1 == 0 or p2 == 0: 
          m[p1][p2] = 1
        else: 
          m[p1][p2] = m[p1 - 1][p2 - 1] + 1
      elif m[p1 - 1][p2] < m[p1][p2 - 1]: 
        m[p1][p2] = m[p1][p2 - 1] 
      else:  # m[p1][p2-1] < m[p1-1][p2] 
        m[p1][p2] = m[p1 - 1][p2] 
  return m[-1][-1] 


def find_lcs(s1, s2): 
  # length table: every element is set to zero. 
  m = [ [ 0 for x in s2 ] for y in s1 ] 
  # direction table: 1st bit for p1, 2nd bit for p2. 
  d = [ [ None for x in s2 ] for y in s1 ] 
  # we don't have to care about the boundery check. 
  # a negative index always gives an intact zero. 
  for p1 in range(len(s1)): 
    for p2 in range(len(s2)): 
      if s1[p1] == s2[p2]: 
        if p1 == 0 or p2 == 0: 
          m[p1][p2] = 1
        else: 
          m[p1][p2] = m[p1 - 1][p2 - 1] + 1
        d[p1][p2] = 3  # 11: decr. p1 and p2 
      elif m[p1 - 1][p2] < m[p1][p2 - 1]: 
        m[p1][p2] = m[p1][p2 - 1] 
        d[p1][p2] = 2  # 10: decr. p2 only 
      else:  # m[p1][p2-1] < m[p1-1][p2] 
        m[p1][p2] = m[p1 - 1][p2] 
        d[p1][p2] = 1  # 01: decr. p1 only 
  (p1, p2) = (len(s1) - 1, len(s2) - 1) 
  # now we traverse the table in reverse order. 
  s = [] 
  while 1: 
    # print p1,p2
    if p1 < -1 or p2 < -1:
        break
    c = d[p1][p2] 
    if c == 3: s.append(s1[p1]) 
    if not ((p1 or p2) and m[p1][p2]): break
    if c & 2: p2 -= 1
    if c & 1: p1 -= 1
  s.reverse() 
  return ''.join(s)


def merge_by_string(word_list):
    word_list.sort(lambda x, y:cmp(len(x), len(y)))
    merge_dict = {}
    le = len(word_list)
    set_list = [[] for i in range(le)]
    k = 0
    hash_bucket = {}
    bucket_id = 0
    bucket_dict = {}
    
    for i in range(0, le):
        t1 = word_list[i]
        for j in range(i + 1, le):
            t2 = word_list[j]
            if has_common_str(t1, t2) != -1:
                if t1 in hash_bucket and t2 not in hash_bucket:
                    bucket = hash_bucket[t1]
                    hash_bucket[t2] = bucket
                    bucket_dict[bucket].append(t2)
                elif t2 in hash_bucket and t1 not in hash_bucket:
                    bucket = hash_bucket[t2]
                    hash_bucket[t1] = bucket
                    bucket_dict[bucket].append(t1)
                elif t1 in hash_bucket and t2 in hash_bucket:
                    pass
                else:
                    hash_bucket[t1] = hash_bucket[t2] = bucket_id
                    bucket_dict[bucket_id] = [t1, t2]
                    bucket_id += 1
    
    merge_result = []
    for id in bucket_dict:
        title_list = bucket_dict[id]
        merge_result.append(title_list)    
    
    return merge_result


def merge_by_string_thread(word_list, id):
    #print 'thread-', id, ' word cnt:', len(word_list)
    res = merge_by_string(word_list)
    thread_data[id] = res
    #print 'thread-', id, ' completely....'



def get_cos_simi(x,y):
    myx=np.array(x) #将列表转化为数组，更好的数学理解是向量
    myy=np.array(y) #将列表转化为数组，更好的数学理解是向量
        
    cos1=np.sum(myx*myy) #cos(a,b)=a*b/(|a|*|b|)
    cos21=np.sqrt(sum(myx*myx))
    cos22=np.sqrt(sum(myy*myy))
    return cos1/(float(cos21*cos22))


def calculate_similarity(t1, t2):
    kws_list1 = get_text_keyword_and_weight(t1)
    keys_1 = {}
    for k in kws_list1:
        keys_1[k[0]] = k[1]
    kws_list2 = get_text_keyword_and_weight(t2)
    keys_2 = {}
    for k in kws_list2:
        keys_2[k[0]] = k[1]
    
    kws = keys_1.keys() + keys_2.keys()
    kws = list(set(kws))
    word_vector_1 = []
    word_vector_2 = []
    for k in kws:
        if k in keys_1:
            word_vector_1.append(keys_1[k])
        else:
            word_vector_1.append(0)
        if k in keys_2:
            word_vector_2.append(keys_2[k])
        else:
            word_vector_2.append(0)
    
    cos_value = get_cos_simi(word_vector_1, word_vector_2)
    return cos_value
    
    

'''
根据keyword进行title聚类
word_list是需要归并的字符串集合，每个元素是一个二元组(title, kws)
'''
def merge_by_keyword(word_list, tag):
    hash_bucket = {}
    bucket_id = 0
    bucket_dict = {}
    print 'merge_by_keyword:', tag
    print 'word cnt before:', len(word_list)
    word_list.sort(lambda x, y:cmp(len(x), len(y)))
    merge_dict = {}
    le = len(word_list)
    
    set_list = [[] for i in range(le)]
    k = 0
    n = 0
    m = 0
    #先通过keyword汇聚到每个桶
    for i in range(0, le):
        t1 = word_list[i][0]
        w1 = word_list[i][1]
        flag = 0
        for j in range(i + 1, le):
            t2 = word_list[j][0]
            w2 = word_list[j][1]
            if len(w2) > 2 * len(w1) or len(w1) > 2 * len(w2):
                continue
            if has_common_keyword(w1, w2, tag) != -1:
                #if tag == 'title':
                #    is_same_debug(t1, t2)
                #if tag == 'bucket':
                    #print t1, '###', t2, '\t\t', '|'.join(w1), '###', '|'.join(w2)
                if t1 in hash_bucket and t2 not in hash_bucket:
                    bucket = hash_bucket[t1]
                    hash_bucket[t2] = bucket
                    bucket_dict[bucket].append(t2)
                elif t2 in hash_bucket and t1 not in hash_bucket:
                    bucket = hash_bucket[t2]
                    hash_bucket[t1] = bucket
                    bucket_dict[bucket].append(t1)
                elif t1 in hash_bucket and t2 in hash_bucket:
                    pass
                else:
                    hash_bucket[t1] = hash_bucket[t2] = bucket_id
                    bucket_dict[bucket_id] = [t1, t2]
                    bucket_id += 1
                flag = 1

        if flag == 0:
            m += 1
            #没有聚合成功的bucket也要返回
            if tag == 'bucket':
                if t1 not in hash_bucket:
                    bucket_dict[bucket_id] = [t1]
                    bucket_id += 1

    print 'bucket num:', bucket_id, '\nwords out of bucket:', m
    return bucket_dict, m


def comp(x, y):
    n1 = 0
    for z in x:
        n1 += len(z)
    n2 = 0
    for z in y:
        n2 += len(z)
    if n1 < n2:
        return 1
    elif n1 > n2:
        return -1
    else:
        return 0
    

#在bucket之间进行merge
def merge_by_bucket(merge_list):
    merge_result = []
    sno = 0
    bucket_list = []
    for bucket in merge_list:
        bucket_keyword = get_keyword_of_bucket(bucket)
        bucket_list.append((sno, bucket_keyword))
        sno += 1
    
    result_dict, rest_bucket_cnt = merge_by_keyword(bucket_list, 'bucket')
    cluster_list = []

    for result in result_dict:
        bucket_list = []
        cluster = result_dict[result]
        for bucket in cluster:
            title_list = merge_list[bucket]
            bucket_list.append(title_list)
        bucket_list.sort(lambda x,y:cmp(len(x), len(y)), reverse = True) 
        cluster_list.append(bucket_list)
    cluster_list.sort(comp) 
    return cluster_list
    
    
#返回的是已经排好序的二级聚类结果
def run_merge(word_list):
    starttime = datetime.datetime.now()
    #global thread_data
    bucket_dict, rest_title_cnt = merge_by_keyword(word_list, 'title')
    
    merge_result = []
    #对每个桶，使用title汇聚
    #thread_pool = []
    
    #第一个merge，根据titlemerge
    total_title = 0
    longest_bucket = 0
    for id in bucket_dict:
        title_list = bucket_dict[id]
        title_list = list(set(title_list))
        len_list = len(title_list)
        if len_list > longest_bucket:
            longest_bucket = len_list        
        total_title += len_list
        merge_result.append(title_list)
    print 'longest bucket:', longest_bucket
    #第二次merge，根据bucketmerge
    #merge_result = merge_by_bucket(merge_result)
        #thread_data[i] = {}
        #th = threading.Thread(target = merge_by_string_thread, args = (title_list, id))
        #thread_pool.append(th)
    
    #for t in thread_pool:
    #    t.start()
    
    #print 'word cnt after:', total_title, '\nlongest bucket:', longest_bucket
    #cnt_thread = len(thread_pool)
    #logging.info('cnt_thread:' + str(cnt_thread))
    #for th in thread_pool :
    #    threading.Thread.join(th)
    
    #for id in thread_data:
    #    id_dict = thread_data[id]
    #    for d in id_dict:
    #        merge_result.append(d)
    
    endtime = datetime.datetime.now() 
    time_elp = (endtime - starttime).seconds
    logging.info('total title:' + str(total_title))
    print ("The run_merge time is : %.03f minutes" % (time_elp / 60))
        
    return merge_result, rest_title_cnt


def is_intersect(la, lb):
    for a in la:
        if a in lb:
            return True
    return False



#使用title的keywords进行聚合
def has_common_keyword(pre, nex, tag = 'title'):
    if tag == 'bucket':
        pre = pre[0:10]
        nex = nex[0:10]
    len_nex = len(pre)
    len_pre = len(nex)
    lcs_len = len_nex + len_pre - len(set(pre + nex))
    #print ' '.join(pre), '-------',  ' '.join(nex), len_nex, len_pre, lcs_len
    if tag == 'bucket':
        #bucket之间判断相似度，必须保证公共keyword >= 3，前三个keyword必须至少有一个相同
        if lcs_len >= 3:
            len_2 = len(pre[0:3]) + len(nex[0:3]) - len(set(pre[0:3] + nex[0:3]))
            if len_2 == 0:
                #print ' '.join(pre), '-------',  ' '.join(nex), len_nex, len_pre, lcs_len
                return -1
            else:
                return 1
    else:
        if lcs_len >= len_pre * 0.5 and lcs_len >= len_nex * 0.5:
            #print ' '.join(pre), '-------',  ' '.join(nex), len_nex, len_pre, lcs_len
            return 1
        elif lcs_len >= 1:
            pass
            #print ' '.join(pre), '-------',  ' '.join(nex), len_nex, len_pre, lcs_len
    return -1  




#使用title的keywords进行聚合
def has_common_keyword2(pre, nex, tag = 'title'):
    cos_value = calculate_similarity(pre, nex)
    if cos_value >= 0.3:
        return 1
    if cos_value > 0.25:
        print pre, nex, cos_value
    return -1  



def has_common_str(pre, nex):
    len_nex = len(unicode(nex.decode('utf-8')))
    len_pre = len(unicode(pre.decode('utf-8')))
    lcs_len = find_lcs_len(unicode(pre.decode('utf-8')), unicode(nex.decode('utf-8')))
    if lcs_len >= len_pre * 0.5 and lcs_len >= len_nex * 0.5:
        return 1
    return -1  


def merge(set_list):
    le = len(set_list)
    for i in range(0, le):
        word_listi = set_list[i]
        if len(word_listi) == 0:
            continue
        for j in range(i + 1, le):
            word_listj = set_list[j]
            if is_intersect(word_listi, word_listj):
                set_list[i] += word_listj
                set_list[j] = []
                j = i + 1
                                  

def get_text_keyword(text):
    res_list = []
    key_word_list = jieba.analyse.extract_tags(text, withWeight=True)
    for key, value in key_word_list:
        pattern = re.compile("^[\w\.]+$")
        match = pattern.match(key)
        if match:
            continue
        res_list.append(key)
    
    return res_list


def get_text_keyword_and_weight(text):
    res_list = []
    key_word_list = jieba.analyse.extract_tags(text, withWeight=True)
    for key, value in key_word_list:
        pattern = re.compile("^[\w\.]+$")
        match = pattern.match(key)
        if match:
            continue
        res_list.append((key, value))
    
    return res_list


#找到属于同一个桶的出现次数最多的keyword
def get_keyword_of_bucket(title_list):
    w_dict = {}
    title_str = ''
    for title in title_list:
        title_str += title + '\t'
    key_word_list = get_text_keyword(title_str)
    return key_word_list


def get_keyword_of_cluster(bucket_list):
    w_dict = {}
    title_str = ''
    for bucket in bucket_list:
        for title in bucket:
            title_str += title + '\t'
    key_word_list = get_text_keyword(title_str)
    return key_word_list


word_seg_dict = {}
def get_title_keyword(title):
    invalid_tag = ['x', 'e', 'u', 'ug', 'r', 'm', 'ad', 'p', 'c', 'uj', 'q', 'l', 'i', 'ul', 'f', 'eng']
    len_limit = ['d', 'n', 'a']
    invalid_word = [u'是']
    seg_list = jieba.posseg.cut(title)
    kws_list = []
    for word, tag in seg_list:
        if tag in len_limit and len(unicode(word)) == 1:
            continue
        if tag not in invalid_tag and word not in invalid_word:
            kws_list.append(word + tag)
            if word + tag in word_seg_dict:
                word_seg_dict[word + tag] += 1
            else:
                word_seg_dict[word + tag] = 1
    kws_list = list(set(kws_list))
    #print title, '###', '|'.join(kws_list)
    return kws_list


def kws_test():
    title = '英国脱欧首相卡梅伦宣布辞职 外媒称卡梅伦是罪人'
    kws1 = get_title_keywords(title)
    
    title = '英国脱欧首相辞职 将对美欧TTIP谈判有何影响'
    kws2 = get_title_keywords(title)
    
    has_common_keyword(kws1, kws2)


if __name__ == "__main__":
 
    starttime = datetime.datetime.now()
    fin = open('./url_title_20.txt')
    word_list = []
    title_list = []
    kws_dict = {}
    for line in fin:
        line = line.strip()
        arr = line.split('\t')
        title = arr[1]
        title_list.append(title)
        #kws = list(set(arr[4].strip('|').split('|')))
        kws = get_text_keyword(title)
        kws_dict[title] = kws
        if len(unicode(title.decode('utf-8'))) > 4:
            if (title.strip(), kws) not in word_list:
                word_list.append((title.strip(), kws))
    
    len_title_list = len(set(title_list))
    print 'title count:', len_title_list
    
    result_list, rest_title_cnt = run_merge(word_list)
    
    endtime = datetime.datetime.now()
    time_elp = (endtime - starttime).seconds
    print "all run time is : %.03f minutes" % (time_elp * 1.0 / 60)
    
    print '\ncompletely.....'
    
    fout = open('merge_result.dat', 'w')
    
    result_list.sort(lambda x,y:cmp(len(x), len(y)), reverse = True) 
    k = 0
    for s in result_list:
        fout.write('\n\n\n***************************\n')
        fout.write('id:' + str(k) + '\t count:' + str(len(s)) + '\nkeys:')
        key_list = get_keyword_of_cluster(s)
        for key in key_list:
            #print key.encode('utf-8')
            fout.write(key.encode('utf-8') + '\t')
        fout.write('\n*********************************\n')
        k += 1
        for bucket in s:
            fout.write('*********************************\n')
            for title in bucket:
                fout.write(title + '\n')
            
            

