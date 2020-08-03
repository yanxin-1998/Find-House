import requests,re,os,xlsxwriter
from lxml import etree
from collections import Counter

class Ftx_fav(object):
    def __init__(self, cookie):
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }
        cookie_dict = {}
        list = cookie.split(';')
        for i in list:
            try:
                cookie_dict[i.split('=')[0]] = i.split('=')[1]
            except IndexError:
                cookie_dict[''] = i
        requests.utils.add_dict_to_cookiejar(self.session.cookies, cookie_dict)

    def get_fav_info(self):  #取得个人收藏信息
        res=self.session.get('https://my.fang.com/MyCollect/Index.html',headers=self.headers)
        page=etree.HTML(res.text)
        all_info_list=[]

        prices = page.xpath('//div[@class="collect_right"]/b/text()')
        divs=page.xpath('//div[@class="collect_info"]')
        count = 0
        for index,div in enumerate(divs):
            count+=1
            try:
                info_dict={}
                p_text = div.xpath('.//p/text()')
                p1_text = p_text[0].split('\xa0\xa0')
                p2_text = p_text[1].split('\xa0\xa0')

                info_dict['title'] = div.xpath('./b/a/text()')[0]  # 标题
                info_dict['price'] = prices[index]  # 租金
                info_dict['type'] = p1_text[0]  # 户型
                info_dict['area'] = p1_text[1][:-2] + '平米'  # 面积
                info_dict['url'] = div.xpath('./b/a/@href')[0]  # 链接
                info_dict['model'] = p1_text[2]  # 出租方式
                info_dict['direction'] = p1_text[3]  # 朝向
                info_dict['district'] = p2_text[0]  # 区域

                all_info_list.append(info_dict)
            except:
                print('第{}条收藏房源信息不完整或已被删除'.format(count))

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
            models.append(info['model'])
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
            file_path = os.path.join(dir_path,'./ftx_fav.xlsx')
        else:
            file_path='./ftx_fav.xlsx'
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
        print('房天下收藏信息储存完毕')

if __name__ == '__main__':
    cookies = 'global_cookie=m7nhb176po4xvhhcwp9r58acw18kcda1wkn; __utmc=147393320; new_loginid=119142944; g_sourcepage=undefined; integratecover=1; newhouse_user_guid=D73B0206-9323-EAD4-F0EA-1563B0998BD4; newhouse_chat_guid=099F33D4-21FE-FD2F-BF13-898A72397CD9; keyWord_recenthousesh=%5b%7b%22name%22%3a%22%e9%97%b5%e8%a1%8c%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhezu-a018%2fc22000-d23000-p23-d53%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e5%98%89%e5%ae%9a%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhezu-a029%2fc22000-d23000-p23-d53%2f%22%2c%22sort%22%3a1%7d%5d; keyWord_recenthousezz=%5b%7b%22name%22%3a%22%e5%b7%a9%e4%b9%89%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a014824%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e9%87%91%e6%b0%b4%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a014861%2fp22%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e7%ae%a1%e5%9f%8e%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhezu-a014863%2f%22%2c%22sort%22%3a1%7d%5d; keyWord_recenthousegz=%5b%7b%22name%22%3a%22%e8%8a%b1%e9%83%bd%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a0639%2fn31%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e7%95%aa%e7%a6%ba%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhezu-a078%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e5%8d%97%e6%b2%99%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a084%2fg23-n31%2f%22%2c%22sort%22%3a1%7d%5d; __utmz=147393320.1594396796.10.9.utmcsr=search.fang.com|utmccn=(referral)|utmcmd=referral|utmcct=/captcha-24ca3bb2cf1ea3497f/redirect; keyWord_recenthousebj=%5b%7b%22name%22%3a%22%e6%9c%9d%e9%98%b3%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a01%2fn31%2f%22%2c%22sort%22%3a1%7d%5d; city=hz; keyWord_recenthousehz=%5b%7b%22name%22%3a%22%e6%8b%b1%e5%a2%85%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhezu-a0152%2fp22%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e6%b1%9f%e5%b9%b2%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhezu-a0153%2fc20-d2500-p22-n32-d54%2f%22%2c%22sort%22%3a1%7d%2c%7b%22name%22%3a%22%e6%bb%a8%e6%b1%9f%22%2c%22detailName%22%3a%22%22%2c%22url%22%3a%22%2fhouse-a0154%2fc21000-d22000-g21-p23-n31%2f%22%2c%22sort%22%3a1%7d%5d; Captcha=7850584468324952466645556255414F454D714A6B6B2F4E6230364A7431775661336D6E6B4A4C4A4F7A314F3747732B457876366E576A63594B2B46374458436C3545422F3341615063553D; __utma=147393320.2138602882.1594207633.1594477161.1594481927.14; g_sourcepage=txz_dl%5Egg_pc; token=27ed8977a78d4df4ace03c977b1c39c7; __utmt_t0=1; __utmt_t1=1; __utmb=147393320.10.10.1594481927; sfut=DB6F9D34CD1D18BAE3A10B280555FCE9ECC448C8C9011CE4BA4921DCD9023D25181987A4BD8C38EF842A43A99A3006DD2271D127E887BA4E3642FEFD89E62D86F5499A9920AE1BF8CB585F2B370376D3C8CD863478D86621731CD7B309BCA5E7; new_loginid=119142944; login_username=passport1364479620; unique_cookie=U_m7nhb176po4xvhhcwp9r58acw18kcda1wkn*493'
    a=Ftx_fav(cookies)
    b=a.get_fav_info()
    print(b)
    print(a.gen_most_dict(b))
    # a.save_fav_info(b,'D:/untitled1/爬虫/Find-house/data')