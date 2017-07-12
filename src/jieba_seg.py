#encoding=utf-8
import sys
sys.path.append("../")

import jieba
import jieba.posseg
import jieba.analyse

print('='*40)
print('-'*40)


words = jieba.posseg.cut("气场太强，感觉要被撞到地上。文章版少帅张学良，总是跳戏")
for word, flag in words:
    print('%s %s' % (word, flag))


print('='*40)
print('-'*40)


result = jieba.tokenize(u'气场太强，感觉要被撞到地上。文章版少帅张学良，总是跳戏')
for tk in result:
    print("word %s\t\t start: %d \t\t end:%d" % (tk[0],tk[1],tk[2]))








