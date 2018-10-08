import json
import pymysql
import time
import xlrd
import sys
import datetime
import hashlib
import random
import string


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

    def query(self, table):
        now = int(time.time())
        sql = 'select * from {}'.format(table)
        self._reConn()
        # 查询操作
        row = self.cursor.execute(sql)
        self.conn.commit()
        row = self.cursor.fetchall()
        return row

    def update(self, table,field,v,id):
        self._reConn()
        # 更新操作
        sql="UPDATE %s SET `%s`='%s' where id=%s" % (table, field, v, id)
        self.cursor.execute(sql)
        self.conn.commit()
        row = self.cursor.fetchone()
        return row
class ReadExcel(object):

    @staticmethod
    def getExcelAllData(excel_name, sheet_name):
        workbook = xlrd.open_workbook(r'%s/files/%s.xlsx' % (sys.path[0], excel_name))
        table = workbook.sheet_by_name(sheet_name)
        nrows = table.nrows
        return [table.row_values(i) for i in range(1, nrows)]


class AsssertResult:
    @staticmethod
    def assert_event(expected, actual, event_name_errors, event_property_errors, event_property_type_errors,
                     event_pro, ):
        for ex_event_1 in expected:
            is_actual_event_name = False
            ex_event_name_1 = ex_event_1.get('event_name', None)
            ex_event_show_name_1 = ex_event_1.get('event_show_name', None)
            for ac_event_1 in actual:
                try:
                    ac_event_1 = json.loads(ac_event_1[1])
                except Exception as e:
                    # print(e.__str__())
                    # print(ac_event_1)
                    continue
                ac_event_name_1 = ac_event_1.get('event')
                if ac_event_name_1 == ex_event_name_1:
                    is_actual_event_name = True
            if is_actual_event_name:
                print('神策返回的事件名{}和excel中的相同'.format(ac_event_name_1))
            else:
                if ex_event_name_1 != '':
                    print('神策返回的事件缺少{}'.format(ex_event_name_1))
                    event_name_errors.append(('缺少', ex_event_name_1, ex_event_show_name_1))

        for ac_event in actual:
            try:
                ac_event = json.loads(ac_event[1])
            except Exception as e:
                continue
            actual_event_name = ac_event.get('event', None)
            is_event_name = False
            for ex_event in expected:
                expected_event_name = ex_event.get('event_name', None)
                if actual_event_name == expected_event_name:
                    is_event_name = True
            if is_event_name:
                print('神策返回的数据有值')
            else:
                event_name_errors.append(('新增', actual_event_name, actual_event_name))

        for ac_event in actual:
            try:
                ac_event = json.loads(ac_event[1])
            except Exception as e:
                continue
            actual_event_name = ac_event.get('event', None)
            if actual_event_name == 'landapp_meterContractButtonClick':
                print(actual_event_name)
            if actual_event_name not in event_name_errors and actual_event_name not in event_name_errors:
                actual_event_property = ac_event.get('properties')
                for ex_event1 in expected:
                    event_name = ex_event1['event_name']
                    event_show_name = ex_event1['event_show_name']
                    if actual_event_name == ex_event1['event_name']:
                        for ex_key in ex_event1.keys():
                            if ex_key == '':
                                continue
                            if ex_key != 'event_name' and ex_key != 'event_show_name':
                                aep_type = actual_event_property.get(ex_key, None)
                                eep_property = ex_event1[ex_key]
                                eep_show_name = eep_property.get('property_show_name')
                                eep_type = eep_property.get('type', None)
                                if ex_key in actual_event_property.keys():
                                    pass
                                else:
                                    event_property_errors.append(('缺少', event_name, event_show_name, ex_key,
                                                                  eep_show_name, str(actual_event_property)))
                                if aep_type != None and aep_type != '':
                                    print('神策返回的数据中事件{}的属性{}存在'.format(actual_event_name, ex_key))
                                    ##神策返回的数据事件的属性如果在表中存在验证数据属性的类型
                                    if (isinstance(aep_type, int) or isinstance(aep_type, float)) and eep_type == '数值':
                                        print('神策返回的数据事件的属性类型相同都是数值型')
                                        continue
                                    if isinstance(aep_type, bool) and (eep_type == 'BOOL' or eep_type == 'BooL'):
                                        print('神策返回的数据事件的属性类型相同都是bool型')
                                        continue
                                    if isinstance(aep_type, str) and eep_type == '字符串':
                                        print('神策返回的数据事件的属性类型相同都是字符串型')
                                        continue
                                    if isinstance(aep_type, str) and eep_type == '字符串':
                                        print('神策返回的数据事件的属性类型相同都是字符串型')
                                        continue
                                    else:
                                        type = ''
                                        if isinstance(aep_type, datetime.datetime):
                                            type = '日期'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, ex_key, eep_show_name, eep_type, type))
                                            continue
                                        if isinstance(aep_type, bool) and (aep_type == True or aep_type == False):
                                            type = 'BOOL'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, ex_key, eep_show_name, eep_type, type))
                                            continue
                                        if isinstance(aep_type, str):
                                            type = '字符串'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, ex_key, eep_show_name, eep_type, type))
                                            continue
                                        if isinstance(aep_type, int) or isinstance(aep_type, float):
                                            type = '数值'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, ex_key, eep_show_name, eep_type, type))
                                        else:
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, ex_key, eep_show_name, eep_type, type))
                        for event_pro1 in event_pro:
                            event_pro_key = event_pro1[0]
                            event_pro_show_name = event_pro1[2]
                            event_pro_type = event_pro1[1]
                            if event_pro_key in actual_event_property.keys():
                                event_pro_ac_key = actual_event_property.get(event_pro_key, None)
                                if event_pro_ac_key == '未知':
                                    event_property_errors.append(('未知', event_name, event_show_name, event_pro_key,
                                                                  event_pro_show_name, str(actual_event_property)))
                                if event_pro_ac_key != None and event_pro_ac_key != '':

                                    if (isinstance(event_pro_ac_key, int) or isinstance(event_pro_ac_key,
                                                                                        float)) and event_pro_type == '数值':
                                        print('神策返回的数据事件的属性类型相同都是数值型')
                                        continue
                                    if isinstance(event_pro_ac_key, bool) and (
                                            event_pro_type == 'BOOL' or event_pro_type == 'BooL'):
                                        print('神策返回的数据事件的属性类型相同都是bool型')
                                        continue
                                    if isinstance(event_pro_ac_key, str) and event_pro_type == '字符串':
                                        print('神策返回的数据事件的属性类型相同都是字符串型')
                                        continue
                                    if isinstance(event_pro_ac_key, str) and event_pro_type == '字符串':
                                        print('神策返回的数据事件的属性类型相同都是字符串型')
                                        continue
                                    else:
                                        type = ''
                                        if isinstance(event_pro_ac_key, datetime.datetime):
                                            type = '日期'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, event_pro_key, event_pro_show_name,
                                                 event_pro_type, type))
                                            continue
                                        if isinstance(event_pro_ac_key, bool) and (
                                                event_pro_ac_key == True or event_pro_ac_key == False):
                                            type = 'BOOL'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, event_pro_key, event_pro_show_name,
                                                 event_pro_type, type))
                                            continue
                                        if isinstance(event_pro_ac_key, str):
                                            type = '字符串'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, event_pro_key, event_pro_show_name,
                                                 event_pro_type, type))
                                            continue
                                        if isinstance(event_pro_ac_key, int) or isinstance(event_pro_ac_key, float):
                                            type = '数值'
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, event_pro_key, event_pro_show_name,
                                                 event_pro_type, type))
                                        else:
                                            event_property_type_errors.append(
                                                (event_name, event_show_name, event_pro_key, event_pro_show_name,
                                                 event_pro_type, type))

                            else:
                                event_property_errors.append(('缺少', event_name, event_show_name, event_pro_key,
                                                              event_pro_show_name, str(actual_event_property)))
                            # if aep_type=='':
                            #     pass
                            # event_property_type_errors.append(
                            #     ( event_name, event_show_name, ex_key, eep_show_name,eep_type,'空字符串'))
                            # else:
                            # try:
                            #     zz_num = len(actual_event_property)
                            #     tt_num = 0
                            #     for zz in actual_event_property.keys():
                            #         if not event_property_errors:
                            #             break
                            #         for xx in event_property_errors:
                            #             tt_num=0
                            #             xx1 = json.loads(xx[5])
                            #             for xx2 in xx1.keys():
                            #                 if xx1[xx2] == actual_event_property[zz]:
                            #                     tt_num = tt_num + 1
                            #     if tt_num == zz_num:
                            #         pass
                            #     else:
                            # if actual_event_property['$element_type'] not in ''.join([dd[5] for dd in event_property_errors]):
                            # event_property_errors.append(('缺少', event_name,event_show_name, ex_key,eep_show_name,str(actual_event_property)))
                            # except:
                            #     event_property_errors.append(('缺少', event_name, event_show_name, ex_key,  eep_show_name, str(actual_event_property)))
                is_add_event_property = False
                index1 = 0
                for index, ex_event2 in enumerate(expected):
                    if ex_event2['event_name'] == actual_event_name:
                        index1 = index

                for ac_key in actual_event_property.keys():
                    if index1 != 0:
                        if ac_key in expected[index1].keys():
                            is_add_event_property = True
                        else:
                            if event_name == 'lanapp_abnormalInformationCollect':
                                pass
                            else:
                                event_property_errors.append(
                                    ('新增', event_name, event_show_name, ac_key, ac_key,
                                     ''))  # str(actual_event_property)
                    if ac_key not in [ee[0] for ee in event_pro]:
                        event_property_errors.append(
                            ('新增', event_name, event_show_name, ac_key, ac_key,
                             ''))  # str(actual_event_property)

                # if is_add_event_property:
                #     print('神策返回的数据中事件{}的属性{}存在'.format(actual_event_name, ac_key))
                # else:
                #     # try:
                #     #     zz_num=len(actual_event_property)
                #     #     tt_num=0
                #     #     for zz in actual_event_property.keys():
                #     #         for xx in event_property_errors:
                #     #             xx1 = json.loads(xx[5])
                #     #             for xx2 in xx1.keys():
                #     #                 if xx1[xx2]==actual_event_property[zz]:
                #     #                     tt_num=tt_num+1
                #     #     if tt_num==zz_num:
                #     #         pass
                #     #     else:
                #     #     if actual_event_property['$element_type'] not in ''.join([dd[5] for dd in event_property_errors]):
                #             # event_property_errors.append(('新增', event_name,event_show_name, ac_key,ac_key,str(actual_event_property)))
                #     # except:
                #         event_property_errors.append( ('新增', event_name, event_show_name, ac_key, ac_key, str(actual_event_property)))

    @staticmethod
    def assert_user(expected, actual, user_property_errors, user_property_type_errors, user_pro):
        for ex_user in expected:
            user_property_type = ex_user.get('user_property_type')
            user_property_name = ex_user.get('user_property_name')
            user_property_show_name = ex_user.get('user_property_show_name')
            if not user_property_show_name:
                user_property_errors.append(('excel表中属性显示名为空', user_property_name, user_property_show_name, ''))
            if not user_property_name:
                user_property_errors.append(('excel表中属性名称为空', user_property_name, user_property_show_name, ''))
            if not user_property_type:
                user_property_type_errors.append(
                    ('excel表中属性类型为空', user_property_name, user_property_show_name, user_property_type))
            for ac_user in actual:
                try:
                    ac_user = json.loads(ac_user[1])
                except:
                    continue
                ac_user_property = ac_user.get('properties')
                ac_user_property_type = ac_user_property.get(user_property_name, None)
                if ac_user_property_type or ac_user_property_type == '':
                    print('神策返回的消息有数据{}'.format(ac_user_property_type))
                else:
                    if user_property_name not in ['is_staff', 'is_operator', 'is_renter', 'is_intermediary']:
                        if ac_user_property['user_mobile'] not in ''.join([dd[3] for dd in user_property_errors]):
                            user_property_errors.append(('缺少', user_property_name, user_property_show_name,
                                                         str(ac_user_property)))  # ,str(ac_user)

        for ac_user in actual:
            try:
                ac_user = json.loads(ac_user[1])
            except:
                continue
            user_properties = ac_user.get('properties')
            for key in user_properties.keys():
                if key in [i.get('user_property_name') for i in expected]:
                    print('神策订阅的用户profile在excel中存在')
                    ac_user_property_type = user_properties.get(key, None)
                    for ex_user in expected:
                        ex_user_property_type = ex_user.get('user_property_type')
                        ex_user_property_name = ex_user.get('user_property_name')
                        ex_user_property_show_name = ex_user.get('user_property_show_name')
                        if key == ex_user_property_name:
                            if ac_user_property_type:
                                if (isinstance(ac_user_property_type, int) or isinstance(ac_user_property_type,
                                                                                         float)) and ex_user_property_type == '数值':
                                    print('神策返回的数据事件的属性类型相同都是数值型')
                                    break
                                if isinstance(ac_user_property_type, bool) and ex_user_property_type == 'BOOL值':
                                    print('神策返回的数据事件的属性类型相同都是bool型')
                                    break
                                if isinstance(ac_user_property_type, str) and ex_user_property_type == '字符串':
                                    print('神策返回的数据事件的属性类型相同都是字符串型')
                                    break
                                if isinstance(ac_user_property_type,
                                              datetime.datetime) and ex_user_property_type == '日期':
                                    print('神策返回的数据事件的属性类型相同都是日期型')
                                    break
                                else:
                                    type = ''
                                    if isinstance(ac_user_property_type, datetime.datetime):
                                        type = '日期'
                                        user_property_type_errors.append(
                                            (ex_user_property_name, ex_user_property_show_name,
                                             ex_user_property_type, type))
                                        continue
                                    if isinstance(ac_user_property_type, bool):
                                        type = 'BOOL'
                                        user_property_type_errors.append(
                                            (ex_user_property_name, ex_user_property_show_name,
                                             ex_user_property_type, type))
                                        continue
                                    if isinstance(ac_user_property_type, str):
                                        type = '字符串'
                                        user_property_type_errors.append(
                                            (ex_user_property_name, ex_user_property_show_name,
                                             ex_user_property_type, type))
                                        continue
                                    if isinstance(ac_user_property_type, int) or isinstance(ac_user_property_type,
                                                                                            float):
                                        type = '数值'
                                        user_property_type_errors.append(
                                            (ex_user_property_name, ex_user_property_show_name,
                                             ex_user_property_type, type))
                                        continue
                        if ac_user_property_type == '' and key not in user_property_errors:
                            pass
                            # user_property_type_errors.append((ex_user_property_name, ex_user_property_show_name,
                            #                                  ex_user_property_type, '空字符串'))
                        if ac_user_property_type == None:
                            if key not in ['is_staff', 'is_operator', 'is_landlord', 'is_intermediary']:
                                if ac_user_property['user_mobile'] not in ''.join(
                                        [dd[3] for dd in user_property_errors]):
                                    user_property_errors.append(
                                        ('缺少', key, ex_user_property_show_name, str(ac_user_property)))  # ,str(ac_user)
                else:
                    user_property_errors.append(('新增', key, key, str(ac_user_property)))  # ,str(ac_user)


