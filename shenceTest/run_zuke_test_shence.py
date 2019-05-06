import json
import pymysql
import time
import xlrd
import sys
import datetime
import hashlib

yuzhi_event = ['distinct_id', 'time', '$app_version', '$ip', '$country', '$city', '$province',
               '$model', '$os', '$os_version', '$screen_height', '$screen_width', '$wifi',
               '$network_type', '$is_first_day', '$device_id', '$manufacturer']
yuzhi_event_all = ['distinct_id', 'time', '$app_version', '$ip', '$country', '$city', '$province',
                   '$model', '$os', '$os_version', '$screen_height', '$screen_width', '$wifi',
                   '$network_type', '$is_first_day', '$device_id', '$manufacturer', '$lib', '$lib_version', '$browser',
                   '$browser_version', '$carrier', '$network_type', '$utm_matching_type', '$latest_referrer',
                   '$latest_referrer_host', '$latest_utm_source', '$latest_utm_medium', '$latest_utm_term',
                   '$latest_utm_content', '$latest_utm_campaign', '$latest_search_keyword','$latest_traffic_source_type']

user_event = ['$city', '$province', '$name', '$signup_time', '$utm_matching_type', '$first_visit_time',
              '$first_referrer', '$first_referrer_host', '$first_browser_language', '$first_browser_charset',
              '$first_search_keyword', '$first_traffic_source_type', '$utm_source', '$utm_medium', '$utm_term',
              '$utm_content', '$utm_campaign']


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
            server = '***'
            user = '***'
            password = '*************'

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
        sql = 'select * from {} group by sig '.format(table)  #
        self._reConn()
        # 查询操作
        row = self.cursor.execute(sql)
        self.conn.commit()
        row = self.cursor.fetchall()
        return row

    def query_feild(self, sql):
        self._reConn()
        # 查询操作
        row = self.cursor.execute(sql)
        self.conn.commit()
        row = self.cursor.fetchall()
        return row

    def query_sig_null(self, table):
        sql = "select * from {} where sig=''".format(table)
        self._reConn()
        # 查询操作
        row = self.cursor.execute(sql)
        self.conn.commit()
        row = self.cursor.fetchall()
        return row

    def update(self, table, field, v, id):
        self._reConn()
        # 更新操作
        sql = "UPDATE %s SET `%s`='%s' where id=%s" % (table, field, v, id)
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
    def assert_user(expected, actual, user_property_errors, user_property_type_errors):
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
                        try:
                            if ac_user_property['user_mobile'] not in ''.join([dd[3] for dd in user_property_errors]):
                                user_property_errors.append(('缺少', user_property_name, user_property_show_name,
                                                             str(ac_user_property)))  # ,str(ac_user)
                        except Exception as e:
                            print(ac_user_property)
                            print(e.__str__())

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
                        if ac_user_property_type == None:
                            if key not in ['is_staff', 'is_operator', 'is_landlord', 'is_intermediary']:
                                # if ac_user_property['user_mobile'] not in ''.join([dd[3] for dd in user_property_errors]):
                                user_property_errors.append(
                                    ('缺少', key, ex_user_property_show_name, str(ac_user_property)))  # ,str(ac_user)
                else:
                    user_property_errors.append(('新增', key, key, str(ac_user_property)))  # ,str(ac_user)

    @staticmethod
    def assert_event2(expected, actual, event_name_errors, event_property_errors, event_property_type_errors,
                      event_pro):
        for ac_event in actual:
            try:
                ac_event = json.loads(ac_event[1])
            except Exception as e:
                continue
            all = [e.get('event_name').strip() for e in expected]
            actual_event_name = ac_event.get('event', None)
            try:
                os = ac_event['properties']['$os']
            except:
                os = ''
            if actual_event_name=='instituteViewMoreClick':
                print('instituteViewMoreClick')
            if actual_event_name in all:
                print('神策返回的数据有值')
            else:
                event_name_errors.append(('新增', actual_event_name, actual_event_name, os))

        for ex_data in expected:
            if '' in ex_data.keys():
                ex_data.pop('')
            ex_event_name = ex_data.get('event_name', None)
            ex_event_show_name = ex_data.get('event_show_name', None)
            if ex_event_name == '$AppClick':
                print(ex_event_name)
            ac_event = DB.getInstance().query_feild(
                "select * from test_zuke_event where message_content LIKE '%" + ex_event_name + "%' group by sig order by id desc")
            if len(ac_event) == 0:
                event_name_errors.append(('缺少', ex_event_name, ex_event_show_name, ''))
            else:
                n = 0
                m = 0
                z = 0
                an_flag = False
                ios_flag = False
                ac_os = ''
                for ac_event_every in ac_event:
                    try:
                        rec_time = ac_event_every[3]
                        timeArray = time.localtime(rec_time)
                        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                        ac_event_every = json.loads(ac_event_every[1])
                    except Exception as e:
                        continue

                    ac_event_properties = ac_event_every.get('properties')
                    try:
                        ac_os = ac_event_every['properties']['$os']
                        if ac_os != 'iOS' and ac_os != 'Android':
                            ac_os = ''
                    except:
                        ac_os = ''
                    if ac_os == 'iOS':
                        ios_flag = True
                    if ac_os == 'Android':
                        an_flag = True

                    for ac_key in ac_event_properties.keys():
                        ac_event_properties_type = ac_event_properties.get(ac_key, None)
                        if ac_event_properties_type == '未知':
                            event_property_errors.append(
                                ('未知', ex_event_name, ex_event_show_name, ac_key, ac_key,otherStyleTime, str(ac_event_properties)))
                            continue
                        if ac_key in event_pro.keys():
                            yuzhi_pro_name = event_pro[ac_key]['name']
                            yuzhi_pro_type = event_pro[ac_key]['type']
                            if ac_event_properties_type == '':
                                event_property_type_errors.append(
                                    (ex_event_name, ex_event_show_name, ac_key, yuzhi_pro_name, yuzhi_pro_type,
                                     ac_event_properties_type))
                            else:
                                if (isinstance(ac_event_properties_type, int) or isinstance(ac_event_properties_type,
                                                                                            float)) and yuzhi_pro_type == '数值':
                                    print('神策返回的数据事件的属性类型相同都是数值型')
                                    continue
                                if isinstance(ac_event_properties_type, bool) and (
                                        yuzhi_pro_type == 'BOOL' or yuzhi_pro_type == '布尔值'):
                                    print('神策返回的数据事件的属性类型相同都是bool型')
                                    continue
                                if isinstance(ac_event_properties_type, str) and yuzhi_pro_type == '字符串':
                                    print('神策返回的数据事件的属性类型相同都是字符串型')
                                    continue
                                if isinstance(ac_event_properties_type, str) and yuzhi_pro_type == '字符串':
                                    print('神策返回的数据事件的属性类型相同都是字符串型')
                                    continue
                                else:
                                    type = ''
                                    if isinstance(ac_event_properties_type, datetime.datetime):
                                        type = '日期'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, yuzhi_pro_name, yuzhi_pro_type,
                                             type))
                                        continue
                                    if isinstance(ac_event_properties_type, bool):
                                        type = '布尔值'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, yuzhi_pro_name, yuzhi_pro_type,
                                             type))
                                        continue
                                    if isinstance(ac_event_properties_type, str):
                                        type = '字符串'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, yuzhi_pro_name, yuzhi_pro_type,
                                             type))
                                        continue
                                    if isinstance(ac_event_properties_type, int) or isinstance(ac_event_properties_type,
                                                                                               float):
                                        type = '数值'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, yuzhi_pro_name, yuzhi_pro_type,
                                             type))
                                    else:
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, yuzhi_pro_name, yuzhi_pro_type,
                                             type))
                        else:
                            if ac_key in yuzhi_event:
                                yuzhi_pro_name = event_pro[ac_key]['name']
                                if z <= 2:
                                    event_property_errors.append(
                                        ('缺少', ex_event_name, ex_event_show_name, ac_key, yuzhi_pro_name,otherStyleTime,
                                         str(ac_event_properties)))
                                z = z + 1
                        if ac_key == '$title':
                            print('d')
                        if ac_key in ex_data.keys() and ac_key not in yuzhi_event_all:
                            print('实际数据属性存在')
                            ac_event_properties_type = ac_event_properties.get(ac_key, None)
                            eep_property = ex_data[ac_key]
                            eep_show_name = eep_property.get('property_show_name')
                            eep_type = eep_property.get('type', None)

                            if ac_event_properties_type != None and ac_event_properties_type != '':
                                ##神策返回的数据事件的属性如果在表中存在验证数据属性的类型
                                if (isinstance(ac_event_properties_type, int) or isinstance(ac_event_properties_type,
                                                                                            float)) and eep_type == '数值':
                                    print('神策返回的数据事件的属性类型相同都是数值型')
                                    continue
                                if isinstance(ac_event_properties_type, bool) and (
                                        eep_type == 'BOOL' or eep_type == 'BooL'):
                                    print('神策返回的数据事件的属性类型相同都是bool型')
                                    continue
                                if isinstance(ac_event_properties_type, str) and eep_type == '字符串':
                                    print('神策返回的数据事件的属性类型相同都是字符串型')
                                    continue
                                if isinstance(ac_event_properties_type, str) and eep_type == '字符串':
                                    print('神策返回的数据事件的属性类型相同都是字符串型')
                                    continue
                                else:
                                    type = ''
                                    if isinstance(ac_event_properties_type, datetime.datetime):
                                        type = '日期'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, eep_show_name, eep_type, type))
                                        continue
                                    if isinstance(ac_event_properties_type, bool):
                                        type = 'BOOL'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, eep_show_name, eep_type, type))
                                        continue
                                    if isinstance(ac_event_properties_type, str):
                                        type = '字符串'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, eep_show_name, eep_type, type))
                                        continue
                                    if isinstance(ac_event_properties_type, int) or isinstance(ac_event_properties_type,
                                                                                               float):
                                        type = '数值'
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, eep_show_name, eep_type, type))
                                    else:
                                        event_property_type_errors.append(
                                            (ex_event_name, ex_event_show_name, ac_key, eep_show_name, eep_type, type))

                        else:
                            if n <= 2:
                                if ac_key not in yuzhi_event_all:
                                    if ac_key=='$title':
                                        print(ac_key)
                                    event_property_errors.append(
                                        ('新增', ex_event_name, ex_event_show_name, ac_key, ac_key, otherStyleTime,str(ac_event_properties)))
                                n = n + 1
                    for ex_key in ex_data.keys():

                        if ex_key != 'event_name' and ex_key != 'event_show_name':
                            eep_show_name = ex_data[ex_key]['property_show_name']
                            if ex_key in ac_event_properties.keys():
                                print('excel表中的属性在实际属性中存在')
                            else:
                                if m <= 2:
                                    event_property_errors.append(('缺少', ex_event_name, ex_event_show_name, ex_key,
                                                                  eep_show_name, otherStyleTime,str(ac_event_properties)))
                                m = m + 1
                if ios_flag == False and ac_os != '':
                    event_name_errors.append(('缺少', ex_event_name, ex_event_show_name, 'ios'))
                if an_flag == False and os != '':
                    event_name_errors.append(('缺少', ex_event_name, ex_event_show_name, 'Android'))


