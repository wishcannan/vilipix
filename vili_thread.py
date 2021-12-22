import threading
import re
import requests
import os
from bs4 import BeautifulSoup



'''
我希望这可以作为一个接口 对外暴露 其他文件只用调用这个接口 传过来一组固定格式的数据 然后这个就完成下载图片
这里又会出现一个储存的问题 我是没有检索功能 这个网站的检索功能也只支持tag or userid简直不好用 无法对
单张图片进行检索 如果要单张索引的话 可就要根据i['id'] https://www.vilipix.com/illust/{} 这样来查询 
其实我们直接返回的api 里面json只有一个头图 要爬完就还得 访问 这个链接 然后爬取
'''

class vi_thread(threading.Thread):
    def __init__(self,threadid,text,tag,filename):
        threading.Thread.__init__(self)
        self.threadID = threadid
        self.tt = text
        self.tag = tag
        self.filename = filename
        self.headers = {
            "Cookie":'auth.strategy=local; Hm_lvt_7246eb56b79171a6fe5284a8bf523aa0=1639670733; Hm_lpvt_7246eb56b79171a6fe5284a8bf523aa0=1639670918',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        }
        self.ill_id_url = 'https://www.vilipix.com/illust/{}'#根据作品id

    def run(self):
        # pattern = r'(.*)\.(.*)'
        print('{}号小火车的{}页发车了'.format(self.tag,self.threadID))
        # print(self.tt)
        for i in self.tt['rows']:
            # matchObj = re.search(pattern,i['url'],re.M|re.I)
            # self.downimage(i['url'],i['id'])
            self.illust_url(i['id'],self.filename)
        print('{}号小火车的{}页已经到站'.format(self.tag,self.threadID))

    def downimage(self,url,uid,style,filename):
        try:
            r = requests.get(url,headers=self.headers)
            if r.status_code == 200:
                # print(filename+title+uid+'.'+style)
                with open(filename+str(uid)+'.'+style,'wb') as f:
                    f.write(r.content)
                r.close()
            else:
                print(r.status_code,url)
        except Exception as e:
            print("有点问题呢",e)
    
    def illust_url(self,uid,filename=None):
    #实现从https://www.vilipix.com/illust/{}中提取主图片
    # if type(uid) == 'str':
        uid = int(uid)
        pattern = r'(.*)\.(.*)\?'
        if not filename:
            filename = self.filename + 'ex/'
            if not os.path.exists(filename):
                os.mkdir(filename)
        ill_url = self.ill_id_url.format(uid)
        r = requests.get(ill_url)
        if r.status_code == 200:
            stoop = BeautifulSoup(r.text,'html.parser')
            a = stoop.find('div',class_='illust-continaer')
            if a != None:
                b = a.div.main.div.ul.find_all('li')
                if b != None:
                    if len(b) == 1:
                        img_url = b[0].a.img['src']
                        matchObj = re.search(pattern,img_url,re.M|re.I)
                        self.downimage(img_url,uid,matchObj.group(2),filename)
                    else:
                        pd = 0
                        for i in b:
                            img_url = i.a.img['src']
                            matchObj = re.search(pattern,img_url,re.M|re.I)
                            # print(img_url)
                            puid = str(uid)+ '_p' + str(pd)
                            self.downimage(img_url,puid,matchObj.group(2),filename)
                            pd += 1
                else:
                    print("又出问题了 这次是网页结构有问题")
            else:
                print("这次网页自己有问题")
        r.close()