class Util:

    @staticmethod
    def generateShield(arg):
        hl = hashlib.md5()
        hl.update(arg.encode(encoding='utf-8'))
        sig = hl.hexdigest()
        return sig

    @staticmethod
    def getEvent(arg):
        event_name = []
        for a in arg:
            if a.get('event', None):
                event_name.append(a.get('event'))

    @staticmethod
    def getCommonProperty(arg):
        m = 0
        for index, data in enumerate(arg):
            n = [i for i in data if i != '']
            if len(n) == 0:
                continue
            if data[0] == '' and data[1] == '' and data[2] == '':
                m = m + 1
                continue
            if data[0] == '事件编号':
                return arg[index - m:index], index

    @staticmethod
    def getEventAndProperty(arg, errors):
        event_name = ''
        event_show_name = ''
        event_property_table = []
        common_property, index1 = Util.getCommonProperty(arg)
        for index, data in enumerate(arg):
            if index >= index1 + 1:
                n = [i for i in data if i != '']
                if len(n) == 0:
                    continue
                if data[1] != '' and data[2] != '':
                    event_name = data[1]
                    event_show_name = data[2]
                if data[1] == '' and data[2] == '':
                    data[1] = event_name
                    data[2] = event_show_name
                    event_property_table.append(
                        {'event_name': event_name, 'event_show_name': event_show_name,
                         str(data[3]): {'property_show_name': str(data[4]), 'type': data[5]}}, )
                if data[1] == '' and data[2] != '':
                    errors.append(('excel事件表中事件名为空', data[1], data[2]))
                    event_name = ''
                    event_show_name = ''
        for event_property in event_property_table:
            for j in common_property:
                event_property[str(j[3])] = {'property_show_name': str(j[4]), 'type': j[5]}
        for index, data in enumerate(arg):
            if index >= index1 + 1:
                event_name = data[1]
                event_len = [i[1] for i in arg if i[1] == event_name]
                if len(event_len) == 1:
                    errors.append(('excel事件表中的属性没有配置', event_name, event_show_name))
        return event_property_table

    @staticmethod
    def getUserIndex(arg):
        for index, data in enumerate(arg):
            if data[0] == '$预置属性':
                return index

    @staticmethod
    def getUserAndProperty(arg, errors):
        index1 = Util.getUserIndex(arg)
        user_property_table = []
        for index, data in enumerate(arg):
            if index > index1:
                n = [i for i in data if i != '']
                if len(n) == 0:
                    continue
                if data[1] != '' and data[2] != '' and data[0] != 0:
                    user_property_table.append({'user_property_show_name': data[0], 'user_property_name': data[1],
                                                'user_property_type': data[2]})
        return user_property_table

    @staticmethod
    def genExcel(event_name_errors='', event_property_errors='', event_property_type_errors='', user_property_errors='',
                 user_property_type_errors=''):

        from xlwt import Workbook
        book = Workbook(encoding='utf-8')

        sheet1 = book.add_sheet('事件校验', cell_overwrite_ok=True)
        sheet1.write(0, 0, "差异类型")
        sheet1.write(0, 1, "事件名称")
        sheet1.write(0, 2, "事件显示名")
        if event_name_errors:
            for index, value in enumerate(event_name_errors):
                sheet1.write(index + 1, 0, value[0])
                sheet1.write(index + 1, 1, value[1])
                sheet1.write(index + 1, 2, value[2])
        sheet2 = book.add_sheet('事件表-属性校验', cell_overwrite_ok=True)
        sheet2.write(0, 0, "差异类型")
        sheet2.write(0, 1, "事件名称")
        sheet2.write(0, 2, "事件显示名")
        sheet2.write(0, 3, "属性名称")
        sheet2.write(0, 4, "属性显示名")
        sheet2.write(0, 5, "属性实际数据")
        if event_property_errors:
            for index, value in enumerate(event_property_errors):
                sheet2.write(index + 1, 0, value[0])
                sheet2.write(index + 1, 1, value[1])
                sheet2.write(index + 1, 2, value[2])
                sheet2.write(index + 1, 3, value[3])
                sheet2.write(index + 1, 4, value[4])
                sheet2.write(index + 1, 5, value[5])
        sheet3 = book.add_sheet('事件表-属性类型校验', cell_overwrite_ok=True)
        sheet3.write(0, 0, "事件名称")
        sheet3.write(0, 1, "事件显示名")
        sheet3.write(0, 2, "属性名称")
        sheet3.write(0, 3, "属性显示名")
        sheet3.write(0, 4, "属性类型")
        sheet3.write(0, 5, "属性实际类型")
        if event_property_type_errors:
            for index, value in enumerate(event_property_type_errors):
                sheet3.write(index + 1, 0, value[0])
                sheet3.write(index + 1, 1, value[1])
                sheet3.write(index + 1, 2, value[2])
                sheet3.write(index + 1, 3, value[3])
                sheet3.write(index + 1, 4, value[4])
                sheet3.write(index + 1, 5, value[5])
        sheet4 = book.add_sheet('用户表-属性校验', cell_overwrite_ok=True)
        sheet4.write(0, 0, "差异类型")
        sheet4.write(0, 1, "属性名称")
        sheet4.write(0, 2, "属性显示名")
        sheet4.write(0, 3, "属性实际数据")
        if user_property_errors:
            for index, value in enumerate(user_property_errors):
                sheet4.write(index + 1, 0, value[0])
                sheet4.write(index + 1, 1, value[1])
                sheet4.write(index + 1, 2, value[2])
                sheet4.write(index + 1, 3, value[3])
        sheet5 = book.add_sheet('用户表-属性类型校验', cell_overwrite_ok=True)
        sheet5.write(0, 0, "属性名称")
        sheet5.write(0, 1, "属性显示名")
        sheet5.write(0, 2, "属性值类型")
        sheet5.write(0, 3, "属性值实际类型")
        if user_property_type_errors:
            for index, value in enumerate(user_property_type_errors):
                sheet5.write(index + 1, 0, value[0])
                sheet5.write(index + 1, 1, value[1])
                sheet5.write(index + 1, 2, value[2])
                sheet5.write(index + 1, 3, value[3])

        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        path = sys.path[0] + '/landlord_report/test_report_{}.xls'.format(now)
        book.save(path)

    @staticmethod
    def getEventPro(property_table):
        event_pro = []
        user_pro = []
        num = 0
        for index, data in property_table:
            if data[0] == '用户表':
                num = index
        for index in range(num, len(property_table)):
            if data[index][0] != '' and data[index][0] != '字段名称' and '√' not in data[index][0]:
                user_pro.append(data)
        for index in range(1, len(property_table)):
            if data[index][0] != '' and data[index][0] != '字段名称':
                event_pro.append(data)
        return event_pro, user_pro