class Util:
    @staticmethod
    def getEventPro(property_table):
        event_pro = {}
        user_pro = {}
        num = 0
        for index, data in enumerate(property_table):
            if '用户表' in data[0]:
                num = index + 1
        for index in range(1, num - 2):
            if property_table[index][0] != '' and property_table[index][0] != '字段名称':
                if property_table[index][0] in yuzhi_event:
                    event_pro[property_table[index][0]] = {'type': property_table[index][1],
                                                           'name': property_table[index][2]}
        return event_pro, user_pro

    @staticmethod
    def deleteRepeate(expected):
        expected1 = []
        # name=[]
        for index, i in enumerate(expected):
            event_name = i.get('event_name')
            if not expected1:
                expected1.append(i)
            else:
                last_expected1 = expected1[len(expected1) - 1]
                if event_name == last_expected1.get('event_name'):
                    for key in i:
                        if key not in last_expected1.keys():
                            last_expected1[key] = i[key]
                else:
                    expected1.append(i)

        return expected1

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
            arg[1] = ['', '', '', 'platformType', '平台类型', '字符串', '', '', '', '']
            if data[0] == '事件编号':
                return arg[1:index], index

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

        for index, data in enumerate(arg):
            if index >= index1 + 1:
                e_n = data[1]
                e_s = data[2]
                event_len=[i[1] for i in arg if i[1]==e_n]
                if len(event_len)==1:
                    event_property_table.append(
                                {'event_name': e_n, 'event_show_name': e_s })
        for event_property in event_property_table:
            for j in common_property:
                event_property[str(j[3])] = {'property_show_name': str(j[4]), 'type': j[5]}
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
        sheet1.write(0, 3, "系统版本")
        if event_name_errors:
            for index, value in enumerate(event_name_errors):
                sheet1.write(index + 1, 0, value[0])
                sheet1.write(index + 1, 1, value[1])
                sheet1.write(index + 1, 2, value[2])
                sheet1.write(index + 1, 3, value[3])
        sheet2 = book.add_sheet('事件表-属性校验', cell_overwrite_ok=True)
        sheet2.write(0, 0, "差异类型")
        sheet2.write(0, 1, "事件名称")
        sheet2.write(0, 2, "事件显示名")
        sheet2.write(0, 3, "属性名称")
        sheet2.write(0, 4, "属性显示名")
        sheet2.write(0, 5, "时间")
        sheet2.write(0, 6, "属性实际数据")
        if event_property_errors:
            for index, value in enumerate(event_property_errors):
                sheet2.write(index + 1, 0, value[0])
                sheet2.write(index + 1, 1, value[1])
                sheet2.write(index + 1, 2, value[2])
                sheet2.write(index + 1, 3, value[3])
                sheet2.write(index + 1, 4, value[4])
                sheet2.write(index + 1, 5, value[5])
                sheet2.write(index + 1, 6, value[6])
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
        path = sys.path[0] + '/zuke_report/test_report_{}.xls'.format(now)
        book.save(path)


