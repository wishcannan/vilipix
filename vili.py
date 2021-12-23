import os
import requests
import vili_thread
import time

# VI = vili_thread
class vili():
    def __init__(self) -> None:
        self.headers = {
            "Cookie":'auth.strategy=local; Hm_lvt_7246eb56b79171a6fe5284a8bf523aa0=1639670733; Hm_lpvt_7246eb56b79171a6fe5284a8bf523aa0=1639670918',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        }
        self.tag_api_url = 'https://www.vilipix.com/api/illust/tag/{}'#根据tag爬取
        self.userid_api_url = 'https://www.vilipix.com/api/illust'#根据画师id爬取
        self.filename = './image/'
        if not os.path.exists(self.filename):
            os.mkdir(self.filename)


    def tag_find(self,tag):
        filename = self.filename + tag + '/'
        if not os.path.exists(filename):
            os.mkdir(filename)
        alist = []#申请一辆空车
        pn = 0
        n = 1
        start_time = time.time()
        while True:
            params = {
                'limit':30,
                'offset':pn
            }
            r = requests.get(self.tag_api_url.format(tag),params=params,headers=self.headers)
            if r.status_code == 200:
                a = vili_thread.vi_thread(n,r.json(),tag,filename)
                alist.append(a)
            else:
                break
            pn += 30
            n += 1
        #装填完毕
        print('{}发车,这次共计{}页'.format(tag,len(alist)))
        for i in alist:
            i.start()
        for i in alist:
            i.join()
        print('一共用时:', time.time()-start_time)

    def userid_find(self,userid:int):#麻了 这个错误访问页数 他也给你正常返回200 之前写的识别方式就不能用
        filename = self.filename + str(userid) + '/'
        if not os.path.exists(filename):
            os.makedirs(filename)
        alist = []
        pn = 0
        #我希望一次只有最多10条线程并发运行 在之前版本里 我其实让有多少页就有多少线程并发运行 确实很快 不够显得不够
        #优雅 我会在最后一个版本里 尝试用线程池来实现 这里呢我希望简简单单的实现一下控制并发运行数量
        start_time = time.time()
        while True:
            n = 1
            while n % 11 != 0:
                params = {
                    'user_id':userid,
                    'limit':30,
                    'offset':pn
                }
                r = requests.get(self.userid_api_url,params=params,headers=self.headers)
                a = r.json()
                if len(a['rows']) != 0:
                    a = vili_thread.vi_thread(n,a,str(userid),filename)
                    alist.append(a)
                else:
                    self.depart(userid,alist)
                    print('一共用时:', time.time()-start_time)#最后一定会在这里结束
                    return
                r.close()
                n += 1
                pn += 30
            self.depart(userid,alist)
            alist = []#清空车
            
    
    def depart(self,name,alist):#这个alist里面不是线程 就报错讲真
        name = str(name)
        print('{}发车,这次共计{}页'.format(name,len(alist)))
        if len(alist) == 0:
            print("是不是有鬼上车了")
        else:
            for i in alist:
                i.start()
            for i in alist:
                i.join()

    def ex(self,uid):
        pn = 60
        params = {
            'user_id':uid,
            'limit':30,
            'offset':pn
        }
        r = requests.get(self.userid_api_url,params=params,headers=self.headers)
        print(r.headers)
        print(r.status_code)
        print(r.text)





V = vili()
# V.tag_find('黒タイツ')
V.userid_find(19440186)
# V.ex(19440186)
