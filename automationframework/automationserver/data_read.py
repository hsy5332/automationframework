# coding : utf-8
import os
import xlrd


class DataRead:

    # 检查测试用例文件是否存在
    def check_case_file(self, file_name):
        file_path = os.getcwd() + '\\automationserver\\automationtestcase\\' + str(file_name)
        if os.path.exists(file_path):  # 判断是否存在该测试用例文件
            return True
        else:
            return False

    # 获取Excel工作薄名 runcasetype值：app interface web
    def gain_shell_name(self, run_case_type):
        if run_case_type == 'app':
            return ['appdeviceinfo', 'appfuncase']  # 若有配置表格,第一个必须是配置表格
        elif run_case_type == 'interface':
            return ['interfacecase']
        elif run_case_type == 'web':
            return ['browserinfo', 'browseefuncase']
        else:
            pass

    # 读取Excel数据
    def read_case_file(self, file_name, sheel_name):
        case_file_path = os.getcwd() + '\\automationtestcase\\' + str(file_name)  # 测试环境地址
        #case_file_path = os.getcwd() + '\\automationserver\\automationtestcase\\' + str(file_name)  # Djngo环境地址
        open_excel_case = xlrd.open_workbook(case_file_path)  # 打开Excel 文件
        case_sheel = open_excel_case.sheet_by_name(sheel_name)  # 读取工作簿
        case_nows = case_sheel.nrows  # 读取Excel总行数
        case_column = case_sheel.ncols  # 读取Excel总列数
        return case_nows, case_column, case_sheel



if __name__ == "__main__":
    DataRead().check_case_file('app_function_case.xlsx')
