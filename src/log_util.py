#coding=utf-8
import os, sys, logging, traceback, time

'''
使用方法：logger = Logger(log_level=1, logger="fox").get_logger()
'''

#用字典保存日志级别
format_dict = {
   1 : logging.Formatter('[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(funcName)s] [%(name)s] [%(levelname)s] %(message)s'),
   2 : logging.Formatter('[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(funcName)s] [%(name)s] [%(levelname)s] %(message)s'),
   3 : logging.Formatter('[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(funcName)s] [%(name)s] [%(levelname)s] %(message)s'),
   4 : logging.Formatter('[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(funcName)s] [%(name)s] [%(levelname)s] %(message)s'),
   5 : logging.Formatter('[%(asctime)s] [%(filename)s] [line:%(lineno)d] [%(funcName)s] [%(name)s] [%(levelname)s] %(message)s')
}

class Logger():
    #只要logger相同，就能得到同一个logger实例
    def __init__(self, log_level, logger, log_file):
        '''
                       指定保存日志的文件路径，日志级别，以及调用文件
                       将日志存入到指定的文件中
        '''
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = format_dict[int(log_level)]
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        #self.logger.addHandler(ch)

    
    def get_logger(self):
        return self.logger
    
    
    
    