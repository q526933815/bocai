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

    def get_sub_list(self):
        """解析当前网站上的比赛上所有的可下注场，获取id列表"""
        print('获取更新列表')
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

        for a in a_list[:30]:
            # print(a['href'], a.get_text())
            rank_item['team_id'] = a['href'].split('/')[-1]
            rank_item['rank'] = a.get_text().split()[0]
            rank_item['team_name'] = ' '.join(a.get_text().split()[1:-1])
            rank_item['team_rank_value'] = a.get_text().split()[-1]
            mongo_data.update_rank_data(self.name, rank_item)


class Llf:
    """从数据库获取数据，判断数据"""

    def __init__(self, name):
        self.name = name

    offer_data = ''
    sub_list = []
    recent_time = ''

    def get_sub_data(self):  # 如果有两个match时间相同就GG了，先不管
        """获取最近一场sub的数据"""

        offer_time = datetime.datetime.now()
        self.offer_data = mongo_data.find_offer_data(self.name, offer_time.timestamp())
        self.recent_time = self.offer_data['sublist']['time']
        match_time = self.offer_data['time']
        match_id = self.offer_data['id']
        if self.recent_time == match_time:  # 这里判断是不是前三盘
            match_data = mongo_data.find_match_by_id(self.name, match_id)
            self.sub_list = match_data['sublist'][:3]
        else:
            self.sub_list = [self.offer_data['sublist']]

    def get_front_league(self):
        league_id = self.offer_data['league']['id']
        mongo_data.find_front_league(self.name, self.recent_time, league_id)

    # def get_next_time(self):
    #     """获取下一场sub的数据"""
    #
    #     offer_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
    #     offer_data = mongo_data.find_offer_data(self.name, offer_time.timestamp())
    #     self.next_time = offer_data['sublist']['time']

    def send_message(self):
        for sub in self.sub_list:
            sub = Sub(sub)
            _ = [sub.llf_rank(), sub.llf_odds(), sub.llf_match(), sub.llf_league()]
            print(_)
            if all(_):
                """触发推送"""
                print("推送消息", sub['id'])


class Sub:
    def __init__(self, sub):
        self.sub = sub
        self.vs1_name = sub['vs1']['name']
        self.vs2_name = sub['vs2']['name']

    @staticmethod
    def get_vs_rank(vs_name):
        """模糊匹配名"""
        # todo 模糊匹配配算法
        # https://www.gosugamers.net/dota2/rankings 全名，简称，映射
        rank = 0
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
        odds = self.sub['vs1']['odds']
        if odds <= 1.1 or odds >= 9:
            # 判断赔率 < 1.1 or > 9
            return True
        else:
            return False

    def llf_match(self):

        # 抓取同一天（抓时间）的同名联赛（抓比赛名）的下注金额的平均值（中位数），如果是饰品菠菜网站，下注最高的3人的下注额通常会显示算这三个人的就行，当场比赛的下注额为平均值N倍
        return True

    def llf_league(self):
        return True


def update_data(name='dota2'):
    """刷新数据"""
    my_update = UpdateData(name)
    my_update.update_base_data()
    my_update.update_tuhao_data()
    my_update.get_rank()


def main():
    """主程序逻辑是这样，但是还不能用"""

    update_data(name='dota2')
    dota2 = Llf('dota2')
    dota2.get_sub_data()
    while dota2.recent_time - datetime.datetime.now() == 5:
        update_data(name='dota2')

        dota2.get_sub_data()
        if dota2.recent_time - datetime.datetime.now() < 5:
            dota2.send_msessage()
        else:
            print('不推送')


if __name__ == '__main__':
    dota2 = Llf('dota2')
    dota2.get_sub_data()
    print(dota2.recent_time)
