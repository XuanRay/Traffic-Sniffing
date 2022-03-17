import win32gui          # 直接装pypiwin32 package即可
import win32con
import win32api
import win32clipboard as clipboard
import pythoncom
import time
import win32com
from PIL import Image        # Pillow is forked from PIL 1.1.7. 直接装Pillow即可
from win32com.client import Dispatch
from io import BytesIO
import random
import string
#from apscheduler.schedulers.blocking import BlockingScheduler
#from urllib import request


"""
此程序可以完成给指定的用户发送特定的文本或者图片。
但是注意：运行代码时微信不可最小化，必须关闭或者移到一旁都可以实现，最小化发送失败。
"""
class SendWechat(object):
    def __init__(self, choice, receiver_name, txt_num, pic_num, pic_path):
        self.image = ""
        self.choice = choice
        self.text_content = {}
        self.className = "WeChatMainWndForPC"
        self.receiver_Name = receiver_name
        self.txt_num = txt_num
        self.pic_num = pic_num
        self.pic_path = pic_path
    """
    setParameters():键入一些发送信息相关的信息。
    """
    def setParameters(self):
        #print("请先输入建立会话的对方的微信备注：")
        #self.receiver_Name = input()
        #print("请选择这次会话想要发送的内容形式:  0:文本；1：图片；")
        #self.choice = int(input())
        # self.choice = 2       # 2:文本+图片
        if self.choice == 2:
            # self.txt_num = 10      # 10个文本

            # 设置要发送的文字
            for i in range(self.txt_num):
                self.text_content[i] = self.generateRandomString()     # 随机60-100个字符

            # 设置要发送的图片
            img = Image.open(self.pic_path + str(self.pic_num) + '.jpg')          # 这块有需要补充的
            output = BytesIO()
            img.convert("RGB").save(output, "BMP")
            self.image = output.getvalue()[14:]
            output.close()

        elif(self.choice == 0):
            print("请先输入你想给对方发送文本的个数：")
            self.txt_num = int(input())
            for i in range(self.txt_num):
                print("请依次输入你想发送的文本消息：")
                self.text_content[i] = input()
            print(self.text_content)
        elif(self.choice ==1):
            # img = Image.open("image.jpg")
            img = Image.open(self.pic_path + str(self.pic_num) + '.jpg')
            output = BytesIO()  # BytesIO实现了在内存中读写bytes
            img.convert("RGB").save(output, "BMP") #以RGB模式保存图像
            self.image = output.getvalue()[14:]
            output.close()
            print("图片读入程序结束！")
        else:
            print("choice有误！")

    '''
    generateRandomString: 随机生成600-1000个字符
    '''
    def generateRandomString(self):
        return ''.join(random.sample(string.ascii_letters + string.digits, random.randint(30, 50)) * 20)

    """
    put_into_clipboard:# 将文本发送信息缓存入剪贴板
    """
    def put_text_clipboard(self, i):
        clipboard.OpenClipboard()
        clipboard.EmptyClipboard()
        clipboard.SetClipboardData(win32con.CF_UNICODETEXT, self.text_content[i])
        clipboard.CloseClipboard()
        return
    """
    put_image_clipboard：将图片存入剪贴板
    """
    def put_image_clipboard(self):
        clipboard.OpenClipboard()
        clipboard.EmptyClipboard()
        clipboard.SetClipboardData(win32con.CF_DIB, self.image)
        clipboard.CloseClipboard()
        return
    """
    set_name:将接收者的名字放入剪贴板
    """
    def set_name(self):
        clipboard.OpenClipboard()
        clipboard.EmptyClipboard()
        clipboard.SetClipboardData(win32con.CF_UNICODETEXT, self.receiver_Name)
        clipboard.CloseClipboard()
        return
    """
    ctrIV:模拟 Ctrl+V,将剪切板中的内容复制到发送框中
    """
    def ctrlV(self):
        win32api.keybd_event(17, 0, 0, 0)  # ctrl
        win32api.keybd_event(86, 0, 0, 0)  # V
        win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
        win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)

    """
    click:模拟点击过程
    """
    def click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    """
    movePos:移动鼠标的位置
    """
    def movePos(self, x, y):
        win32api.SetCursorPos((x, y))

    """
    enter:模拟enter
    """
    def enter(self):
        win32api.keybd_event(13, 0, 0, 0)
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)

    def get_window(self):
        win = win32gui.FindWindow(self.className, "微信")  # param1需要传入窗口的类名，param2需要传入窗口的标题
        win32gui.ShowWindow(win, win32con.SW_SHOW)
        # print("找到句柄：%x" % win)
        left, top, right, bottom = win32gui.GetWindowRect(win)
        # print(left, top, right, bottom)    # 最小化为负数
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(win)  # 获取控制
        win32gui.MoveWindow(win, 0, 0, 1000, 700, True)
        time.sleep(1)
        return

    #发送过程
    def send_wechat(self):
        self.get_window()
        # print("已经找到微信窗口！")
        # 1.移动鼠标到通讯录位置，单击打开通讯录
        self.movePos(28, 147)
        self.click()
        # 2.移动鼠标到搜索框，单击，输入要搜索的名字
        self.movePos(148, 35)
        self.click()
        self.set_name()
        self.ctrlV()
        time.sleep(1)
        self.enter()
        time.sleep(1)
        #3.复制要发送的消息，发送
        if(self.choice==2):
            # 发送文本
            for i in range(self.txt_num):
                self.put_text_clipboard(i)
                self.ctrlV()
                self.enter()
                time.sleep(1)
            # 发送图片
            self.put_image_clipboard()
            self.ctrlV()
            self.enter()
            time.sleep(5)

        if(self.choice==0):
            for i in range(self.txt_num):
                self.put_text_clipboard(i)
                self.ctrlV()
                self.enter()
                time.sleep(1)
            print("完成微信文本消息发送")
        if(self.choice==1):
            self.put_image_clipboard()
            self.ctrlV()
            self.enter()
            time.sleep(1)
            print("完成微信图片消息发送")



if __name__ == '__main__':
    # print("————该程序完成根据用户选择发送内容自动与另一个微信用户进行互动————")
    # print("该程序建立于一对一交互发送微信消息的简单场景下：")
    # print("请先输入你本次想要建立会话的个数：")
    # con_num =  int(input())
    # for i in range (con_num):
    #     wechat_sender = SendWechat()
    #     wechat_sender.setParameters()
    #     wechat_sender.send_wechat()

    times = 10
    for i in range(times):
        wechat_sender = SendWechat(2, "文件传输助手", 10, 1, 'D:/Ray/pics/')
        wechat_sender.setParameters()
        wechat_sender.send_wechat()
        time.sleep(2)



