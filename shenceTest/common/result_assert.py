class AsssertResult:
    @staticmethod
    def assert_event(expected,actual,event_name_errors,event_property_errors,event_property_type_errors):
        for ex_event_1 in expected:
            is_actual_event_name = False
            ex_event_name_1 = ex_event_1.get('event_name', None)
            for ac_event_1 in actual:
                ac_event_name_1 = ac_event_1.get('event')
                if ac_event_name_1 == ex_event_name_1:
                    is_actual_event_name = True
            if is_actual_event_name:
                print('神策返回的数据有值')
            else:
                if ex_event_name_1 != '':
                    event_name_errors.append(('缺少', ex_event_name_1))

        for ac_event in actual:
            actual_event_name = ac_event.get('event', None)
            is_event_name = False
            for ex_event in expected:
                expected_event_name = ex_event.get('event_name', None)
                if actual_event_name == expected_event_name:
                    is_event_name = True
            if is_event_name:
                print('神策返回的数据有值')
            else:
                event_name_errors.append(('新增', actual_event_name))

        for ac_event in actual:
            actual_event_name = ac_event.get('event', None)
            if actual_event_name not in event_name_errors and actual_event_name not in event_name_errors:
                actual_event_property = ac_event.get('properties')
                for ex_event1 in expected:
                    if actual_event_name == ex_event1['event_name']:
                        for ex_key in ex_event1.keys():
                            if ex_key != 'event_name' and ex_key != 'event_show_name':
                                aep_type = actual_event_property.get(ex_key, None)
                                if aep_type:
                                    print('神策返回的数据中事件{}的属性{}存在'.format(actual_event_name, ex_key))
                                    ##神策返回的数据事件的属性如果在表中存在验证数据属性的类型
                                    eep_type = ex_event1[ex_key]
                                    if (isinstance(aep_type, int) or isinstance(aep_type, float)) and eep_type == '数值':
                                        print('神策返回的数据事件的属性类型相同都是数值型')
                                        continue
                                    if isinstance(aep_type, bool) and eep_type == 'BOOL':
                                        print('神策返回的数据事件的属性类型相同都是bool型')
                                        continue
                                    if isinstance(aep_type, str) and eep_type == '字符串':
                                        print('神策返回的数据事件的属性类型相同都是字符串型')
                                        continue
                                    else:
                                        event_property_type_errors.append(
                                            (actual_event_name, ex_key, eep_type, aep_type))

                                else:
                                    event_property_errors.append(('缺少', actual_event_name, ex_key))
                is_add_event_property = False
                for ac_key in actual_event_property.keys():
                    for ex_event2 in expected:
                        if ac_key in ex_event2:
                            is_add_event_property = True
                if is_add_event_property:
                    print('神策返回的数据中事件{}的属性{}存在'.format(actual_event_name, ac_key))
                else:
                    event_property_errors.append(('新增', actual_event_name, ac_key))

    @staticmethod
    def assert_user(expected,actual, user_property_errors, user_property_type_errors):
        for ex_user in expected:
            user_property_type = ex_user.get('user_property_type')
            user_property_name = ex_user.get('user_property_name')
            user_property_show_name = ex_user.get('user_property_show_name')
            if not user_property_show_name:
                user_property_errors.append(('excel表中属性显示名为空', user_property_name, user_property_show_name))
            if not user_property_name:
                user_property_errors.append(('excel表中属性名称为空', user_property_name, user_property_show_name))
            if not user_property_type:
                user_property_type_errors.append(
                    ('excel表中属性名称为空', user_property_name, user_property_show_name, user_property_type))
            for ac_user in actual:
                ac_user_property = ac_user.get('properties')
                ac_user_property_type = ac_user.get(user_property_name, None)
                if ac_user_property_type:
                    print('神策返回的消息有数据')
                else:
                    user_property_errors(('缺少', user_property_name, user_property_show_name))

        for ac_user in actual:
            user_property_type = ac_user.get('properties')
            user_property_name = ac_user.get('event')
            if not user_property_name:
                user_property_errors.append(
                    ('神策订阅的消息属性显示名为空', user_property_name, user_property_show_name, user_property_type))
            if not user_property_name:
                user_property_errors.append(
                    ('excel表中属性名称为空', user_property_name, user_property_show_name, user_property_type))
            if not user_property_type:
                user_property_type_errors.append(
                    ('excel表中属性名称为空', user_property_name, user_property_show_name, user_property_type))

