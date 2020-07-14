import requests,re,base64,os
from lxml import etree
from fontTools.ttLib import TTFont
class Spider_58(object):
    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }

    def get_house_info(self,most_dict):
        most_dict2=most_dict.copy()  #建立副本储存变更后的条件
        if most_dict2['model'][:2] == '整租':   #由于整租和合租网页结构不同，所以分开
            # 'https: // zz.58.com / zufang /'
            url=most_dict2['begin_url'].split('.')[0]+'.58.com/zufang/'
        else:
            url = most_dict2['begin_url'].split('.')[0]+'.58.com/hezu/'
        res = self.session.get(url)
        page=etree.HTML(res.text)

        kw_path_dict={}   #生成一个关键词与路径的对照表，以下操作主要是添加关键词：路径，以及将most_dict2的信息转换成关键字，以便后续匹配路径，构造url

        # 地区
        districts = page.xpath('//dl[@class="secitem secitem_fist"]/dd/a/text()')[1:]  # 关键词名字
        paths = page.xpath('//dl[@class="secitem secitem_fist"]/dd/a/@href')[1:]  # 关键词路径
        for index, district in enumerate(districts):
            #有的地区后面带区字，有的不带，烦死了，干脆都做一份
            kw_path_dict[district] = paths[index].split('/')[3]
            kw_path_dict[district[:-1]] = paths[index].split('/')[3]
            kw_path_dict[district+'区'] = paths[index].split('/')[3]

        # 价格
        prices = page.xpath('//dl[@id="secitem-rent"]/dd/a/text()')[1:]
        paths = page.xpath('//dl[@id="secitem-rent"]/dd/a/@href')[1:]
        for index, price in enumerate(prices):
            kw_path_dict[price] = paths[index].split('/')[-2]
        # 判断价格属于那个范围
        price_num = int(most_dict2["price"][:-3])
        if price_num <= int(prices[0][:-3]):
            most_dict2['price'] = prices[0]
        for i in prices[1:-1]:
            if price_num > int(i.split('-')[0]):
                most_dict2['price'] = i
        if price_num > int(prices[-1][:-3]):
            most_dict2['price'] = prices[-1]

        #整租是几室，合租是主卧，次卧
        types = page.xpath('//dd[@id="secitem-room"]/a/text()')[1:]
        paths = page.xpath('//dd[@id="secitem-room"]/a/@href')[1:]
        for index, type in enumerate(types):
            kw_path_dict[type] = paths[index].split('/')[-2]

        if most_dict2['model'][:2] == '整租':
            t = most_dict2['type'][0]
            if t=='1': most_dict2['type']='一室'
            elif t == '2': most_dict2['type'] = '二室'
            elif t == '3': most_dict2['type'] = '三室'
            elif t == '4': most_dict2['type'] = '四室'
            else: most_dict2['type'] = '四室以上'

        else:
            mt=most_dict2['type'][2:]
            if mt=='主卧':most_dict2['type'] = '主卧'
            else: most_dict2['type'] = '次卧'

        #朝向
        directions = page.xpath('//div[@id="secitem-direction"]/a/text()')[1:]
        paths = page.xpath('//div[@id="secitem-direction"]/a/@href')[1:]
        for index, direction in enumerate(directions):
            direction=direction.strip()
            kw_path_dict[direction] = paths[index].split('/')[-2]
        most_dict2['direction']= most_dict2['direction'][:-1]

        #构造url
        # 'https://zz.58.com/jinshui/zufang/b3j2d2/'
        # 'https://sh.58.com/pudongxinqu/hezu/k1c1d2/'
        if most_dict2['model'][:2]=='整租':
            url='https://zz.58.com/{}/zufang/{}{}{}/'\
                .format(kw_path_dict[most_dict2['district']],kw_path_dict[most_dict2['price']],kw_path_dict[most_dict2['type']],kw_path_dict[most_dict2['direction']])

        else:
            url='https://zz.58.com/{}/hezu/{}{}{}/'\
                .format(kw_path_dict[most_dict2['district']],kw_path_dict[most_dict2['price']],kw_path_dict[most_dict2['type']],kw_path_dict[most_dict2['direction']])
        print(url)
        res=self.session.get(url)
        page = etree.HTML(res.text)

        #处理字体反爬
        font_text = re.findall(r"\@font-face\{font-family:'fangchan-secret';src:url\('data:application/font-ttf;charset=utf-8;base64,(.*?)'\) format\('truetype'\)",res.text)[0]
        font_path=os.path.join(os.path.dirname(__file__) + '/58同城字体.ttf')
        with open(font_path, 'wb')as f:
            f.write(base64.b64decode(font_text.encode()))
        font = TTFont(font_path)

        def transCharByFont(font: TTFont, string: str):
            dict = font.getBestCmap()
            final_string = ''
            for char in string:  # 判断字符是否经过字体反爬
                unicode = ord(char)
                if unicode in dict:
                    glyph = dict[unicode]
                    char = font.getReverseGlyphMap()[glyph] - 1  # 通过对应关系找出原来值
                final_string += str(char)
            return final_string

        # 匹配相应信息，返回信息列表
        all_li=page.xpath('//ul[@class="house-list"]/li')[:-1]
        info_list=[]
        for li in all_li:
            info_dict={}
            link_url=li.xpath('./div/h2/a/@href')[0]
            img_url=li.xpath('./div[@class="img-list"]/a/img/@lazy_src')[0].replace('"','')
            title = li.xpath('./div/h2/a/text()')[0].strip()
            price=li.xpath('./div[@class="list-li-right"]/div[@class="money"]')[0].xpath('string(.)').strip()
            main_info=li.xpath('./div[@class="des"]/p[@class="room"]/text()')[0].strip().replace(' ','').replace('\xa0','')
            location=li.xpath('./div[@class="des"]/p[@class="infor"]')[0].xpath('string(.)').replace(' ','').replace('\xa0','').replace('\n','')

            title = transCharByFont(font, title)
            price = transCharByFont(font, price)
            main_info = transCharByFont(font, main_info)
            location = transCharByFont(font, location)

            info_dict['link_url']=link_url
            info_dict['img_url']=img_url
            info_dict['title']=title
            info_dict['price']=price
            info_dict['main_info']=main_info
            info_dict['location']=location
            info_list.append(info_dict)
        return info_list

if __name__ == '__main__':
    most_dict = {'price': '1516元/月', 'type': '1室1厅', 'district': '经开', 'model': '整租', 'area': '48平米',
                 'direction': '南向', 'begin_url': 'https://zz.zu.fang.com'}
    a = Spider_58()
    print(a.get_house_info(most_dict))