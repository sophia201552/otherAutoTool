from kafka import KafkaConsumer
import pymysql
import time
import json
import  hashlib

class DB:
    __instance = None

    def __init__(self):
        self._conn()

    @classmethod
    def getInstance(cls):
        if (cls.__instance == None):
            cls.__instance = DB()
        return cls.__instance

    def _conn(self):
        try:
            server = '****'
            user = '***
            password = '******'

            database = 'message'
            self.conn = pymysql.connect(server, user, password, database)
            self.cursor = self.conn.cursor()
            return True
        except:
            return False

    def _reConn(self, num=28800, stime=3):  # 重试连接总次数为1天
        _number = 0
        _status = True
        while _status and _number <= num:
            try:
                self.conn.ping()  # cping 校验连接是否异常
                _status = False
            except:
                if self._conn() == True:  # 重新连接,成功退出
                    _status = False
                    break
                _number += 1
                time.sleep(stime)  # 连接不成

    def insert(self, table, message_content, create_time,rec_time,sig):
        sql = "insert into  %s(message_content,create_time,rec_time,sig) value ('%s',%s,%s,'%s')" % (table, message_content, create_time,rec_time,sig)
        self._reConn()
        # 查询操作
        row = self.cursor.execute(sql)
        self.conn.commit()
        if not row:
            print('插入失败{}'.format(sql))
        else:
            print('插入成功')
        return row


class Message:
    @staticmethod
    def generateShield(arg):
        hl = hashlib.md5()
        hl.update(arg.encode(encoding='utf-8'))
        sig = hl.hexdigest()
        return sig
    def getMessage(self):
        bootstrap_servers = ['data01:9092', 'data02:9092', 'data03:9092']
        consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)
        consumer.subscribe(topics=('event_topic'))
        db = DB.getInstance()
        for message in consumer:
            value = str(message.value, encoding="utf-8")
            rec_time=''
            try:
                rec_time=json.loads(value).get('time','')
            except:
                pass
            if isinstance(rec_time, int):
                rec_time = int(rec_time / 1000)
            if 'landapp' in value and 'event' in value:
                # db.insert('production_landlord_event', value, int(time.time()), Message.generateShield(value))#rec_time
                pass
            if 'landapptest' in value and 'event' in value:
                db.insert('test_landlord_event', value, int(time.time()),rec_time,Message.generateShield(value))
                pass
            if 'profile_set' in value and 'landapp' in value and 'profile_set_once' not in value:
                # db.insert('production_landlord_user', value, int(time.time()),rec_time,Message.generateShield(value))
                pass
            if 'profile_set' in value and 'landapptest' in value and 'profile_set_once' not in value:
                db.insert('test_landlord_user', value, int(time.time()),rec_time,Message.generateShield(value))
                pass


if __name__ == '__main__':
    m = Message()
    m.getMessage()

