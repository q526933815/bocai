import settings
import pymongo

host = settings.MONGODB_HOST
port = settings.MONGODB_PORT
dbname = settings.MONGODB_DBNAME
sheetname = settings.MONGODB_SHEETNAME
# 创建MONGODB数据库链接
client = pymongo.MongoClient(host=host, port=port)
# 指定数据库
mydb = client[dbname]
# 存放数据的数据库表名
post = mydb[sheetname]


def update_data(items):
    for _ in items:
        result = post.update_one({'id': _['id']}, {"$set": _}, upsert=True)
        print(result.raw_result)


def update_tuhao_data(match_id, data):
    post = mydb['tuhao']
    result = post.update_one({'id': match_id}, {"$set": data}, upsert=True)
    print(result.raw_result)


if __name__ == '__main__':
    match_id = '565'
    data = {'ihf': '125', 'a': '16'}
    update_tuhao_data(match_id, data)
