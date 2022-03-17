#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time   : 2021/11/15 10:55
# @Author : Ray'
# @File   : Sniff.py 在网关端和本机端同时捕获Tor-Message流量


from scapy.all import *
import SSHConnection
from Send_Wechat_Auto_single import *



## ========================================================================== ##
## ------------------------ USER CONFIGURATION FLAGS ------------------------ ##
## ========================================================================== ##

### 本机设置
## 附件位置
dir_pics = "D:\\Ray\\pics\\"

## 时间设置
local_catch_traffic_time = 30   # 本机收集流量时间
shutdown_wait = 1               # 一次发送完后等待时间

## 其他设置
# 本机IP
local_IP = 'xx.xx.xx.xx'
# 本机网卡       两种方式获取。 scapy中的show_interfaces()方法；命令行中ipconfig /all
local_iface = 'Intel(R) Dual Band Wireless-AC 8260'
# 消息交互次数
times = 1


### 服务器设置
## 网关
gateway_catch_traffic_time = 30  # 网关每次抓流量时长
gateway_dict = {'host': '211.65.197.199', 'port': 2222, 'username': 'work', 'pwd': '1qaz2wsx'}
#gateway_dict = {'host':'127.0.0.1','port':9511,'username':'mason','pwd':'123456'}
gateway_path = '/media/work/6ac23a2a-da54-4b0f-904f-b0ca33560d98/tor_message'

## 代理服务器
# server_catch_traffic_time=21  # 代理服务器端抓流量时长
server_IP = '43.129.71.17'
# server_dict={'host':'170.106.161.59','port':22,'username':'root','pwd':'Meihantao123!'}
# server_path='/root/file/exp_0823'


# 本机流量收集
def catch_traffic():
    IPfilter='host ' + server_IP + ' and tcp'
    PTKS = sniff(filter=IPfilter, iface=local_iface, timeout=local_catch_traffic_time)
    pcapname = 'D:\\Ray\\pcap\\tor_message\\' + datetime.now().strftime('%Y%m%d_%H%M_%S_') + \
               'message' + '.pcap'      # %Y_%m%d_%H%M_%S
    wrpcap(pcapname, PTKS)

# 网关收集流量
def catch_traffic_gateway(gatewaySSH, no):
    gateway_cmd = 'sudo timeout ' + str(gateway_catch_traffic_time) + ' tcpdump host ' + server_IP + ' -s0 -G ' + str(gateway_catch_traffic_time) + ' -w ' + gateway_path + '/%Y_%m%d_%H%M_%S.pcap'
    gatewaySSH.cmd(gateway_cmd, sudo=True)


# 自动发送微信
def send_message(wechat_id, num):  # num表示这是自动发送的第几个循环了, pic0 -- pic2999
    wechat_sender = SendWechat(2, wechat_id, 10, num, dir_pics)
    wechat_sender.setParameters()
    wechat_sender.send_wechat()
    # 走代理发送一条大概需要20s

# 主函数
def capture():
    # 连接网关
    gatewaySSH = SSHConnection.SSHConnection(gateway_dict)
    gatewaySSH.connect()

    for i in range(times):
        print("第%d趟开始。" % i)

        # ========================= 网关开始收集流量 =========================#
        catch_traffic_gateway_thread = threading.Thread(target=catch_traffic_gateway, args=(gatewaySSH, 'no'))
        catch_traffic_gateway_thread.start()

        # ========================= 本机开始收集流量 =========================#
        catch_traffic_thread = threading.Thread(target=catch_traffic, args=())
        catch_traffic_thread.start()

        # ========================= 自动发送微信信息 =========================#
        send_message('雷斯曼', i)
        #catch_traffic_thread.join()  # 主线程等待子线程
        catch_traffic_gateway_thread.join()   #30s时间足够长，可以发送和接收完毕信息。这里，join一下能保证时间是30s

        time.sleep(shutdown_wait)

    gatewaySSH.close()


if __name__ == '__main__':
    capture()
