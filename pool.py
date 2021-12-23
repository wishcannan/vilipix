from concurrent.futures import ThreadPoolExecutor
import time
from types import TracebackType
import requests
import os
from bs4 import BeautifulSoup
import re

'''
    我希望这个也能作为一个接口 用户传json过来 我将任务完成 就对外暴露一个接口
'''


class t_pool():
    def __init__(self,alist,filename) -> None:
        self.data = alist
        self.filename = filename
        self.headers = {
            "Cookie":'auth.strategy=local; Hm_lvt_7246eb56b79171a6fe5284a8bf523aa0=1639670733; Hm_lpvt_7246eb56b79171a6fe5284a8bf523aa0=1639670918',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        }
        self.ill_id_url = 'https://www.vilipix.com/illust/{}'#根据作品id

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

    def done(self):
        #alist 里面初步想的是塞json对象进去然后我挨个遍历 塞入进程池里面 工作
        #这个方法就是实现 一个alist的进入进程池的过程
        executor = ThreadPoolExecutor(max_workers=2)#创建一个最大线程数为2的线程池
        print("线程注入")
        # for data in executor.map(self.get_html,self.data):
        #     print("succes get page")这个data只是取结果用的 没什么用
        executor.map(self.get_html,self.data)
        executor.shutdown()
        print("线程池关闭")

    def get_html(self,a):
        # print(a)
        #a 实际就是一个单独的json对象 这个里面 要对他做个小小的处理
        for i in a['rows']:
            print(i['id'])
            self.illust_url(i['id'],self.filename)



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
                        # print(b[0].a.img['src'])
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