def run():
    event_name_errors = []
    event_property_errors = []
    event_property_type_errors = []
    re = ReadExcel.getExcelAllData('landlord', '事件表')
    event_table = Util.getEventAndProperty(re, event_name_errors)
    event_rt_db = DB.getInstance().query('test_landlord_event')

    property_table = ReadExcel.getExcelAllData('landlord', '预置属性')
    event_pro, user_pro = Util.getEventPro(property_table)
    AsssertResult.assert_event(event_table, event_rt_db, event_name_errors, event_property_errors,
                               event_property_type_errors, event_pro)
    # 获取数据库所有的数据
    # 解析数据库数据

    # 查看用户表
    user_property_errors = []
    user_property_type_errors = []
    user_rt_db = DB.getInstance().query('test_landlord_user')
    re = ReadExcel.getExcelAllData('landlord', '用户表')
    user_table = Util.getUserAndProperty(re, event_name_errors)

    AsssertResult.assert_user(user_table, user_rt_db, user_property_errors, user_property_type_errors, user_pro)

    # 写入报告
    event_name_errors = list(set(event_name_errors))
    # event_property_errors = list(set(event_property_errors))
    event_property_type_errors = list(set(event_property_type_errors))
    user_property_errors = list(set(user_property_errors))
    user_property_type_errors = list(set(user_property_type_errors))
    if event_property_type_errors or event_name_errors:
        Util.genExcel(event_name_errors=event_name_errors, event_property_errors=event_property_errors,
                      event_property_type_errors=event_property_type_errors,
                      user_property_errors=user_property_errors, user_property_type_errors=user_property_type_errors)


if __name__ == '__main__':
    # run()
    q_data=DB.getInstance().query('test_landlord_event')
    for d in q_data:
        tt = Util.generateShield(d[1])
        DB.getInstance().update('test_landlord_event','sig',tt,d[0])
        print('插入成功')

