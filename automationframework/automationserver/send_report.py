import smtplib
import json
from urllib.parse import quote
from urllib.request import urlopen  # quote,urlopen发送短信的接口使用
from email.mime.text import MIMEText
from email.header import Header


class SendReport(object):
    # 发邮件提醒
    def sender_email(self, runtime, case_amount, pass_case_count, not_run_case):
        # 发送邮件配置
        to_email = "allenyao224@qq.com,1653838404@qq.com"  # 收件人
        cc_email = "268455431@qq.com"  # 抄送人

        sendmail_configure = {
            'mail_host': 'smtp.163.com',  # 设置服务器
            'mail_user': "allencredit@163.com",  # 用户名
            'mail_pass': 'xiaoxi5332',  # 邮箱密码
        }
        sender = 'allencredit@163.com'
        if to_email == "" or "@" not in to_email:
            toemail = "allenyao@qq.com"
        if cc_email == "" or "@" not in cc_email:
            ccemail = ""
        receivers = to_email.split(',') + cc_email.split(',')  # 收件人+抄送人
        message = MIMEText(
            "Dear all: \n           测试用例全部执行完毕，执行用例时间为：%s，共执行%s个用例，通过%s个用例，未执行%s个用例" % (runtime, case_amount, pass_case_count,not_run_case),
            'plain',
            'utf-8')
        message['From'] = Header("automationauthor", 'utf-8')  # 收件人
        message['To'] = Header(to_email)  # 收件人的地址栏显示
        message['Cc'] = cc_email
        subject = '自动化测试用例结果'  # 邮件标题
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = smtplib.SMTP()
            # 163 默认端口25 也为 SMTP 端口号 465/994
            smtpObj.connect(sendmail_configure.get('mail_host'), 25)
            smtpObj.login(sendmail_configure.get(
                'mail_user'), sendmail_configure.get('mail_pass'))  # 邮箱的登录
            smtpObj.sendmail(sender, receivers, message.as_string())
            return True
        except smtplib.SMTPException:
            return False

    # 发短信提醒 短信的文案还未修改完善
    def send_message(self):
        appkey = "12fa16d0a55a8ef4925ac22825487343"
        mobile = "17721292302"
        tpl_id = "52062"
        tpl_value = '#code#=%s&#company#=JuheData' % ("ssss")
        sendurl = 'http://v.juhe.cn/sms/send'  # 短信发送的URL,无需修改

        params = 'key=%s&mobile=%s&tpl_id=%s&tpl_value=%s' % \
                 (appkey, mobile, tpl_id, quote(tpl_value))  # 组合参数

        wp = urlopen(sendurl + "?" + params)
        content = wp.read()  # 获取接口返回内容

        result = json.loads(content)

        if result:
            error_code = result['error_code']
            if error_code == 0:
                # 发送成功
                smsid = result['result']['sid']
                return ("sendsms success,smsid: %s" % (smsid))
            else:
                # 发送失败
                return ("sendsms error :(%s) %s" % (error_code, result['reason']))
        else:
            # 请求失败
            return ("request sendsms error")


if __name__ == "__main__":
    SendReport().sender_email("2018年7月2日 22:40:66", "10", '20');  # 邮箱提醒
    # SendReport().sendmessage();#手机短信提醒
    # print(sendmessage())
