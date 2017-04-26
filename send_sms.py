#!/Users/simon/.venv/test/bin/python
# -*- encoding: utf-8 -*-
import os
import time
import json
import random
import string
import requests
import hashlib
try:
    from urllib import urlencode, quote
except ImportError:
    from urllib.parse import urlencode, quote

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

SMS_APPKEY = ""
SMS_APPSECRET = ""
SMS_TEMPLATEID = ""
SMS_SENDTEMPLATE_URL = "https://api.netease.im/sms/sendtemplate.action"

IMESSAGE_PHONE_NUMBER = ""
IMESSAGE_CMD_TMPL = "/opt/bin/send_imessage.sh {} '{}'"

LOCATION = ("", "")


def gen_nonce(n_length=16):
    return ''.join([(string.ascii_letters + string.digits)[x] for x in random.sample(range(0,62), n_length)])


def get_weather_info(longitude, latitude):
    url = "https://api.caiyunapp.com/v2/TAkhjf8d1nlSlspN/{},{}/forecast.json".format(
        longitude,
        latitude
    )
    weather_info = None
    while not weather_info:
        res = requests.get(url)
        res_json = res.json()
        if res.status_code == 200 and res_json["status"] == "ok":
            weather_info = res_json["result"]["hourly"]["description"]
        else:
            print("request failed.")
            time.sleep(2)

    return weather_info


def send_sms(url, message):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "charset": "utf-8"
    }
    app_secret = SMS_APPSECRET
    nonce = gen_nonce()
    curtime = str(int(time.time()))
    s = "{}{}{}".format(app_secret, nonce, curtime).encode(encoding="utf-8")
    checksum = hashlib.sha1(s).hexdigest()

    payload = 'templateid={}&mobiles=["{}"]&params=["{}"]'.format(SMS_TEMPLATEID, "13162391986", message)
    headers.update({
        "AppKey": SMS_APPKEY,
        "Nonce": nonce,
        "CurTime": curtime,
        "CheckSum": checksum
    })

    res = requests.post(url, headers=headers, data=payload)
    return res.json()


def send_imessage(phone_number, message):
    cmd = IMESSAGE_CMD_TMPL.format(phone_number, message)
    return os.system(cmd)

if __name__ == '__main__':
    weather_info = get_weather_info(*LOCATION)

    # res = send_sms(SMS_SENDTEMPLATE_URL, weather_info)
    for number in IMESSAGE_PHONE_NUMBER.split(","):
        result = send_imessage(number.strip(), weather_info)
        if result == 0:
            print("消息已发送, {}, {}".format(number, weather_info))
        else:
            print("消息发送失败")
