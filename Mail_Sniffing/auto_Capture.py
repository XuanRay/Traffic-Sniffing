#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time   : 2021/11/17 15:22
# @Author : Ray'
# @File   : auto_Capture.py 同时在本机和网关端捕获Tor流量--email

# hdbnoc 密码：njnet@seu

from scapy.all import *
import datetime
import SSHConnection
import threading
import string
from SendMail_Proxy import Mail
import argparse

## ========================================================================== ##
## ------------------------ USER CONFIGURATION FLAGS ------------------------ ##
## ========================================================================== ##

## ==================  本机设置  ================== ##
## 附件位置
dir_txt_small = "D:\\Ray\\txtFiles_small\\"
dir_txt_big = "D:\\Ray\\txtFiles_big\\"
dir_save_pcap = 'D:\\Ray\\pcap\\'

## 时间设置
shutdown_wait = 10  # 一封邮件发送完后等待时间

## 其他设置
# 代理
proxy = {'host': '127.0.0.1', 'port': 9050}
# smtp服务器设置
smtpHost = 'smtp.gmail.com'

# 用户名和验证码
uname = 'leixiaoc@gmail.com'
verify_code = '1500737iloveyou'

# 发送和接受邮箱
fromWho = 'leixiaoc@gmail.com'
toWho = '<xuanlei98xiang@vip.163.com>'

# 本机网卡    --- 两种方式获取。 scapy中的show_interfaces()方法； 命令行中ipconfig /all
local_iface = 'Intel(R) Dual Band Wireless-AC 8260'


## ==================  服务器设置  ================== ##
## 网关
gateway_dict = {'host': '211.65.197.199', 'port': 2222, 'username': 'work', 'pwd': '1qaz2wsx'}
gateway_path = '/media/work/6ac23a2a-da54-4b0f-904f-b0ca33560d98/tor_email_body_bigFile'

## 代理服务器
server_IP = '43.129.71.17'


def getRandomMailBody(bodySize_min, bodySize_max):
    """
        生成[bodysize_min, bodysize_max]区间字符大小的随机字符串
    """
    body = ''.join(random.sample(string.ascii_letters + string.digits,
                                 random.randint(bodySize_min // 100, bodySize_max // 100)) * 100)
    return body


def catch_traffic(attchment_type, catch_traffic_time):
    """ 本机收集流量

    :param attchment_type: 附件类型
    :param catch_traffic_time: 捕获流量时长
    :return: none
    """
    IPfilter = 'host ' + server_IP + ' and tcp'
    PTKS = sniff(filter=IPfilter, iface=local_iface, timeout=catch_traffic_time)
    pcapname = dir_save_pcap + datetime.datetime.now().strftime('%Y%m%d_%H%M_%S_') + \
               str(attchment_type) + '.pcap'
    wrpcap(pcapname, PTKS)


def catch_traffic_gateway(gatewaySSH, catch_traffic_time):
    """ 网关收集流量

    :param gatewaySSH:  实例化的一个连接网关的对象
    :param catch_traffic_time:  捕获流量时长
    :return: none
    """
    gateway_cmd = 'sudo timeout ' + str(catch_traffic_time) + ' tcpdump host ' + server_IP + ' -s0 -G ' +\
                  str(catch_traffic_time) + ' -w ' + gateway_path + '/%Y_%m%d_%H%M_%S.pcap'
    gatewaySSH.cmd(gateway_cmd, sudo=True)



def capture_traffic(has_attachment, path, attchment_type, envelop_nums, through_proxy, catch_traffic_time):
    """ email流量捕获主函数

    :param has_attachment:  whether contains attchment
    :param path:  if has attchment, give the file path
    :param attchment_type:  the type of attchment
    :param envelop_nums:  the numbers of envelops to send
    :param through_proxy:  sending mails whether through proxy
    :param catch_traffic_time:  the time for catching traffic
    :return: none
    """
    # 连接网关
    gatewaySSH = SSHConnection.SSHConnection(gateway_dict)
    gatewaySSH.connect()

    files = []
    if has_attachment:
        files = os.listdir(path)

    for i in range(envelop_nums):

        # generate mail body
        body = getRandomMailBody(1000, 2000)

        print("Start Sniffing")

        # ========================= 本机开始收集流量 =========================#
        catch_traffic_thread = threading.Thread(target=catch_traffic, args=(attchment_type, catch_traffic_time))
        catch_traffic_thread.start()

        # ========================= 网关开始收集流量 =========================#
        catch_gateway_traffic_thread = threading.Thread(target=catch_traffic_gateway, args=(gatewaySSH, catch_traffic_time))
        catch_gateway_traffic_thread.start()

        print("Start Sending mails")

        # ========================= 开始发送邮件 =========================#
        if has_attachment:
            mailman = Mail(smtpHost, uname, verify_code, has_attachment, os.path.join(path, files[i]), through_proxy, proxy)
        else:
            mailman = Mail(smtpHost, uname, verify_code, has_attachment, '', through_proxy, proxy)
        mailman.sendMail(toWho, 'This is a mail', body, '')

        # ========================= 线程等待 =========================#
        catch_gateway_traffic_thread.join()
        catch_traffic_thread.join()
        time.sleep(shutdown_wait)      # 一封完了歇息shutdown_wait秒

    gatewaySSH.close()


def capture(attchment_code, envelop_nums, through_proxy, catch_traffic_time):
    """ 捕获函数

    :param attchment_code: 附件代码编号，0：无附件； 1：小文件； 2：大文件
    :param envelop_nums:  邮件封数
    :param through_proxy:  是否通过代理转发
    :param catch_traffic_time:  捕获时间
    :return: none
    """
    attchment_code_to_str = {0: 'only_body', 1: 'body_smallfile', 2: 'body_bigfile'}
    attchment_str = attchment_code_to_str[attchment_code]

    if attchment_code == 0:
        # only contains mail body
        capture_traffic(0, '', attchment_str, envelop_nums, through_proxy, catch_traffic_time)

    elif attchment_code == 1:
        # the type of attchment is small file
        capture_traffic(1, dir_txt_small, attchment_str, envelop_nums, through_proxy, catch_traffic_time)

    elif attchment_code == 2:
        # the type of attchment is big file
        capture_traffic(1, dir_txt_big, attchment_str, envelop_nums, through_proxy, catch_traffic_time)

    else:
        return


if __name__ == "__main__":
    """
        usage:
            python auto_Capture -h
    """
    parser = argparse.ArgumentParser(description="Automation process for sending email (can by proxy) and \
                                                  capture network traffic at different positions")
    parser.add_argument("-c", "--attchmentCode", type=int, help="附件编号", choices=[0, 1, 2], default=0)
    parser.add_argument("-n", "--envelopNum", type=int, help="邮件封数", default=1)
    parser.add_argument("-p", "--throughProxy", type=int, help="是否通过代理转发", choices=[0, 1], default=0)
    parser.add_argument("-t", "--catchTrafficTime", type=int, help="流量捕获时间", default=15)

    args = parser.parse_args()

    capture(args.attchmentCode, args.envelopNum, args.throughProxy, args.catchTrafficTime)

    print("^-^success^-^")

    #########################################################
    # 发送一篇邮件需要多少秒，可以测试一下，再决定catch_traffic_time #
    #########################################################


