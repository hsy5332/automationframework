# coding : utf-8
import time
import pymysql
# from automationframework.automationserver import data_read, send_report  # 单独此文件需要开启 windows
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from . import data_read, send_report  # 启动django服务需要开启


class RunWebAutomation:
    # 读取用例
    def read_web_case(self, driver, read_case_rows, read_case_column, read_case_sheel,
                      *browser_configure):  # *browser_configure 是一个元组,里面包含一个浏览器信息列表
        pass_case_count, not_run_case, read_case_count = 0, 0, 1;  # 执行用例的通过数  不执行用例数 从Excel第1个开始,0是列标题
        event_id = time.strftime('%Y%m%d%H%M%S', time.localtime())  # 执行一组用例事件码
        case_report_list = []  # 存放测试结果列表,然后去保存到数据库
        end_case_number = []  # Excel end操作类型标记列表
        if_case_number = []  # Excel if 操作类型标记列表
        for if_end_count in range(1, read_case_rows):  # if_end_count if和end 计数器
            operate_types = read_case_sheel.row_values(if_end_count)[1]  # 获取Excel所有操作类型
            if 'if' in operate_types:
                if_case_number.append(if_end_count)  # 获取操作类型为if 在Excel中的序号
            if 'end' in operate_types:
                end_case_number.append(if_end_count)  # 获取操作类型为end 在Excel中的序号
        if_number = 0;  # 当前if 计数器
        while read_case_count < read_case_rows:
            case_id = int(read_case_sheel.row_values(read_case_count)[0])  # 用例编号
            operate_type = read_case_sheel.row_values(read_case_count)[1]  # 操作类型
            element_attribute = read_case_sheel.row_values(read_case_count)[2]  # 元素属性
            parameter = str(read_case_sheel.row_values(read_case_count)[3])  # 参数 必须要转成字符串，要不然在使用send_keys时无法使用
            case_describe = read_case_sheel.row_values(read_case_count)[5]  # 描述步骤
            case_execute = read_case_sheel.row_values(read_case_count)[6]  # 执行状态
            print(case_id, operate_type, element_attribute, parameter, case_describe, case_execute)
            start_one_case_time = time.time()  # 开始执行单个用例时间
            if '1' in case_execute or 'Y' in case_execute or 'y' in case_execute:
                if '等待时间' in operate_type:
                    time.sleep(element_attribute)
                    case_report = '用例编号:%s,执行通过。' % case_id
                    print(case_report)
                elif '点击_' in operate_type:
                    RunWebAutomation.operate_click(self, driver, case_id, operate_type, element_attribute)
                elif '输入_' in operate_type:
                    RunWebAutomation.operate_input(self, driver, case_id, operate_type, element_attribute, parameter)
                elif '清空_' in operate_type:
                    RunWebAutomation.clear_input(self, driver, case_id, operate_type, element_attribute)
                elif '查找_' in operate_type:
                    RunWebAutomation.operate_check_element(self, driver, case_id, operate_type, element_attribute)
                elif '右击_' in operate_type:
                    RunWebAutomation.operate_right_click(self, driver, case_id, operate_type, element_attribute)
                elif '双击_' in operate_type:
                    RunWebAutomation.operate_double_click(self, driver, case_id, operate_type, element_attribute)
                elif '按' in operate_type or 'pagedown' in operate_type or 'pageup' in operate_type or '浏览器全屏' in operate_type or '设置分辨率' in operate_type:
                    RunWebAutomation.operate_physics_key(self, driver, case_id, operate_type, element_attribute)
                elif "if" in operate_type:
                    case_report = RunWebAutomation.operate_check_element(self, driver, case_id, operate_type,
                                                                         element_attribute)
                    if "执行通过" not in case_report:
                        print(case_report)
                        if len(end_case_number) == len(if_case_number):
                            read_case_count = end_case_number[if_number]
                        else:
                            print("当前用例中的if和and不等，请检查用例")
                            read_case_count = end_case_number[-1]  # end和if 不等时,会从用例最后一个end开始执行
                    if_number += 1;
                elif 'end' in operate_type:
                    case_report = '用例编号:%s,执行通过。' % case_id
                    print(case_report)
                else:
                    case_report = "用例编号:%s操作类型错误,该用例不执行。" % (case_id)
                    print(case_report)
                if '执行通过' in case_report:
                    pass_case_count += 1;  # 当用例执行通过，则加1
            else:
                not_run_case += 1;
                print('用例编号:%s,执行状态为No,故不执行。' % case_id)
            end_one_case_time = time.time()  # 结束执行单个用例时间
            run_one_case_time = round(end_one_case_time - start_one_case_time)  # 单个用例执行时间
            case_report_dictionary = {
                'browsername': browser_configure[0][0],
                'browserconfigure': browser_configure[0][1],
                'testurl': browser_configure[0][2],
                'browserstatus': browser_configure[0][3],
                'caseid': case_id,
                'operatetype': operate_type,
                'element': element_attribute,
                'parameter': parameter,
                'rundescribe': case_describe,
                'caseexecute': case_execute,
                'runcasetime': run_one_case_time,
                'eventid': event_id,
                'casereport': case_report,
                'createdtime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'updatetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            }
            case_report_list.append(case_report_dictionary)
            read_case_count += 1;
        return pass_case_count, not_run_case, case_report_list  # 返回执行用例通过数和执行结果列表

    # 执行用例
    def run_web_case(self, file_name, run_case_type):
        excel_shell_name = data_read.DataRead().gain_shell_name(run_case_type)  # 获取工作薄名称
        pass_case_counts, case_rows_counts = 0, 0;  # 执行用例的通过数和执行的总用例数
        # 获取配置工作薄信息
        configure_case_rows, configure_case_column, configure_sheel = data_read.DataRead().read_case_file(file_name,
                                                                                                          excel_shell_name[
                                                                                                              0])
        # 获取用例工作薄信息
        read_case_rows, read_case_column, read_case_sheel = data_read.DataRead().read_case_file(file_name,
                                                                                                excel_shell_name[1])
        run_web_event_id = time.strftime('%Y%m%d%H%M%S', time.localtime())
        start_run_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 执行用例时间
        for i in range(1, configure_case_rows):
            browser_name = configure_sheel.row_values(i)[0]  # 浏览器名称
            browser_configure_path = configure_sheel.row_values(i)[1]  # 浏览器配置目录 一般是火狐浏览器用到
            test_url = configure_sheel.row_values(i)[2]  # 测试网站
            browser_execute_status = configure_sheel.row_values(i)[3]  # 浏览器执行状态
            browser_configure = [browser_name, browser_configure_path, test_url,
                                 browser_execute_status]  # 把读取出来的浏览器信息存入在列表中
            if '1' in browser_execute_status or 'Y' in browser_execute_status or 'y' in browser_execute_status:
                case_rows_counts += (read_case_rows - 1);  # 用例总数
                driver = RunWebAutomation.start_web_browser(self, browser_name, browser_configure_path)
                if driver != False:
                    driver.get(test_url)  # 打开测试的网站
                    pass_case_count, not_run_case, case_report_list = RunWebAutomation.read_web_case(self, driver,
                                                                                                     read_case_rows,
                                                                                                     read_case_column,
                                                                                                     read_case_sheel,
                                                                                                     browser_configure)  # 读取运行的测试用例,获取执行通过用例数和结果列表
                    pass_case_counts += pass_case_count;  # 得到通过用例总数
                    driver.quit()  # 退出浏览器
                    try:
                        mysql_cursor, connect_mysql = data_read.DataRead().save_database()  # 获取数据库游标 游标执行sql,以及连接的变量用于关闭数据连接
                        if len(case_report_list) > 0:
                            execute_sql_count = 0;  # 执行sql数据计数器
                            while execute_sql_count < len(case_report_list):
                                element =  str(case_report_list[execute_sql_count].get('element'))
                                if '"' in element:
                                    element = pymysql.escape_string(element)
                                execute_sql = "insert into automationquery_automation_function_web  (`browsername`,`browserconfigure`,`browserstatus`,`operatetype`,`element`,`parameter`,`testurl`,`rundescribe`,`caseexecute`,`runcasetime`,`caseid`,`eventid`,`casereport`,`createdtime`,`updatetime`)VALUES('%s','%s','%s','%s',\"%s\",'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                                    case_report_list[execute_sql_count].get('browsername'),
                                    case_report_list[execute_sql_count].get('browserconfigure'),
                                    case_report_list[execute_sql_count].get('browserstatus'),
                                    case_report_list[execute_sql_count].get('operatetype'),
                                    element,
                                    case_report_list[execute_sql_count].get('parameter'),
                                    case_report_list[execute_sql_count].get('testurl'),
                                    case_report_list[execute_sql_count].get('rundescribe'),
                                    case_report_list[execute_sql_count].get('caseexecute'),
                                    case_report_list[execute_sql_count].get('runcasetime'),
                                    case_report_list[execute_sql_count].get('caseid'),
                                    case_report_list[execute_sql_count].get('eventid'),
                                    case_report_list[execute_sql_count].get('casereport'),
                                    str(case_report_list[execute_sql_count].get('createdtime')),
                                    str(case_report_list[execute_sql_count].get('updatetime')),
                                )
                                mysql_cursor.execute(execute_sql)
                                execute_sql_count += 1;
                            connect_mysql.commit()  # 提交数据
                            connect_mysql.close()  # 关闭数据库连接
                        else:
                            print('无任何数据写入数据库中')
                    except:
                        print("保存数据失败。")
            else:
                print('浏览%s,状态为不执行，故该浏览器上不运行用例。' % browser_execute_status)
                try:
                    mysql_cursor, connect_mysql = data_read.DataRead().save_database()  # 获取数据库游标 游标执行sql,以及连接的变量用于关闭数据连接
                    execute_sql = "insert into automationquery_automation_function_web  (`browsername`,`browserconfigure`,`browserstatus`,`operatetype`,`element`,`parameter`,`testurl`,`rundescribe`,`caseexecute`,`runcasetime`,`caseid`,`eventid`,`casereport`,`createdtime`,`updatetime`)VALUES('%s','%s','%s','%s',\"%s\",'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
                        browser_name, browser_configure_path, browser_execute_status, '', '', '', '', '', '', '', '',
                        run_web_event_id, '', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    mysql_cursor.execute(execute_sql)
                    connect_mysql.commit()  # 提交数据
                    connect_mysql.close()  # 关闭数据库连接
                except:
                    print("保存数据失败。")
        if send_report.SendReport().sender_email(start_run_time, case_rows_counts, pass_case_counts,
                                                 not_run_case):  # 发送邮件
            print('邮件发送成功')
        else:
            print('发送邮件失败')

    # 启动浏览器
    def start_web_browser(self, browser_name, browser_configure_path):
        try:
            if 'google' in browser_name or '谷歌' in browser_name:
                driver = webdriver.Chrome()
                return driver

            elif 'firefox' in browser_name or '火狐' in browser_name:
                if browser_configure_path == '':
                    driver = webdriver.Firefox()
                    return driver
                else:
                    try:
                        driver = webdriver.Firefox(webdriver.FirefoxOptions(browser_configure_path))
                        return driver
                    except:
                        print('请检查Excel中浏览器配置目录列是否填写正确。')
                        return driver
            else:
                print('您的测试用例中，存在无法识别的浏览器名称，请检查用例。')
                driver = False
                return driver
        except:
            print('启动浏览器失败请检查webdriver对应的浏览器配置文件是否正确,启动失败的浏览器是%s' % browser_name)
            driver = False
            return driver

    # 双击操作
    def operate_double_click(self, driver, case_id, operate_type, element):
        if operate_type == "双击_id":
            try:
                driver.find_element_by_id(element).double_click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "双击_xpath":
            try:
                driver.find_element_by_xpath(element).double_click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "双击_textname":  # 点击textname
            try:
                driver.find_elements_by_name(element)[0].double_click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "双击_classname":
            try:
                driver.find_elements_by_class_name(element)[0].double_click()  # 点击xpath
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "双击_linkname":
            try:
                driver.find_elements_by_link_text(element)[0].double_click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 右点击击操作
    def operate_right_click(self, driver, case_id, operate_type, element):
        if operate_type == "右击_id":
            try:
                driver.find_element_by_id(element).context_click().perform()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "右击_xpath":
            try:
                driver.find_element_by_xpath(element).context_click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "右击_textname":  # 点击textname
            try:
                driver.find_elements_by_name(element)[0].context_click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "右击_classname":
            try:
                driver.find_elements_by_class_name(element)[0].context_click()  # 点击xpath
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "右击_linkname":
            try:
                driver.find_elements_by_link_text(element)[0].context_click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 左点击击操作
    def operate_click(self, driver, case_id, operate_type, element):
        if operate_type == "点击_id":
            try:
                driver.find_element_by_id(element).click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "点击_xpath":
            try:
                driver.find_element_by_xpath(element).click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "点击_textname":  # 点击textname
            try:
                driver.find_elements_by_name(element)[0].click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "点击_classname":
            try:
                driver.find_elements_by_class_name(element)[0].click()  # 点击xpath
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "点击_linkname":
            try:
                driver.find_elements_by_link_text(element)[0].click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        # 扩展性 查找元素方法
        elif operate_type == "点击_cssid":
            try:
                driver.find_element_by_css_selector("#%s" % (element)).click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "点击_cssname":
            try:
                driver.find_element_by_css_selector("a[name=\"%s\"]" % (element)).click()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 检查元素是否存在
    def operate_check_element(self, driver, case_id, operate_type, element):
        if operate_type == "查找_id":
            try:
                driver.find_element_by_id(element)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "查找_xpath":
            try:
                driver.find_element_by_xpath(element)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "查找_textname":  # 查找textname
            try:
                driver.find_elements_by_name(element)[0]
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        elif operate_type == "查找_classname":
            try:
                driver.find_elements_by_class_name(element)[0]
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "查找_linkname":
            try:
                driver.find_elements_by_link_text(element)[0]
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "if包含_id":
            try:
                driver.find_element_by_id(element)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "if包含_xpath":
            try:
                driver.find_element_by_xpath(element)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "if包含_textname":
            try:
                driver.find_elements_by_name(element)[0]
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "if包含_classname":
            try:
                driver.find_elements_by_class_name(element)[0]
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "if包含_linkname":
            try:
                driver.find_elements_by_link_text(element)[0]
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 清空输入框
    def clear_input(self, driver, case_id, operate_type, element):
        if operate_type == "清空输入框_id":
            try:
                driver.find_element_by_id(element).clear()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "清空输入框_xpath":
            try:
                driver.find_element_by_xpath(element).clear()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "清空输入框_textname":
            try:
                driver.find_elements_by_name(element)[0].clear()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 输入操作
    def operate_input(self, driver, case_id, operate_type, element, *parameter):
        if operate_type == "输入_id":
            try:
                driver.find_element_by_id(element).send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "输入_xpath":
            try:
                driver.find_element_by_xpath(element).send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "输入_textname":
            try:
                driver.find_elements_by_name(element)[0].send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report

        # 扩展性 查找元素方法
        elif operate_type == "输入_cssid":
            try:
                driver.find_element_by_css_selector("#%s" % (element)).send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "输入_cssname":
            try:
                driver.find_element_by_css_selector("a[name=\"%s\"]" % (element)).send_keys(parameter[0])
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report

    # 物理按鍵操作
    def operate_physics_key(self, driver, case_id, operate_type, element):
        if operate_type == "按enter_id":
            try:
                driver.find_element_by_id(element).send_keys(Keys.ENTER)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "按enter_xpath":
            try:
                driver.find_element_by_xpath(element).send_keys(Keys.ENTER)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "按enter_textname":
            try:
                driver.find_elements_by_name(element)[0].send_keys(Keys.ENTER)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "pagedown_id":
            try:
                driver.find_element_by_id(element).send_keys(Keys.PAGE_DOWN)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "pagedown_xpath":
            try:
                driver.find_element_by_xpath(element).send_keys(Keys.PAGE_DOWN)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "pagedown_textname":
            try:
                driver.find_elements_by_name(element)[0].send_keys(Keys.PAGE_DOWN)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "pageup_id":
            try:
                driver.find_element_by_id(element).send_keys(Keys.PAGE_UP)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "pageup_xpath":
            try:
                driver.find_element_by_xpath(element).send_keys(Keys.PAGE_UP)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "pageup_textname":
            try:
                driver.find_elements_by_name(element)[0].send_keys(Keys.PAGE_UP)
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "浏览器全屏":
            try:
                driver.maximize_window()
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        elif operate_type == "设置分辨率":
            try:
                windowslist = element.split(',')
                driver.set_window_size(int(windowslist[0]), int(windowslist[1]))
                case_report = "用例编号:%s,执行通过。" % (case_id)
                return case_report
            except:
                case_report = "用例编号:%s,执行不通过。" % (case_id)
                return case_report
        else:
            case_report = "用例编号:%s,执行不通过，该用例的元素属性或参数可能有问题，请检查该用例。" % (case_id)
            return case_report


if __name__ == "__main__":
    RunWebAutomation().run_web_case("web_function_case.xlsx", 'web')