def run():
    event_name_errors = []
    event_property_errors = []
    event_property_type_errors = []
    re = ReadExcel.getExcelAllData('zuke', '事件表')
    event_table = Util.getEventAndProperty(re, event_name_errors)
    event_table = Util.deleteRepeate(event_table)
    event_rt_db = DB.getInstance().query('test_zuke_event')

    property_table = ReadExcel.getExcelAllData('zuke', '预置属性')
    event_pro, user_pro = Util.getEventPro(property_table)

    AsssertResult.assert_event2(event_table, event_rt_db, event_name_errors, event_property_errors,
                                event_property_type_errors, event_pro)
    # 获取数据库所有的数据
    # 解析数据库数据

    # 查看用户表
    user_property_errors = []
    user_property_type_errors = []
    user_rt_db = DB.getInstance().query('test_zuke_user')
    re = ReadExcel.getExcelAllData('zuke', '用户表')
    user_table = Util.getUserAndProperty(re, event_name_errors)

    AsssertResult.assert_user(user_table, user_rt_db, user_property_errors, user_property_type_errors)

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
    run()
    # sig_nulls = DB.getInstance().query_sig_null('test_zuke_user')
    # for ss in sig_nulls:
    #     tt = Util.generateShield(ss[1])
    #     DB.getInstance().update('test_zuke_user', 'sig', tt, ss[0])
    #     print('插入成功')
    # q_data = DB.getInstance().query('test_zuke_user')
    # for d in q_data:
    #     tt = Util.generateShield(d[1])
    #     DB.getInstance().update('test_zuke_user', 'sig', tt, d[0])
    #     print('插入成功')
    # # for d in q_data:
    #     try:
    #         d1=json.loads(d[1])
    #     except:
    #         print(d)
    #     rec_time =d1.get('time', '')
    #     print(rec_time)
    #     if isinstance(rec_time, int):
    #         rec_time = int(rec_time / 1000)
    #     DB.getInstance().update('test_zuke_user', 'rec_time', rec_time, d[0])
