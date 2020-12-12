#!/usr/bin/python
# -*- coding: UTF-8 -*-

# pip install requests

import re
import os
import os.path
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header


# resolve ip from they servers, try one by one
resolve_ip_servers = ['http://icanhazip.com/',
                      'http://www.trackip.net/ip', 'http://ifconfig.me/ip']

# save last ip file name
last_ip_file_name = '__last_ip.txt'

class Monitor:
    def __init__(self):
        self.mail_host = "smtp.163.com"
        self.mail_user = "xxx@163.com"
        self.mail_pass = "xxx"
        self.mail_port = 465
        self.sender = "xxx@163.com"
        self.receivers = ["xxx@163.com", "xxx@qq.com"]

    def resolve_ip(self):
        """
        get public ip
        """

        ip = None
        for ip_server in resolve_ip_servers:
            try:
                r = requests.get(ip_server, timeout=5)
                if r.status_code == 200 and r.text != None and re.match('^\d+.\d+.\d+.\d+$',  r.text.strip()):
                    ip = r.text.strip()
                    print("from ip_server: %s get ip: %s " % (ip_server, ip))
                    break
                else:
                    print("from ip_server: %s get ip error")
            except Exception as err:
                print("from ip_server: %s get ip error:%s",
                      (ip_server, str(err)))
        return ip


    def is_ip_changed(self, ip):
        """
        check last ip is same
        """

        file = os.path.join(os.getcwd(), last_ip_file_name)

        last_ip = None
        if os.path.isfile(file):
            f = open(file, mode='r')
            print("history_file: %s" % (str(f.name)))
            last_ip = f.read()
            f.close()

        print("last ip: %s" % (str(last_ip)))

        if not last_ip or last_ip != ip:
            f = open(file, mode='w')
            f.write(ip)
            f.close()
            return True, last_ip
        else:
            return False, ip


    def send_email(self, ip):
        """
        send email
        """

        mail_msg = """
        <p>Public IP: {}</p>
        """
        message = MIMEText(mail_msg.format(ip), 'html', 'utf-8')
        message['From'] = Header(self.sender)
        message['To'] = Header(','.join(self.receivers))

        subject = 'Your New Public IP: {}'.format(ip)
        message['Subject'] = Header(subject, 'utf-8')

        try:
            smtpObj = smtplib.SMTP_SSL(self.mail_host, self.mail_port)
            smtpObj.login(self.mail_user, self.mail_pass)

            smtpObj.sendmail(self.sender, ','.join(
                self.receivers), message.as_string())

            print("email send sucessed!")
        except smtplib.SMTPException as err:
            print("Error: can't email send:%s", (str(err)))
 

# linux or mac run : monitor.sh
# Windows run : monitor.bat
if __name__ == '__main__':
    monitor = Monitor()
    ip = monitor.resolve_ip()
    print("resolved ip: %s" % (ip))
    result, last_ip = monitor.is_ip_changed(ip)
    if result:
        print("ip changed: %s, last ip:%s" % (ip, last_ip))
        monitor.send_email(ip)
    else:
        print("last ip is same as: %s, cancel send email." % (ip))
