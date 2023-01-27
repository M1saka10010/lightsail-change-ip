from tcping import Ping
import sys
import os
import time


region = "ap-southeast-1"  # Your region
awsName = "awsName"  # Your aws name
ipName = "ipName"  # Your static ip name
serverName = "serverName"  # Your server name
port = 443  # Your server port


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def check_gfw(serverName, port):
    ping = Ping(serverName, port, 1)
    with HiddenPrints():
        ping.ping(4)
    rate = Ping._success_rate(ping)
    # 根据丢包率判断是否被墙
    if rate != 0.0:
        return True
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


if __name__ == "__main__":
    while(1):
        if check_gfw(serverName, port):
            print("aws is ok")
        else:
            print("aws is not ok, changing ip...")
            try:
                ip, newIp = change_ip()
                print("ip changed from "+ip+" to "+newIp)
            except Exception as e:
                print(e+"\nchange ip failed")
        time.sleep(600)
