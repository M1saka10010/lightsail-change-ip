# A simple lightsail ip changer

## Notice

Running this script requires a server located in mainland China. This script is only valid when running in mainland China. It helps you protect your server from being blocked by GFW.

## How to use

1. Use git to clone this repo

    `git clone https://github.com/m1saka10010/lightsail-change-ip.git`

2. Move into the directory

    `cd lightsail-change-ip`

3. Install dependencies

    `pip install -r requirements.txt`

4. Set up the aws-cli

    `aws configure`

5. Edit the config in `aws.py`

```python
# aws.py
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
```

6. Run the script

    `python3 aws.py`
