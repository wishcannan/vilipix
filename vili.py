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
        start_time = time.time()
        print('{}发车,这次共计{}页'.format(tag,len(alist)))
        for i in alist:
            i.start()
        for i in alist:
            i.join()
        print('一共用时:', time.time()-start_time)

V = vili()
V.tag_find('黒タイツ')