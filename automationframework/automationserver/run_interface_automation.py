# coding : utf-8

import requests
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
        run_case_now_count = 1;  # 遍历用例表格计数器 从1 开始 第一行不算
        while run_case_now_count < read_case_rows:
            interface_case_id = int(read_case_sheel.row_values(run_case_now_count)[0])  # 获取case id
            interface_url = read_case_sheel.row_values(run_case_now_count)[1]  # 接口地址
            request_interface_header = read_case_sheel.row_values(run_case_now_count)[2]  # 请求头
            quote_interface_header = read_case_sheel.row_values(run_case_now_count)[3]  # 引用接口请求头
            request_parameter = read_case_sheel.row_values(run_case_now_count)[4]  # 请求参数
            interface_request_type = read_case_sheel.row_values(run_case_now_count)[5]  # 请求方式
            correlation_interface = read_case_sheel.row_values(run_case_now_count)[6]  # 关联接口
            correlation_interface_parameter = read_case_sheel.row_values(run_case_now_count)[7]  # 关联接口参数
            interface_execute_status = str(read_case_sheel.row_values(run_case_now_count)[8])  # 执行状态 1 执行 0 不执行
            interface_case_remark = read_case_sheel.row_values(run_case_now_count)[9]  # 备注
            if '1' in interface_execute_status or 'Y' in interface_execute_status or 'y' in interface_execute_status:
                if interface_url != '' and interface_request_type != '':
                    calling_method_parameter = [interface_url, request_interface_header, quote_interface_header, request_parameter,
                                                interface_request_type, correlation_interface, correlation_interface_parameter]  # 把请求接口的参数存放在列表中
                    case_report = self.interface_request(calling_method_parameter)

                    calling_method_parameter.clear();  # 在使用完数据后,清空列表
                else:
                    case_report = '用例编号:%s,接口地址或请求方式为空,故不执行。' % (interface_case_id)
                    print(case_report)
            else:
                case_report = '用例编号:%s,执行状态为No,故不执行。' % (interface_case_id)
                print(case_report)
            run_case_now_count += 1;

    # 请求接口
    def interface_request(self, calling_method_parameter):
        interface_url, request_interface_header, quote_interface_header, request_parameter, interface_request_type, correlation_interface, correlation_interface_parameter = \
            calling_method_parameter[0], calling_method_parameter[1], calling_method_parameter[2], calling_method_parameter[3], \
            calling_method_parameter[4], calling_method_parameter[5], calling_method_parameter[6]
        # 接口地址 请求头  引用接口请求头 请求参数 请求方式 关联接口 关联接口参数
        if interface_request_type == 'get' or interface_request_type == 'GET':
            pass
        elif interface_request_type == 'post' or interface_request_type == 'POST':
            pass
        else:
            return False


if __name__ == '__main__':
    RunInterfaceAutomation('interface_case.xlsx', 'interface').run_interface_case()
