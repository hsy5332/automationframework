# coding : utf-8

import requests
import json
import time
from automationframework.automationserver import data_read, send_report  # 单独此文件需要开启 windows


# from automationserver import data_read, send_report  # 启动django服务需要开启


class RunInterfaceAutomation:
    def __init__(self, file_name, run_case_type):
        self.file_name = file_name  # file_name 测试用例名称
        self.run_case_type = run_case_type

    # 读取接口测试用例
    def read_interface_case(self):
        excel_shell_name = data_read.DataRead().gain_shell_name(self.run_case_type)
        read_case_rows, read_case_column, read_case_sheel = data_read.DataRead().read_case_file(self.file_name, excel_shell_name[0])
        return read_case_rows, read_case_column, read_case_sheel

    # 运行接口测试用例
    def run_interface_case(self):
        read_case_rows, read_case_column, read_case_sheel = self.read_interface_case()
        pass_case_counts, not_run_case, run_case_now_count, = 0, 0, 1;  # 用例通过数 和 遍历用例表格计数器 从1 开始 第一行不算
        report_request_datas = []  # 存放请求数据以及返回结果
        case_report_data_list = []  # 存放Excel原始数据以及真实请求数据，以及 返回数据
        start_run_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 执行用例时间
        run_interface_event_id = time.strftime('%Y%m%d%H%M%S', time.localtime())  # 事件编码
        while run_case_now_count < read_case_rows:
            interface_case_id = int(read_case_sheel.row_values(run_case_now_count)[0])  # 获取case id
            interface_url = read_case_sheel.row_values(run_case_now_count)[1]  # 接口地址
            try:
                request_interface_header = eval(read_case_sheel.row_values(run_case_now_count)[2])  # 请求头

            except:
                request_interface_header = '';  # 请求头一定是字典格,如果转化错误,则参数为空
            read_excel_interface_header = request_interface_header;  # 保存一份 Excel默认的请求头

            try:
                quote_interface_header = int(read_case_sheel.row_values(run_case_now_count)[3])  # 引用接口请求头
            except:
                quote_interface_header = '';  # 如果无法转换引用接口请求头 就置为空

            try:
                request_parameter = eval(read_case_sheel.row_values(run_case_now_count)[4])  # 请求参数
            except:
                request_parameter = '';  # 请求参数一定是字典格,如果转化错误,则参数为空
            read_excel_interface_parameter = request_parameter  # 保存一份 Excel默认的请求参数

            interface_request_type = read_case_sheel.row_values(run_case_now_count)[5]  # 请求方式

            try:
                correlation_interface = int(read_case_sheel.row_values(run_case_now_count)[6])  # 关联接口
            except:
                correlation_interface = '';  # 如果无法转换 关联接口 就置为空
            interface_execute_status = str(read_case_sheel.row_values(run_case_now_count)[7])  # 执行状态 1 执行 0 不执行
            interface_case_remark = read_case_sheel.row_values(run_case_now_count)[8]  # 备注
            if '1' in interface_execute_status or 'Y' in interface_execute_status or 'y' in interface_execute_status:
                if len(interface_url) > 0 and interface_request_type != '':
                    if quote_interface_header != '' and interface_case_id > 1 and quote_interface_header < interface_case_id:  # 判断当前引用请求头接口是否小于当前用例id以及不等于空以及caseid 大于1
                        try:
                            request_interface_header = report_request_datas[quote_interface_header - 1]['headers']
                        except:
                            print('用例编号: %s,引用请求头接口数据出错,请检查引用请求头接口是否请求成功' % interface_case_id)
                    if correlation_interface != '' and interface_case_id > 1 and correlation_interface < interface_case_id:
                        try:
                            report_request_dic = report_request_datas[correlation_interface - 1]['request_report']
                            for report_request_dic_index, report_request_dic_element in report_request_dic.items():
                                for request_parameter_index, request_parameter_element in request_parameter.items():
                                    if request_parameter_element == report_request_dic_index:
                                        request_parameter[request_parameter_index] = report_request_dic[report_request_dic_index]
                                    if isinstance(report_request_dic_element, dict):
                                        for element_index, element in report_request_dic_element.items():
                                            if request_parameter_element == element_index:
                                                request_parameter[request_parameter_index] = report_request_dic_element[element_index]
                                    if isinstance(report_request_dic_element, list):
                                        for list_index, list_element in enumerate(report_request_dic_element):
                                            if isinstance(list_element, dict):
                                                for dict_index, dict_element in list_element.items():
                                                    if request_parameter_element == dict_index:
                                                        request_parameter[request_parameter_index] = list_element[dict_index]
                        except:
                            print('用例编号: %s,引用关联接口数据出错,请检查关联接口是否请求成功' % interface_case_id)
                        # 遍历取数据接口返回数据和遍历当前请求参数,判断当前请求参数是否有取接口返回数据值如有则取出相应的值
                    calling_method_parameter = [interface_url, request_interface_header, request_parameter, interface_request_type]  # 把请求接口的参数存放在列表中
                    report_data_dic = self.interface_request(calling_method_parameter)
                    # print(report_request_datas)  # 打印返回结果
                    report_request_datas.append(report_data_dic)
                    calling_method_parameter.clear();  # 在使用完数据后,清空列表

                    if report_data_dic != False:
                        if len(report_data_dic) > 0:
                            case_report = '用例编号: %s,执行通过。' % interface_case_id
                            print(case_report)
                        else:
                            case_report = '用例编号: %s,执行不通过。' % interface_case_id
                            print(case_report)
                    else:
                        case_report = '用例编号: %s,执行不通过。' % interface_case_id
                        print(case_report)
                else:
                    case_report = '用例编号:%s,接口地址或请求方式为空,故不执行。' % interface_case_id
                    print(case_report)
            else:
                case_report = '用例编号:%s,执行状态为No,故不执行。' % interface_case_id
                print(case_report)

            case_report_data_dic = {
                'event_id': run_interface_event_id,
                'interface_case_id': interface_case_id,  # caseID
                'interface_url': interface_url,  # 请求URL
                'read_excel_interface_header': read_excel_interface_header,  # excel 中的请求头
                'request_interface_header': request_interface_header,  # 实际的请求头
                'quote_interface_header': quote_interface_header,  # 引用请求的用例编号
                'read_excel_interface_parameter': read_excel_interface_parameter,  # excel 中的请求参数
                'request_parameter': request_parameter,  # 实际的请求参数
                'interface_request_type': interface_request_type,  # 接口请求类型
                'correlation_interface': correlation_interface,  # 关联接口 用例编号
                'interface_execute_status': interface_execute_status,  # 用例执行状态
                'interface_case_remark': interface_case_remark,  # 备注
                'report_data_dic': report_data_dic,  # 接口返回数据
                'createdtime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'updatetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
            case_report_data_list.append(case_report_data_dic)
            if '执行通过' in case_report:
                pass_case_counts += 1;
            elif '故不执行' in case_report:
                not_run_case += 1;
            else:
                pass

            run_case_now_count += 1;

        if send_report.SendReport().sender_email(start_run_time, run_case_now_count - 1, pass_case_counts,
                                                 not_run_case):  # 发送邮件
            print('邮件发送成功')
        else:
            print('发送邮件失败')
        mysql_cursor, connect_mysql = data_read.DataRead().save_database()  # 获取数据库游标 游标执行sql,以及连接的变量用于关闭数据连接
        if len(case_report_data_list) > 0:
            execute_sql_count = 0;  # 执行sql数据计数器
            while execute_sql_count < len(case_report_data_list):
                execute_sql = "insert into automationquery_automation_interface  (`interfaceurl`,`requestparameter`,`realheader`,`realparameter`,`associationinterface`,`referenceinterfaceheader`,`casestatus`,`requesttype`,`caseid`,`remark`,`returnparameter`,`createdtime`,`updatetime`,`eventid`)VALUES(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",'%s','%s','%s')" % (
                    case_report_data_list[execute_sql_count].get('interface_url'),
                    case_report_data_list[execute_sql_count].get('read_excel_interface_parameter'),
                    case_report_data_list[execute_sql_count].get('request_interface_header'),
                    case_report_data_list[execute_sql_count].get('request_parameter'),
                    case_report_data_list[execute_sql_count].get('correlation_interface'),
                    case_report_data_list[execute_sql_count].get('quote_interface_header'),
                    case_report_data_list[execute_sql_count].get('interface_execute_status'),
                    case_report_data_list[execute_sql_count].get('interface_request_type'),
                    case_report_data_list[execute_sql_count].get('interface_case_id'),
                    case_report_data_list[execute_sql_count].get('interface_case_remark'),
                    case_report_data_list[execute_sql_count].get('report_data_dic').get('request_report'),
                    str(case_report_data_list[execute_sql_count].get('createdtime')),
                    str(case_report_data_list[execute_sql_count].get('updatetime')),
                    case_report_data_list[execute_sql_count].get('run_interface_event_idrun_interface_event_id'),
                )
                mysql_cursor.execute(execute_sql)
                execute_sql_count += 1;
            connect_mysql.commit()  # 提交数据

            
            connect_mysql.close()  # 关闭数据库连接
        else:
            print('无任何数据写入数据库中')

    # 请求接口
    def interface_request(self, calling_method_parameter):
        report_data_dic = {}  # 请求数据和返回数据
        interface_url, request_interface_header, request_parameter, interface_request_type, = calling_method_parameter[0], calling_method_parameter[
            1], calling_method_parameter[2], calling_method_parameter[3]
        # 接口地址 请求头 请求参数 请求方式
        if interface_request_type == 'get' or interface_request_type == 'GET':
            request_interface_report = requests.get(interface_url, params=request_parameter, headers=request_interface_header)
        elif interface_request_type == 'post' or interface_request_type == 'POST':
            request_interface_report = requests.post(interface_url, data=request_parameter, headers=request_interface_header)
        else:
            return False

        try:
            request_report_data_transfer = json.loads(request_interface_report.text)
            report_data_dic = {
                'url': interface_url,
                'headers': request_interface_header,
                'params': request_parameter,
                'request_report': request_report_data_transfer
            }
        except:
            pass
        return report_data_dic


if __name__ == '__main__':
    RunInterfaceAutomation('interface_case.xlsx', 'interface').run_interface_case()
