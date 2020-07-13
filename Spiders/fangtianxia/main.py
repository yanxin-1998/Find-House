import requests,re
from lxml import etree


class Ftx(object):
    def __init__(self,most_dict):
        self.most_dict = most_dict
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }

    def get_house_info(self):
        if self.most_dict['model'][:2] == '整租':   #由于整租和合租网页结构不同，所以分开
            url=self.most_dict['begin_url']
            res = self.session.get(url)
        else:
            url = self.most_dict['begin_url']+'/hezu'
            res = self.session.get(url)
            url=re.findall('href="(.*?)">点击跳转</a>', res.text)[0]
            res = self.session.get(url)

        page=etree.HTML(res.text)
        kw_path_dict={}   #生成一个关键词与路径的对照表，以下操作主要是添加关键词：路径，以及将most_dict的信息转换成关键字，以便后续匹配路径，构造url

        #地区
        districts=page.xpath('//dl[@class="search-list clearfix"][1]/dd/a/text()')[1:] #关键词名字
        paths = page.xpath('//dl[@class="search-list clearfix"][1]/dd/a/@href')[1:]  #关键词路径
        for index, district in enumerate(districts):  # "/hezu-a0153/"
            kw_path_dict[district] = paths[index].split('/')[1].split('-')[1]


        #价格
        prices = page.xpath('//dl[@id="rentid_D04_02"]/dd/a/text()')[1:]
        # print(prices)
        paths = page.xpath('//dl[@id="rentid_D04_02"]/dd/a/@href')[1:]
        for index, price in enumerate(prices):  # "/house/c20-d2500/"
            kw_path_dict[price] = paths[index].split('/')[-2]

        #判断价格属于那个范围
        price_num = int(self.most_dict["price"][:-3])
        if price_num <= int(prices[0][:-3]):
            self.most_dict['price']=prices[0]
        for i in prices[1:-1]:
            if price_num > int(i.split('-')[0]):
                self.most_dict['price']=i
        if price_num > int(prices[-1][:-3]):
            self.most_dict['price']=prices[-1]

        #整租是几居，合租是几户
        types = page.xpath('//dl[@id="rentid_D04_03"]/dd/a/text()')[1:]
        paths = page.xpath('//dl[@id="rentid_D04_03"]/dd/a/@href')[1:]
        for index, type in enumerate(types):  # "/house/g21/"
            kw_path_dict[type] = paths[index].split('/')[-2]

        t=self.most_dict['type'][0]
        if self.most_dict['model'][:2] == '整租':
            if t=='1': self.most_dict['type']='一居'
            elif t == '2': self.most_dict['type'] = '二居'
            elif t == '3': self.most_dict['type'] = '三居'
            elif t == '4': self.most_dict['type'] = '四居'
            else: self.most_dict['type'] = '四居以上'

            #朝向，合租和整租页面xpath匹配不同
            directions = page.xpath('//dl[@class="search-list clearfix"][5]/dd/a/text()')[1:]
            paths = page.xpath('//dl[@class="search-list clearfix"][5]/dd/a/@href')[1:]
            for index, direction in enumerate(directions):  # "/house/p21/"
                kw_path_dict[direction] = paths[index].split('/')[-2]

        else:
            if t=='2': self.most_dict['type']='二户'
            elif t == '3': self.most_dict['type'] = '三户'
            elif t == '4': self.most_dict['type'] = '四户'
            elif t == '5': self.most_dict['type'] = '五户'
            else: self.most_dict['type'] = '五户以上'

            directions = page.xpath('//dl[@class="search-list clearfix"][6]/dd/a/text()')[1:]
            paths = page.xpath('//dl[@class="search-list clearfix"][6]/dd/a/@href')[1:]
            for index, direction in enumerate(directions):  # "/house/p21/"
                kw_path_dict[direction] = paths[index].split('/')[-2]

            self.most_dict['model_type']=self.most_dict['model'][2:]
            model_types = page.xpath('//dl[@id="rentid_D04_09"]/dd/a/text()')[1:]
            paths = page.xpath('//dl[@id="rentid_D04_09"]/dd/a/@href')[1:]
            for index, model_type in enumerate(model_types):  # "/hezu/n32/"
                kw_path_dict[model_type] = paths[index].split('/')[-2]

        d=self.most_dict['direction'][:-1]
        if d=='南北': self.most_dict['direction']='南北通透'
        elif d=='东西': self.most_dict['direction']='东西向'
        elif d=='南': self.most_dict['direction']='朝南'
        elif d == '北':self.most_dict['direction'] = '朝北'
        elif d == '东': self.most_dict['direction'] = '朝东'
        else : self.most_dict['direction']='朝西'

        'https://gz.zu.fang.com/house-a084/c2500-d21000-g23-p23-n31/'
        'https://hz.zu.fang.com/hezu-a0154/c2500-d21000-p23-n33-d52/'
        #构造url
        if self.most_dict['model'][:2]=='整租':
            url=self.most_dict['begin_url']+'/house-'+kw_path_dict[self.most_dict['district']]+'/'+kw_path_dict[self.most_dict['price']]+'-'+kw_path_dict[self.most_dict['type']]+'-'+kw_path_dict[self.most_dict['direction']]+'-n31/'
            res = self.session.get(url)
            url = re.findall('href="(.*?)">点击跳转</a>', res.text)[0]
        else:
            url=self.most_dict['begin_url']+'/hezu-'+kw_path_dict[self.most_dict['district']]+'/'+kw_path_dict[self.most_dict['price']]+'-'+kw_path_dict[self.most_dict['direction']]+'-'+kw_path_dict[self.most_dict['model_type']]+'-'+kw_path_dict[self.most_dict['type']]+'/'

        res=self.session.get(url)
        page = etree.HTML(res.text)

        #匹配相应信息，返回信息列表
        all_dl=page.xpath('//div[@class="houseList"]/dl')
        info_list=[]
        for i in all_dl:
            info_dict={}
            link_url=self.most_dict['begin_url']+i.xpath('./dd/p[@class="title"]/a/@href')[0]
            img_url=i.xpath('./dt/a/img/@onerror')[0].replace("imgiserror(this,'",'').replace("')",'')
            title = i.xpath('./dd/p[@class="title"]/a/text()')[0]
            price=i.xpath('./dd/div[@class="moreInfo"]')[0].xpath('string(.)').strip()
            main_info=i.xpath('./dd/p[@class="font15 mt12 bold"]')[0].xpath('string(.)').strip().replace('�O','平米')
            location=page.xpath('//div[@class="houseList"]/dl/dd/p[@class="gray6 mt12"]')[0].xpath('string(.)')

            info_dict['link_url']=link_url
            info_dict['img_url']=img_url
            info_dict['title']=title
            info_dict['price']=price
            info_dict['main_info']=main_info
            info_dict['location']=location
            info_list.append(info_dict)
        return info_list


if __name__ == '__main__':
    most_dict={'price': '2000元/月', 'type': '1室1厅', 'district': '滨江', 'model': '整租', 'area': '15.0平米', 'direction': '南向', 'begin_url': 'https://hz.zu.fang.com'}
    a=Ftx(most_dict)
    a.get_house_info()