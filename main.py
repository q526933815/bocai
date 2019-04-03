import requests
import json
import mongo_data


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
    myUpdateData = UpdateData('dota2')
    myUpdateData.update_base_data()
    myUpdateData.get_match_list()
    myUpdateData.update_tuhao_data()
