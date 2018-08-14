# coding : utf-8
import os
import xlrd
import pymysql


class DataRead:
    # 检查测试用例文件是否存在
    def check_case_file(self, file_name):
        #file_path = os.getcwd() + '/automationtestcase/' + str(file_name)  # 本地开启
        file_path = os.getcwd() + '/automationserver/automationtestcase/' + str(file_name) #djngo服务开启
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
        #case_file_path = os.getcwd() + '/automationtestcase/' + str(file_name)  # 测试环境地址
        case_file_path = os.getcwd() + '/automationserver/automationtestcase/' + str(file_name)  # Djngo环境地址
        open_excel_case = xlrd.open_workbook(case_file_path)  # 打开Excel 文件
        case_sheel = open_excel_case.sheet_by_name(sheel_name)  # 读取工作簿
        case_nows = case_sheel.nrows  # 读取Excel总行数
        case_column = case_sheel.ncols  # 读取Excel总列数
        return case_nows, case_column, case_sheel

    # 连接数据库
    def save_database(self):
        # 线上环境数据库配置
        # connect_mysql = pymysql.connect(
        #     host='steel.iask.in',
        #     port=33067,
        #     user='huangshunyao',
        #     password='Hsy5332#',
        #     db='automation_db',
        #     charset='utf8',  # 解决中文乱码
        # )
        # # 本地环境数据库配置
        # connect_mysql = pymysql.connect(
        #     host='192.168.100.6',
        #     port=33006,
        #     user='huangshunyao',
        #     passwd='Hsy5332#',
        #     db='automation_db',
        #     charset='utf8',  # 解决中文乱码
        # )

        connect_mysql = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='',
            db='automation_db',
            charset='utf8',  # 解决中文乱码
        )
        mysql_cursor = connect_mysql.cursor()  # 获取游标
        return mysql_cursor, connect_mysql  # 执行语句用mysql_cursor，关闭和提交 由返回connect_mysql 去控制 提交和关闭


if __name__ == "__main__":
    DataRead().check_case_file('app_function_case.xlsx')
    # mysql_cursor, connect_mysql = DataRead().save_database()
    # mysql_cursor.execute(
    #     "insert into automationquery_automation_function_app  (`devicesinfos`,`appiumport`,`devicesexecute`,`operatetype`,`element`,`parameter`,`rundescribe`,`caseexecute`,`runcasetime`,`caseid`,`eventid`,`casereport`,`createdtime`,`updatetime`)VALUES('%s','%s','%s','%s',\"%s\",'%s','%s','%s','%s','%s','%s','%s','%s','%s')" %
    #     (
    #         '1', '2', '3', '4', '5', '6', '7', '1', '2', '3', '4', '5', '6', '7'
    #     )
    # )
    # connect_mysql.commit()
    # connect_mysql.close()
