#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time   : 2021/11/16 15:42
# @Author : Ray'
# @File   : SendMail.py   使用chilkat库转发邮件（使用代理），非开源


import sys
import chilkat  # refer to https://www.example-code.com/python/smtp_socks_proxy.asp


'''
    usage:
        dict = {'host': '127.0.0.1', 'port': 9050}
        smtpHost = 'smtp.qq.com' or ’smtp.163.com' etc
        uname = '2582171339@qq.com'              'xuanlei98xiang@163.com'
        verify_code = 'qbccoutgyfvtdjbi'   验证码     'FILLUAPGJISPMINT'
        has_Attachment  是否有附件  

        mailArgs 邮件的各种参数
            (fromWho, toWho, mailBody, AttachmentPath, mailSubject)
            mailSubject 这个参数sendMail中写死了
    
    return: 
        -1 : 发送错误
        -2 : Connection to SMTP server not closed cleanly.
         1 : 发送成功
'''
def sendMail(proxy: dict, smtpHost, uname, verify_code, has_Attachment, *mailArgs):  # 封装的发送邮件的函数

    # The mailman object is used for sending and receiving email.
    mailman = chilkat.CkMailMan()

    # set proxy 127.0.0.1:9050
    mailman.put_SocksHostname(proxy['host'])
    mailman.put_SocksPort(proxy['port'])
    # mailman.put_SocksUsername("myProxyLogin")
    # mailman.put_SocksPassword("myProxyPassword")

    mailman.put_SocksVersion(5)

    # Set the SMTP server.
    mailman.put_SmtpHost(smtpHost)

    # Set the SMTP login/password (if required)
    mailman.put_SmtpUsername(uname)
    mailman.put_SmtpPassword(verify_code)

    # Create a new email object
    email = chilkat.CkEmail()

    email.put_Subject("This is a mail test")
    email.put_Body(mailArgs[2])

    # add attachment
    if has_Attachment == 1:
        email.addFileAttachment(mailArgs[3])

    email.put_From(mailArgs[0])

    success = email.AddTo("xuanlei", mailArgs[1])

    # Call SendEmail to connect to the SMTP server and send.
    # The connection (i.e. session) to the SMTP server remains
    # open so that subsequent SendEmail calls may use the
    # same connection.
    success = mailman.SendEmail(email)
    if (success != True):
        print("错误，原因如下：")
        print("mailman.lastErrorText()--错误出现")
        print(mailman.lastErrorText())
        return -1

    success = mailman.CloseSmtpConnection()
    if (success != True):
        print("Connection to SMTP server not closed cleanly.")
        return -2

    print("Mail Sent! Success")
    return 1
