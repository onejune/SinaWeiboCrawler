#coding=utf-8
import os, sys, redis, time, datetime
time_now = time.strftime('%Y-%m-%d %H', time.localtime(time.time()))
redis_server = redis.Redis(host = '112.126.67.205', port = 6379, db = 1)
starttime = datetime.datetime.now()
a = ''
for i in range(0, 100000):
    redis_server.delete(i)

endtime = datetime.datetime.now()
print (endtime - starttime).seconds
