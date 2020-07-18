import requests,re,os,base64,xlsxwriter
from lxml import etree
from collections import Counter
from fontTools.ttLib import TTFont

class C58_fav(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
        }

    # 处理字体反爬
    def transCharByFont(self,font: TTFont, string: str):
        dict = font.getBestCmap()
        final_string = ''
        for char in string:  # 判断字符是否经过字体反爬
            unicode = ord(char)
            if unicode in dict:
                glyph = dict[unicode]
                char = font.getReverseGlyphMap()[glyph] - 1  # 通过对应关系找出原来值
            final_string += str(char)
        return final_string

    def get_fav_info(self,url_ls):
        all_info_list = []
        try:
            for url in url_ls:
                res=requests.get(url,headers=self.headers)
                # 下载字体文件
                font_text = re.findall(r"\@font-face\{font-family:'fangchan-secret';src:url\('data:application/font-ttf;charset=utf-8;base64,(.*?)'\) format\('truetype'\)",res.text)[0]
                font_path = os.path.join(os.path.dirname(__file__) + '/58同城字体.ttf')
                with open(font_path, 'wb')as f:
                    f.write(base64.b64decode(font_text.encode()))
                font = TTFont(font_path)

                page = etree.HTML(res.text)
                info_dict = {}
                info=page.xpath('//ul[@class="f14"]/li/span[2]/text()')

                info_dict['title'] = page.xpath('//h1/text()')[0]  # 标题
                info_dict['model'] = info[0]  # 出租方式
                info_dict['price'] = self.transCharByFont(font,page.xpath('//b[@class="f36 strongbox"]/text()')[0])+'元/月'  # 租金
                info_dict['type'] =self.transCharByFont(font,info[1].split('\xa0\xa0')[0])  # 户型
                info_dict['area'] =self.transCharByFont(font,info[1].split('\xa0\xa0')[1].split(' ')[0]) + '平米'  # 面积
                info_dict['direction'] =self.transCharByFont(font,info[2].split('\xa0\xa0')[0])+'向'  # 朝向
                info_dict['district'] =page.xpath('//ul[@class="f14"]/li/span[2]')[4].xpath('./a[1]/text()')[0]  # 区域
                info_dict['url'] = url  # 链接
                all_info_list.append(info_dict)
        except:
            print('58同城需要验证或ip被封')

        return all_info_list

    def gen_most_dict(self,info_list):  #找出最有可能的条件
        prices=[]   #租金
        types = []  # 户型
        areas = []  # 面积
        models = []  # 出租方式
        directions = []  # 朝向
        districts = []  # 地区

        for info in info_list:
            prices.append(int(info['price'][:-3]))
            types.append(info['type'])
            areas.append(float(info['area'][:-2]))
            if len(info['model'])>2: models.append(info['model'].split(' - ')[0]+info['model'].split(' - ')[1])
            else: models.append(info['model'])
            directions.append(info['direction'])
            districts.append(info['district'])

        most_dict={}
        sum_price,sum_area=0,0
        for price in prices: sum_price+=price
        for area in areas: sum_area+=area
        most_dict['price'] =str(int(sum_price/len(prices)))+'元/月'
        most_dict['area'] = str(int(sum_area/len(areas)))+'平米'
        most_dict['type'] = Counter(types).most_common()[0][0]
        most_dict['district'] = Counter(districts).most_common()[0][0]
        most_dict['model'] = Counter(models).most_common()[0][0]
        most_dict['direction'] = Counter(directions).most_common()[0][0]
        for i in info_list:
            if i['district']==most_dict['district']:   #此处begin_url是为了判断是哪个地区的页面
                most_dict['begin_url'] =i['url'].split('/')[0]+'//'+i['url'].split('/')[2].split('.')[0]
                break
        return most_dict

    def save_fav_info(self,info_list,dir_path=None):  #保存个人收藏信息为xlsx
        if dir_path:
            file_path = os.path.join(dir_path,'./58_fav.xlsx')
        else:
            file_path='./58_fav.xlsx'
        book = xlsxwriter.Workbook(file_path)
        sheet = book.add_worksheet()
        sheet.write(0, 0, '标题')
        sheet.write(0, 1, '租金')
        sheet.write(0, 2, '户型')
        sheet.write(0, 3, '面积')
        sheet.write(0, 4, '出租方式')
        sheet.write(0, 5, '朝向')
        sheet.write(0, 6, '地区')
        sheet.write(0, 7, '链接')

        for index, info in enumerate(info_list):
            sheet.write(index + 1, 0, info['title'])
            sheet.write(index + 1, 1, info['price'])
            sheet.write(index + 1, 2, info['type'])
            sheet.write(index + 1, 3, info['area'])
            sheet.write(index + 1, 4, info['model'])
            sheet.write(index + 1, 5, info['direction'])
            sheet.write(index + 1, 6, info['district'])
            sheet.write(index + 1, 7, info['url'])