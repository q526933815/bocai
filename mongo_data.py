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
        print(result.raw_result)


def update_tuhao_data(match_id, data):
    post = my_db['tuhao']
    result = post.update_one({'id': match_id}, {"$set": data}, upsert=True)
    print(result.raw_result)


def update_rank_data(sheet_name, item):
    post = my_db[sheet_name + '_rank']
    result = post.update_one({'rank': item['rank']}, {"$set": item}, upsert=True)
    print(result.raw_result)




if __name__ == '__main__':
    match_id = '565'
    # data = {'ihf': '125', 'a': '16'}
    # update_tuhao_data(match_id, data)
