import json
import pymysql
import time
import xlrd
import sys
import datetime


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
            server = '47.99.99.45'
            user = 'root'
            password = 'Hp#x5zlEvOk!L8AepTFxp'

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

    def delete(self, table):
        now = int(time.time())
        sql = 'delete from {}'.format(table)
        self._reConn()
        # 查询操作
        row = self.cursor.execute(sql)
        self.conn.commit()
        return row


def run():
    db = DB.getInstance()

    db.delete('test_zuke_user')
    db.delete('test_zuke_event')
    # db.delete('test_landlord_user')
    # db.delete('test_landlord_event')

if __name__ == '__main__':
    run()
