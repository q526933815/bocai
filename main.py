import requests
import json
import mongo_data
from bs4 import BeautifulSoup
import datetime
import time


class UpdateData:
    """刷新数据"""

    def __init__(self, name):
        self.name = name

    base_data = ''

    sub_id_list = []

    def update_base_data(self):
        """获取当前网站上显示的所有比赛，更新基础数据库"""

        base_data_url = f'https://www.dota188.com/api/match/list.do?status=run&game={self.name}'
        req = requests.get(base_data_url)

        self.base_data = req.json()
        print('更新基础数据库')
        mongo_data.update_data(self.name, self.base_data['datas']['list'])

    def get_match_list(self):
        """解析当前网站上的比赛上所有的可下注场，获取id列表"""
        print('获取更新列表')
        for data in self.base_data['datas']['list']:
            for sub in data['sublist']:
                sub_id = sub['id']
                self.sub_id_list.append(sub_id)

    def update_tuhao_data(self):
        """使用解析到的id列表，更新土豪数据库"""
        print(f'更新土豪榜{len(self.sub_id_list)}条')
        for _id in self.sub_id_list:
            url = f'https://www.dota188.com/api/match/{_id}/tuhao.do'
            req = requests.get(url)
            json_data = json.loads(req.text)
            mongo_data.update_tuhao_data(_id, json_data)

    def get_rank(self):
        """获取队伍的rank排名"""
        if self.name == 'dota2':
            url = 'https://www.gosugamers.net/dota2/rankings/list'
        elif self.name == 'csgo':
            url = 'https://www.gosugamers.net/counterstrike/rankings/list'
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "lxml")
        rank_item = {}
        a_list = soup.find(class_='ranking-list').find_all('a')

        for a in a_list[:30]:
            # print(a['href'], a.get_text())
            rank_item['team_id'] = a['href'].split('/')[-1]
            rank_item['rank'] = a.get_text().split()[0]
            rank_item['team_name'] = ' '.join(a.get_text().split()[1:-1])
            rank_item['team_rank_value'] = a.get_text().split()[-1]
            mongo_data.update_rank_data(self.name, rank_item)


class Llf(UpdateData):
    """从数据库获取数据，判断数据"""
    odds = ''
    vs1_rank = ''
    vs2_rank = ''
    offer_data = ''

    def get_recent_event_time(self):
        """获取最近一场的时间"""

        now = datetime.datetime.now()
        return mongo_data.find_recent_time(self.name, now)

    def get_offer_data(self):
        offer_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        self.offer_data = mongo_data.find_offer_data(self.name, offer_time.timestamp())

    def get_offer_id(self):
        pass

    def get_odds(self):
        pass

    def get_vs_rank(self):
        pass

    def get_front_league_tuhao(self):
        pass


def llf(vs1_odds, vs1_rank, vs2_rank, ):
    pass
    # 判断赔率 < 1.1 or > 9
    # 判断两方队伍排名均 > 30
    # https://www.gosugamers.net/dota2/rankings 全名，简称，映射
    # 抓取同一天（抓时间）的同名联赛（抓比赛名）的下注金额的平均值（中位数），如果是饰品菠菜网站，下注最高的3人的下注额通常会显示算这三个人的就行，当场比赛的下注额为平均值N倍


def main():
    dota2 = UpdateData('dota2')
    # csgo = UpdateData('csgo')
    dota2.update_base_data()
    dota2.get_match_list()
    dota2.update_tuhao_data()
    dota2.get_rank()


if __name__ == '__main__':
    # main()
    dota2 = Llf('dota2')
    dota2.get_offer_data()
