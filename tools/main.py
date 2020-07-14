import json
import os
import wx
import time
from selenium import webdriver
from selenium.webdriver import ChromeOptions

import sys

MAIN_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
print(MAIN_FILE_PATH)
BASE_PATH = os.path.dirname(MAIN_FILE_PATH)
print(BASE_PATH)
sys.path.append(os.path.join(BASE_PATH, "./Spiders/"))
DATA_DIR = os.path.join(BASE_PATH, "./data")
try:
    print(DATA_DIR)
    os.mkdir(DATA_DIR)
except OSError:
    pass

from fangtianxia.fav_info import Ftx_fav
from fangtianxia.main import Ftx
from city58.main import Spider_58

class Spider_all(object):
    def crawl_all(self,most_dict):
        a=Ftx()
        ftx=a.get_house_info(most_dict)

        try:
            b=Spider_58()
            c58=b.get_house_info(most_dict)
        except:
            c58=[]
            print('58同城需要验证，或ip被封')

        all_info=[]
        all_info.extend(ftx)
        all_info.extend(c58)
        return all_info

    def gen_html(self,info:list):
        content=''
        for i in info:
            content+='<div><span class="right">{}</span><a href="{}"><img src="{}" /></a><p class=title><a href="{}">{}</a></p><p>{}</p><p>{}</p></div>'\
            .format(i['price'],i['link_url'],i['img_url'],i['link_url'],i['title'],i['main_info'],i['location'])

        framework ='<!DOCTYPE html><html><head><meta charset="utf-8" /><title></title><style>body{font-family:"Arial";}' \
                   'a{text-decoration:none;color: black;}p{font-size:18px;}img{width:200px;height:150px;float:left;margin-right: 15px;}' \
                   'div{clear:both;height:150px;width:860px;}.right{float:right;font-size:20px;font-weight:bolder;color:crimson;margin-top:50px;}' \
                   '.title{font-weight: bolder;} #content{margin:auto;}</style></head><body><div id="content">'+content+'</div></body></html>'

        with open(DATA_DIR+'/Housing-Resource.html','w',encoding='utf-8') as f:
            f.write(framework)

    def save_json(self,info:list):
        with open(DATA_DIR+'/Housing-Resource.json','w',encoding='utf-8') as f:
            json.dump(info,fp=f)


class Button:
    frame = None
    def __init__(self, frame, pnl, item):
        pic_jd = wx.Image(item.img, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        btn_jd = wx.BitmapButton(pnl, -1, pic_jd, pos=(item.x, item.y), size=(100, 100))
        wx.StaticText(pnl, -1, item.title, pos=(item.x + 30, item.y + 110))
        self.frame = frame
        self.frame.Bind(wx.EVT_BUTTON, self.OnClick, btn_jd)

    def Automation(self, url):
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.driver = webdriver.Chrome(options=option)
        url = str(url)
        self.driver.get(url)

    def updateStatus(self, frame, status):
        if status == 0:
            frame.SetStatusText("爬取中...", 1)
        elif status == 1:
            self.driver.quit()
            frame.SetStatusText("你的收藏中没有租房信息，终止爬取", 1)
        elif status == 2:
            frame.SetStatusText("爬取成功", 1)
        else:
            self.driver.quit()
            frame.SetStatusText("爬取失败！", 1)

class FangtianxiaButton(Button):
    def OnClick(self, event):
        try:
            self.updateStatus(self.frame,0)
            url='https://passport.fang.com/?backurl=https%3A%2F%2Fwww.fang.com%2F'
            self.Automation(url)
            while 1:
                time.sleep(0.2)
                if self.driver.current_url[:16]!='https://passport':
                    get_cookies = self.driver.get_cookies()
                    cookie_str = ''
                    for s in get_cookies:
                        cookie_str = cookie_str + s['name'] + '=' + s['value'] + ';'
                    self.driver.quit()
                    break
            try:
                #抓取使用者房天下网站收藏的租房信息
                a=Ftx_fav(cookie_str)
                fav_info=a.get_fav_info()
                # a.save_fav_info(fav_info,os.path.join(BASE_PATH,'./Spiders/fangtianxia'))
                #判断使用者的收藏中是否有租房信息
                if len(fav_info)>0:
                    # 分析数据，找出最符合使用者的租房条件
                    most_dict=a.gen_most_dict(fav_info)
                    print(most_dict)
                    #根据租房条件抓取各大租房网站的房源信息
                    b=Spider_all()
                    info=b.crawl_all(most_dict)
                    #生成HTML页面
                    b.gen_html(info)
                    # b.save_json(info)
                    self.Automation(os.path.join(DATA_DIR, './Housing-Resource.html'))
                    self.updateStatus(self.frame, 2)
                else:
                    self.updateStatus(self.frame, 1)
            except Exception:
                self.updateStatus(self.frame,3)
        except Exception:
            self.updateStatus(self.frame,3)

class Item:
    x = 0
    y = 0
    title = ''
    img = ''
    def __init__(self, x, y, title, img):
        self.x = x
        self.y = y
        self.title = title
        self.img = img

class CreateFrame(wx.Frame):
    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(CreateFrame, self).__init__(*args, **kw)

        # create a panel(面板)
        self.pnl = wx.Panel(self)

        # create status bar(状态栏）
        statusBar = self.CreateStatusBar()
        statusBar.SetFieldsCount(2) #分两栏
        statusBar.SetStatusWidths([-3, -2]) #两栏宽度是3:2

        # create buttons
        start_x = 50
        start_y = 25
        xstep = 200
        ystep = 150
        FangtianxiaButton(self, self.pnl, Item(start_x, start_y, '房天下',
            'resource/icon/ftx.png'))

if __name__ == '__main__':
    app = wx.App()
    frm = CreateFrame(None, title='Find-House', size=(400, 600))
    frm.Show()
    app.MainLoop()
