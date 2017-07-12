# -*- coding:UTF-8 -*-
import urllib
import hashlib
import rsa
import binascii
import string
import base64
import getdata

class data_deal:
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.gd = getdata.GET_DATA()
        self.nonce,self.rsakv,self.servertime,self.pubkey = self.gd.get_data() 

    #获取nonce
    def get_nonce(self):
        return self.nonce

    #获取servername
    def get_servername(self):
        return self.servertime

    #获取 rsakv
    def get_rsakv(self):
        return self.rsakv
    
    #username 经过了BASE64 计算：
    #username = base64.encodestring( urllib.quote(username) )[:-1]    
    def get_username(self):
        username_ = urllib.quote(self.username)
        username = base64.encodestring(username_)[:-1]
        return username

    #password经过rsa加密
    def get_pwd(self):
        rsaPublickey = int(self.pubkey,16)
        key = rsa.PublicKey(rsaPublickey,65537)
        
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        pwd_ = rsa.encrypt(message,key)
        pwd = binascii.b2a_hex(pwd_)
        return pwd
        
    def print_data(self):
        print self.nonce
        print self.rsakv
        print self.servertime
        print self.pubkey
