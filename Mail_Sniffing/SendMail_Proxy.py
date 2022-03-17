#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time   : 2021/11/17 15:22
# @Author : Ray'
# @File   : SendMail_Proxy.py  自动发送邮件的类


import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from os.path import basename
import ssl

import socks     # python3 不是自带的， 通过pip install PySocks即可


class Mail:
    """
    邮件发送工具类
    """
    def __init__(self, mail_host, mail_user, mail_pass, has_attchment, attach_path, need_proxy=0, mail_proxy=None):
        """
        初始化邮箱设置
        :param mail_host: string 邮箱服务器地址
        :param mail_user: string 发件人
        :param mail_pass: string 验证码
        :param has_attchment: int 是否包含附件
        :param attach_path: string     附件文件名称
        :param need_proxy: int
        :param mail_proxy: dict  代理服务器ip和端口
        """
        try:
            if need_proxy:
                print('使用代理发送....')
                self.mail_proxy = mail_proxy
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, self.mail_proxy['host'], self.mail_proxy['port'])
                socks.wrapmodule(smtplib)
            self.me = '<' + mail_user + '>'
            self.has_attchment = has_attchment
            self.attach_path = attach_path
            self.server = smtplib.SMTP_SSL(mail_host, 465, context=ssl.create_default_context())
            self.server.login(mail_user, mail_pass)
        except Exception as e:
            print(e)

    def sendMail(self, to_list, sub, body, images):
        """
        邮件发送
        :param to_list: list 收件人列表
        :param sub:  string 主题
        :param body:  string 正文
        :param images:  dict 图片
        :return:  None
        """
        # def add_img(src, img_id):
        #     """
        #     邮件正文添加图片
        #     :param src: string 图片路径
        #     :param img_id: string 图片id
        #     :return: MIMEImage
        #     """
        #     try:
        #         fp = open(src, 'rb')
        #         msg_image = MIMEImage(fp.read())
        #         fp.close()
        #         msg_image.add_header('Content-ID', img_id)
        #         return msg_image
        #     except Exception as ex:
        #         log('ERROR', '[Mail->__call__->add_img] --> errmsg:%s' % (str(ex)))

        msg = MIMEMultipart()
        msg_text = MIMEText(body, 'html', 'utf-8')
        msg.attach(msg_text)
        if self.has_attchment:
            print("添加附件")
            attchment = MIMEApplication(open(self.attach_path, 'rb').read())
            # 标示位置为附件，设置附件的文件名
            attchment.add_header("Content-Disposition", "attachment", filename=basename(self.attach_path))
            msg.attach(attchment)

        # if images:
        #     for k, v in images.iteritems():
        #         msg.attach(add_img(k, v))

        msg['Subject'] = sub
        msg['From'] = self.me
        msg['To'] = to_list
        try:
            print('开始发送邮件....')
            self.server.sendmail(self.me, to_list, msg.as_string())
            print('邮件发送成功....')
        except Exception as e:
            print(e)

    def __del__(self):
        self.server.close()