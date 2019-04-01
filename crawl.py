import requests
import json

url = 'https://www.dota188.com/api/match/list.do?status=run&game=all'
req = requests.get(url)
# print(req.text)
data = json.loads(req.text)
print(data)
print(data['datas']['list'][0])


def llf(vs1_odds,):
    # 判断赔率 < 1.1 or > 9
    # 判断两方队伍排名均 > 30
    # https://www.gosugamers.net/dota2/rankings 全名，简称，映射
    # 抓取同一天（抓时间）的同名联赛（抓比赛名）的下注金额的平均值（中位数），如果是饰品菠菜网站，下注最高的3人的下注额通常会显示算这三个人的就行，当场比赛的下注额为平均值N倍


