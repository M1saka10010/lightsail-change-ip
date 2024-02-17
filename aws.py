# -*- coding: utf-8 -*-
import os
import socket
import time
import requests

region = "ap-southeast-1"  # Your region
# Your aws name (not username, it's the name of your lightsail instance)
awsName = "awsName"
ipName = "ipName"  # Your static ip name
port = 443  # Your server port
roundTime = 600  # Check interval
notifyOn = True  # Whether to notify you when ip changed
telegramBotKey = "telegramBotKey"  # Your telegram bot key
telegramChatId = "telegramChatId"  # Your telegram chat id
# Telegram bot api(you may proxy it if you are in China)
telegramBotApi = "https://api.telegram.org"


def tcp_ping(host, port, timeout=3, attempts=3):
    """
    尝试连接指定的主机和端口多次，如果在任何尝试中连接成功，则返回True，否则返回False。

    参数:
    - host: 目标主机的IP地址或主机名
    - port: 目标端口号
    - timeout: 连接超时时间（秒）
    - attempts: 尝试连接的次数
    """
    for attempt in range(1, attempts + 1):
        try:
            print(f"Attempt {attempt} of {attempts}")
            # 创建一个socket对象
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            # 尝试连接
            start_time = time.time()
            result = sock.connect_ex((host, port))
            end_time = time.time()
            # 关闭socket
            sock.close()
            
            if result == 0:
                print(f"Connected to {host} on port {port} (time={end_time - start_time:.2f}s)")
                return True
            else:
                print(f"Failed to connect to {host} on port {port}")
        except socket.error as e:
            print(f"Socket error: {e}")
        time.sleep(1)  # 等待1秒再次尝试
    return False



# 用aws静态ip名称获取ip
def get_ip(ipName):
    try:
        sh = os.popen("aws lightsail --region "+region +
                    " get-static-ip --static-ip-name "+ipName)
        ip = sh.read().split("ipAddress")[1].split('"')[2]
        return ip
    except Exception as e:
        print(e)
        return False


def os_cmd(cmd):
    sh = os.popen(cmd)
    return sh.read()


def change_ip():
    # 获取原ip
    sh = os_cmd("aws lightsail --region "+region +
                " get-static-ip --static-ip-name "+ipName)
    ip = sh.split("ipAddress")[1].split('"')[2]
    # 解绑ip
    sh = os_cmd("aws lightsail --region "+region +
                " detach-static-ip --static-ip-name "+ipName)
    # 释放ip
    sh = os_cmd("aws lightsail --region "+region +
                " release-static-ip --static-ip-name "+ipName)
    # 重新分配ip
    sh = os_cmd("aws lightsail --region "+region +
                " allocate-static-ip --static-ip-name "+ipName)
    # 重新绑定ip
    sh = os_cmd("aws lightsail --region "+region +
                " attach-static-ip --static-ip-name "+ipName+" --instance-name "+awsName)
    # 获取新ip
    sh = os_cmd("aws lightsail --region "+region +
                " get-static-ip --static-ip-name "+ipName)
    newIp = sh.split("ipAddress")[1].split('"')[2]
    return ip, newIp


def get(url):
    try:
        r = requests.get(url, timeout=2)
        return r.text
    except Exception as e:
        return e


def notify_ip_changed(ip, newIp):
    if notifyOn:
        res = get(telegramBotApi+"/bot"+telegramBotKey+"/sendMessage?chat_id="+telegramChatId +
                  "&text=ip changed from "+ip+" to "+newIp)
        return res


def notify_ip_changed_failed(err):
    if notifyOn:
        res = get(telegramBotApi+"/bot"+telegramBotKey+"/sendMessage?chat_id="+telegramChatId +
                  "&text=ip changed failed\n"+err)
        return res


if __name__ == "__main__":
    while (1):
        ip = get_ip(ipName)
        if not ip:
            print("get ip failed")
            time.sleep(roundTime)
            continue
        if tcp_ping(ip, port):
            print("aws is ok")
        else:
            print("aws is not ok, changing ip...")
            try:
                ip, newIp = change_ip()
                print("ip changed from "+ip+" to "+newIp)
                notify_ip_changed(ip, newIp)
            except Exception as e:
                print(str(e)+"\nchange ip failed")
                notify_ip_changed_failed()
        time.sleep(roundTime)
