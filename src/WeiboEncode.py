#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import base64
import rsa
import binascii

def PostEncode(userName, passWord, serverTime, nonce, pubkey, rsakv):
    "Used to generate POST data"

    encodedUserName = GetUserName(userName)#�û���ʹ��base64����
    encodedPassWord = get_pwd(passWord, serverTime, nonce, pubkey)#Ŀǰ�������rsa����
    postPara = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'userticket': '1',
        'ssosimplelogin': '1',
        'vsnf': '1',
        'vsnval': '',
        'su': encodedUserName,
        'service': 'miniblog',
        'servertime': serverTime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'sp': encodedPassWord,
        'encoding': 'UTF-8',
        'prelt': '115',
        'rsakv': rsakv,     
        'door': '2341',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
    }
    postData = urllib.urlencode(postPara)#�������
    return postData


def GetUserName(userName):
    "Used to encode user name"

    userNameTemp = urllib.quote(userName)
    userNameEncoded = base64.encodestring(userNameTemp)[:-1]
    return userNameEncoded


def get_pwd(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537) #������Կ
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #ƴ������js�����ļ��еõ�
    passwd = rsa.encrypt(message, key) #����
    passwd = binascii.b2a_hex(passwd) #��������Ϣת��Ϊ16���ơ�
    return passwd

