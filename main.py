import requests
import json
import mongo_data


class Dota2:
    base_data = ''
    base_data_url = 'https://www.dota188.com/api/match/list.do?status=run&game=dota2'
    sub_id_list = []

    def update_base_data(self):
        req = requests.get(self.base_data_url)
        print(req.json())
        self.base_data = req.json()
        mongo_data.update_data(self.base_data['datas']['list'])

    def get_match_list(self):
        for data in self.base_data['datas']['list']:
            for sub in data['sublist']:
                sub_id = sub['id']
                self.sub_id_list.append(sub_id)

    def update_tuhao_data(self):
        for match_id in self.sub_id_list:
            url = f'https://www.dota188.com/api/match/{match_id}/tuhao.do'
            req = requests.get(url)
            data = json.loads(req.text)
            mongo_data.update_tuhao_data(match_id, data)

    def get_rank(team_name):
        pass

    def llf(vs1_odds, vs1_rank, vs2_rank, ):
        pass
        # 判断赔率 < 1.1 or > 9
        # 判断两方队伍排名均 > 30
        # https://www.gosugamers.net/dota2/rankings 全名，简称，映射
        # 抓取同一天（抓时间）的同名联赛（抓比赛名）的下注金额的平均值（中位数），如果是饰品菠菜网站，下注最高的3人的下注额通常会显示算这三个人的就行，当场比赛的下注额为平均值N倍


if __name__ == '__main__':
    dota = Dota2()
    dota.update_base_data()
    dota.get_match_list()
    dota.update_tuhao_data()
