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
region = "ap-southeast-1" # Your region
awsName = "awsName" # Your aws name
ipName = "ipName" # Your static ip name
serverName = "serverName" # Your server name
port = 443 # Your server port
```

6. Run the script

    `python3 aws.py`
