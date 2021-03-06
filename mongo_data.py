import settings
import pymongo

host = settings.MONGODB_HOST
port = settings.MONGODB_PORT
db_name = settings.MONGODB_DBNAME

# 创建MONGODB数据库链接
client = pymongo.MongoClient(host=host, port=port)
# 指定数据库
my_db = client[db_name]


# 存放数据的数据库表名


def update_data(sheet_name, items):
    post = my_db[sheet_name + '_base']
    for _ in items:
        result = post.update_one({'id': _['id']}, {"$set": _}, upsert=True)
        # print(result.raw_result)


def update_tuhao_data(sub_id, data):
    post = my_db['tuhao']
    result = post.update_one({'id': sub_id}, {"$set": data}, upsert=True)
    # print(result.raw_result)


def update_rank_data(sheet_name, item):
    post = my_db[sheet_name + '_rank']
    result = post.update_one({'rank': item['rank']}, {"$set": item}, upsert=True)
    # print(result.raw_result)


def find_offer_data(sheet_name, time):
    """获取只包含1个sub的match"""
    time = time * 1000
    post = my_db[sheet_name + '_base']
    result = post.aggregate([{'$unwind': '$sublist'},
                             {'$match': {'time': {'$gte': time}}},
                             {'$sort': {'time': 1}},
                             {'$limit': 1}])
    offer_data = list(result)
    # for _ in offer_data:
    #     print(_)
    print('获取最近比赛数据成功', offer_data)
    # todo:当天不再有比赛
    return offer_data[0]


def find_match_by_id(sheet_name, match_id):
    post = my_db[sheet_name + '_base']
    result = post.find_one({'id': match_id})
    # print(result)
    return result


def find_match_by_time(sheet_name, match_time):
    post = my_db[sheet_name + '_base']
    result = post.find_one({'time': match_time})
    # print(result)
    return result


def find_front_league(sheet_name, time, league_id, limit=10):
    time = time * 1000
    post = my_db[sheet_name + '_base']
    result = post.find({'$and': [{'league.id': league_id},
                                 {'time': {'$lte': time}}]}).sort('time', -1).limit(limit)  # 前10场
    return result


def get_tuhao(sub_id):
    post = my_db['tuhao']
    result = post.find_one({'id': sub_id})
    return result


def get_rank(name):
    post = my_db[name + '_rank']
    result = post.find()
    return result


if __name__ == '__main__':
    # get_rank('dota2')
    pass
