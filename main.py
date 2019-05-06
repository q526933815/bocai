import requests
import json
import mongo_data
from bs4 import BeautifulSoup
import datetime
import numpy as np
import time


class UpdateData:
    """刷新数据"""

    def __init__(self, name):
        self.name = name
        self.sub_id_list = []

    base_data = ''

    def update_base_data(self):
        """获取当前网站上显示的所有比赛，更新基础数据库"""

        base_data_url = f'https://www.dota188.com/api/match/list.do?status=run&game={self.name}'
        req = requests.get(base_data_url)

        self.base_data = req.json()
        print('更新基础数据库', req.status_code, req.url)
        mongo_data.update_data(self.name, self.base_data['datas']['list'])

    def get_sub_list(self):
        """解析当前网站上的比赛上所有的可下注场，获取id列表"""
        print('获取更新列表')
        self.sub_id_list = []
        for data in self.base_data['datas']['list']:
            for sub in data['sublist']:
                sub_id = sub['id']
                self.sub_id_list.append(sub_id)

    def update_tuhao_data(self):
        """使用最新获取解析到的id列表，更新土豪数据库"""

        self.get_sub_list()
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
        # todo 获取最后页数
        for a in a_list:
            # print(a['href'], a.get_text())
            rank_item['team_id'] = a['href'].split('/')[-1]
            rank_item['rank'] = a.get_text().split()[0]
            rank_item['team_name'] = ' '.join(a.get_text().split()[1:-1])
            rank_item['team_rank_value'] = a.get_text().split()[-1]
            rank_item['team_short_name'] = self.get_short_name(rank_item)
            mongo_data.update_rank_data(self.name, rank_item)

    def get_short_name(self, rank_item):
        import re
        if self.name == 'dota2':
            url = 'https://www.gosugamers.net/dota2/teams/{}'
        elif self.name == 'csgo':
            url = 'https://www.gosugamers.net/counterstrike/teams/{}'
        para_name = f"{rank_item['team_id']}-{re.sub('|'.join([' ', '.']), '-', rank_item['team_name'].lower())}"
        req_url = url.format(para_name)
        req = requests.get(req_url)
        print(req.text)
        soup = BeautifulSoup(req.text, "lxml")
        short_name = soup.find('h3', class_='name').get_text()
        print(short_name)
        return short_name


class Llf:
    """从数据库获取数据，判断数据"""

    def __init__(self, name):
        self.name = name

    offer_data = ''
    sub_list = []
    recent_time = ''

    def get_sub_data(self):
        """获取最近sub的list数据"""

        time_now = datetime.datetime.now()
        self.offer_data = mongo_data.find_offer_data(self.name, time_now.timestamp())
        self.recent_time = self.offer_data['sublist']['time']
        match_time = self.offer_data['time']
        if self.recent_time == match_time:  # 这里判断是不是前三盘
            match_result = mongo_data.find_match_by_time(self.name, match_time)
            self.sub_list = match_result['sublist'][:3]  # 获取所有match的前三个sub
        else:
            self.sub_list = [self.offer_data['sublist']]

    @staticmethod
    def get_longgo(sub_id):
        """计算龙钩个数"""
        longgo_cot = 0
        tuhao_row = mongo_data.get_tuhao(sub_id)

        for tuhao in tuhao_row['datas']['list']:
            for obj in tuhao['items']:
                if obj['name'] == '龙爪弯钩':
                    longgo_cot += 1
        return longgo_cot

    def get_front_league(self):
        """获取相同league之前sub的龙钩量"""

        tuhao_data = {}
        league_id = self.offer_data['league']['id']
        match_data = mongo_data.find_front_league(self.name, self.recent_time, league_id)
        for match in match_data:
            for sub in match['sublist']:
                longgo_cot = self.get_longgo(sub['id'])
                tuhao_data[sub['id']] = longgo_cot
        return tuhao_data

    def send_message(self):
        """是否推送"""

        for sub in self.sub_list:
            tuhao_data = self.get_front_league()
            sub = Sub(sub, tuhao_data)
            _ = [sub.llf_rank(), sub.llf_odds(), sub.llf_match()]
            print(sub.id, _)
            if all(_):
                """触发推送"""
                print("推送消息:关注这场比赛", sub.id, sub.vs1_name, sub.vs2_name)


class Sub:
    """计算每一个sub"""

    def __init__(self, sub, tuhao_data, rank_data):
        self.sub = sub
        self.tuhao_data = tuhao_data
        self.rank_data = rank_data
        self.vs1_name = sub['vs1']['name']
        self.vs2_name = sub['vs2']['name']
        self.id = sub['id']

    @staticmethod
    def get_vs_rank(vs_name):
        import difflib
        """模糊匹配名"""
        rank_data = mongo_data.get_rank('dota2')
        ll2 = []
        for i in rank_data:
            team_name = i['team_name']
            rank = i['rank']
            ll2.append([difflib.SequenceMatcher(None, team_name, vs_name).ratio(), team_name, rank])

        rank = sorted(ll2, reverse=True)[0][2]

        # https://www.gosugamers.net/dota2/rankings 全名，简称，映射

        return rank

    def llf_rank(self):
        """判断两方队伍排名均 > 30"""
        vs1_rank = self.get_vs_rank(self.vs1_name)
        vs2_rank = self.get_vs_rank(self.vs2_name)
        if vs1_rank >= 30 and vs2_rank >= 30:

            return True
        else:
            return False

    def llf_odds(self):
        """判断赔率"""
        odds = self.sub['vs1']['odds']
        if odds <= 0.1 or odds >= 9:
            # 判断赔率 < 1.1 or > 9
            return True
        else:
            return False

    def llf_match(self, n=3):
        """判断中位数"""
        if self.tuhao_data[self.id] > np.median(list(self.tuhao_data.values())) * n:
            # 抓取同一天（抓时间）的同名联赛（抓比赛名）的下注金额的平均值（中位数），如果是饰品菠菜网站，下注最高的3人的下注额通常会显示算这三个人的就行，当场比赛的下注额为平均值N倍
            return True
        else:
            return False


def update_data(name='dota2'):
    """刷新数据"""
    my_update = UpdateData(name)
    my_update.update_base_data()
    my_update.update_tuhao_data()
    my_update.get_rank()


def main():
    """主程序逻辑"""

    update_data(name='dota2')
    dota2 = Llf('dota2')
    dota2.get_sub_data()
    recent_time = datetime.datetime.utcfromtimestamp(dota2.recent_time / 1000)  # 时间戳转时间

    time_difference = datetime.timedelta(seconds=300)
    while True:
        if recent_time - datetime.datetime.now() <= time_difference:
            update_data(name='dota2')
            dota2.get_sub_data()
            recent_time = datetime.datetime.utcfromtimestamp(dota2.recent_time / 1000)  # 时间戳转时间

            dota2.send_message()

        time.sleep(10)


if __name__ == '__main__':
    main()
    # Sub.get_vs_rank('VP')
    # dota2 = Llf('dota2')
    # dota2.get_sub_data()
    # print(dota2.recent_time)
