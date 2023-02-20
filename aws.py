import os
import sys
import time
import requests

from tcping import Ping

region = "ap-southeast-1"  # Your region
awsName = "awsName"  # Your aws name
ipName = "ipName"  # Your static ip name
port = 443  # Your server port
roundTime = 600  # Check interval
notifyOn = True  # Whether to notify you when ip changed
telegramBotKey = "telegramBotKey"  # Your telegram bot key
telegramChatId = "telegramChatId"  # Your telegram chat id
# Telegram bot api(you may proxy it if you are in China)
telegramBotApi = "https://api.telegram.org"


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def check_gfw(serverIp, port):
    ping = Ping(serverIp, port, 1)
    with HiddenPrints():
        ping.ping(4)
    rate = Ping._success_rate(ping)
    # 根据丢包率判断是否被墙
    if rate != 0.0:
        return True
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
        if check_gfw(ip, port):
            print("aws is ok")
        else:
            print("aws is not ok, changing ip...")
            try:
                ip, newIp = change_ip()
                print("ip changed from "+ip+" to "+newIp)
                notify_ip_changed(ip, newIp)
            except Exception as e:
                print(e+"\nchange ip failed")
                notify_ip_changed_failed()
        time.sleep(roundTime)
