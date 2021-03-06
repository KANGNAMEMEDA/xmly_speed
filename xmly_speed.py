import requests
import json
import rsa
import base64
import time
from itertools import groupby
from functools import reduce
from random import choice
import hashlib
from datetime import datetime
from dateutil import tz
import os

# 喜马拉雅极速版
# 使用参考 xmly_speed.md
# cookies填写

cookies1 = '' # 字符串形式 都可以识别


cookiesList = [cookies1, ]  # 多账号准备


UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 iting/1.0.12 kdtunion_iting/1.0 iting(main)/1.0.12/ios_1"
# 非iOS设备的需要的自行修改,自己抓包 与cookie形式类似


def str2dict(str_cookie):
    if type(str_cookie) == dict:
        return str_cookie
    tmp = str_cookie.split(";")
    dict_cookie = {}
    for i in tmp:
        j = i.split("=")
        if not j[0]:
            continue
        dict_cookie[j[0].strip()] = j[1].strip()
    return dict_cookie


if "XMLY_SPEED_COOKIE" in os.environ:
    """
    判断是否运行自GitHub action,"XMLY_SPEED_COOKIE" 该参数与 repo里的Secrets的名称保持一致
    """
    print("执行自GitHub action")
    xmly_speed_cookie = os.environ["XMLY_SPEED_COOKIE"]
    cookiesList = []  # 重置cookiesList
    for line in xmly_speed_cookie.split('\n'):
        if not line:
            continue
        cookiesList.append(line)

if not cookiesList[0]:
    print("cookie为空 跳出X")
    exit()
mins = int(time.time())
date_stamp = (mins-57600) % 86400
print(datetime.now(tz=tz.gettz('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S", ))
_datatime = datetime.now(tz=tz.gettz('Asia/Shanghai')).strftime("%Y%m%d", )
print(_datatime)
print("今日已过秒数: ", date_stamp)
print("当前时间戳", mins)


def ans_receive(cookies, paperId, lastTopicId, receiveType):
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
    }
    _checkData = f"""lastTopicId={lastTopicId}&numOfAnswers=3&receiveType={receiveType}"""
    checkData = rsa_encrypt(str(_checkData), pubkey_str)
    data = {
        "paperId": paperId,
        "checkData": checkData,
        "lastTopicId": lastTopicId,
        "numOfAnswers": 3,
        "receiveType": receiveType
    }
    response = requests.post('https://m.ximalaya.com/speed/web-earn/topic/receive',
                             headers=headers, cookies=cookies, data=json.dumps(data))
    print(response.text)


def ans_restore(cookies):
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
    }
    checkData = rsa_encrypt("restoreType=2", pubkey_str)

    data = {
        "restoreType": 2,
        "checkData": checkData,
    }
    response = requests.post('https://m.ximalaya.com/speed/web-earn/topic/restore',
                             headers=headers, cookies=cookies, data=json.dumps(data))
    print(response.text)


def ans_getTimes(cookies):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    response = requests.get(
        'https://m.ximalaya.com/speed/web-earn/topic/user', headers=headers, cookies=cookies)
    result = json.loads(response.text)
    stamina = result["data"]["stamina"]  
    remainingTimes = result["data"]["remainingTimes"] 
    return {"stamina": stamina,
            "remainingTimes": remainingTimes}


def ans_start(cookies):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/quiz',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    response = requests.get(
        'https://m.ximalaya.com/speed/web-earn/topic/start', headers=headers, cookies=cookies)
    result = json.loads(response.text)
    paperId = result["data"]["paperId"]
    dateStr = result["data"]["dateStr"]
    lastTopicId = result["data"]["topics"][2]["topicId"]
    print(paperId, dateStr, lastTopicId)
    return paperId, dateStr, lastTopicId


def _str2key(s):
    b_str = base64.b64decode(s)
    if len(b_str) < 162:
        return False
    hex_str = ''
    for x in b_str:
        h = hex(x)[2:]
        h = h.rjust(2, '0')
        hex_str += h
    m_start = 29 * 2
    e_start = 159 * 2
    m_len = 128 * 2
    e_len = 3 * 2
    modulus = hex_str[m_start:m_start + m_len]
    exponent = hex_str[e_start:e_start + e_len]
    return modulus, exponent


def rsa_encrypt(s, pubkey_str):
    key = _str2key(pubkey_str)
    modulus = int(key[0], 16)
    exponent = int(key[1], 16)
    pubkey = rsa.PublicKey(modulus, exponent)
    return base64.b64encode(rsa.encrypt(s.encode(), pubkey)).decode()


pubkey_str = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCVhaR3Or7suUlwHUl2Ly36uVmboZ3+HhovogDjLgRE9CbaUokS2eqGaVFfbxAUxFThNDuXq/fBD+SdUgppmcZrIw4HMMP4AtE2qJJQH/KxPWmbXH7Lv+9CisNtPYOlvWJ/GHRqf9x3TBKjjeJ2CjuVxlPBDX63+Ecil2JR9klVawIDAQAB"


def lottery_info(cookies):
    print("\n【幸运大转盘】")
    """
    转盘信息查询
    """
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-ad-sweepstake-h5/home',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    response = requests.get(
        'https://m.ximalaya.com/speed/web-earn/inspire/lottery/info', headers=headers, cookies=cookies)
    result = json.loads(response.text)
    remainingTimes = result["data"]["remainingTimes"]
    print(f'转盘剩余次数: {remainingTimes}\n')
    if result["data"]["chanceId"] != 0 and result["data"]["remainingTimes"] == 1:
        print("免费抽奖次数")
        return
    if result["data"]["remainingTimes"] in [0, 1]:
        return
    data = {
        "sign": rsa_encrypt(str(result["data"]["chanceId"]), pubkey_str),
    }
    response = requests.post('https://m.ximalaya.com/speed/web-earn/inspire/lottery/action',
                             headers=headers, cookies=cookies, data=json.dumps(data))
    print(response.text)
    if remainingTimes > 0:
        headers = {
            'Host': 'm.ximalaya.com',
            'Accept': 'application/json, text/plain, */*',
            'Connection': 'keep-alive',
            'User-Agent': UserAgent,
            'Accept-Language': 'zh-cn',
            'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-ad-sweepstake-h5/home',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        response = requests.get(
            'https://m.ximalaya.com/speed/web-earn/inspire/lottery/token', headers=headers, cookies=cookies)
        print("token", response.text)
        result = json.loads(response.text)
        _id = result["data"]["id"]
        data = {
            "token": _id,
            "sign": rsa_encrypt(f"token={_id}&userId={uid}", pubkey_str),
        }
        headers = {
            'User-Agent': UserAgent,
            'Content-Type': 'application/json;charset=utf-8',
            'Host': 'm.ximalaya.com',
            'Origin': 'https://m.ximalaya.com',
            'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-ad-sweepstake-h5/home',
        }
        response = requests.post('https://m.ximalaya.com/speed/web-earn/inspire/lottery/chance',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        result = json.loads(response.text)
        print("chance", result)
        data = {
            "sign": rsa_encrypt(str(result["data"]["chanceId"]), pubkey_str),
        }
        response = requests.post('https://m.ximalaya.com/speed/web-earn/inspire/lottery/action',
                                 headers=headers, cookies=cookies, data=json.dumps(data))
        print("action", response.text)

def index_baoxiang_award(cookies):
    print("\n  【首页、宝箱奖励及翻倍】")
    headers = {
        'User-Agent': UserAgent,
        'Host': 'mobile.ximalaya.com',
    }
    uid = cookies["1&_token"].split("&")[0]
    currentTimeMillis = int(time.time()*1000)-2
    response = requests.post('https://mobile.ximalaya.com/pizza-category/activity/getAward?activtyId=baoxiangAward',
                             headers=headers, cookies=cookies)
    
    result = response.json()
    print("宝箱奖励: ", result)
    if "ret" in result and result["ret"] == 0:
        awardReceiveId = result["awardReceiveId"]
        headers = {
            'Host': 'mobile.ximalaya.com',
            'Accept': '*/*',
            'User-Agent': UserAgent,
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        params = (
            ('activtyId', 'baoxiangAward'),
            ('awardReceiveId', awardReceiveId),
        )

        response = requests.get('http://mobile.ximalaya.com/pizza-category/activity/awardMultiple',
                                headers=headers, params=params, cookies=cookies)
        print("翻倍 ",response.text)
    ###################################
    params = (
        ('activtyId', 'indexSegAward'),
        ('ballKey', str(uid)),
        ('currentTimeMillis', str(currentTimeMillis)),
        ('sawVideoSignature', f'{currentTimeMillis}+{uid}'),
        ('version', '2'),
    )
    response = requests.get('https://mobile.ximalaya.com/pizza-category/activity/getAward',
                            headers=headers, cookies=cookies, params=params)
    result = response.json()
    print("首页奖励: ",result)
    if "ret" in result and result["ret"] == 0:
        awardReceiveId = result["awardReceiveId"]
        headers = {
            'Host': 'mobile.ximalaya.com',
            'Accept': '*/*',
            'User-Agent': UserAgent,
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        params = (
            ('activtyId', 'indexSegAward'),
            ('awardReceiveId', awardReceiveId),
        )

        response = requests.get('http://mobile.ximalaya.com/pizza-category/activity/awardMultiple',
                                headers=headers, params=params, cookies=cookies)
        print("翻倍: ",response.text)

def checkin(cookies):
    print("\n【连续签到】")
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/growth-ssr-speed-welfare-center/page/welfare',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    params = (
        ('time', f"""{int(time.time()*1000)}"""),
    )
    response = requests.get('https://m.ximalaya.com/speed/task-center/check-in/record',
                            headers=headers, params=params, cookies=cookies)
    result = json.loads(response.text)
    print(result)
    print(f"""连续签到{result["continuousDays"]}/{result["historyDays"]}天""")
    print(result["isTickedToday"])
    if result["isTickedToday"] == False:
        print("!!!未签到")
        pass


def ad_score(cookies, businessType, taskId):

    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain ,*/*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Content-Type': 'application/json;charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    response = requests.get(
        'https://m.ximalaya.com/speed/task-center/ad/token', headers=headers, cookies=cookies)
    result = response.json()
    token = result["id"]
    data = {
        "taskId": taskId,
        "businessType": businessType,
        "rsaSign": rsa_encrypt(f"""businessType={businessType}&token={token}&uid={uid}""", pubkey_str),
    }
    response = requests.post(f'https://m.ximalaya.com/speed/task-center/ad/score',
                             headers=headers, cookies=cookies, data=json.dumps(data))
    print(response.text)
    print("\n")


def bubble(cookies):
    print("\n【bubble】")
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-open-components/bubble',
    }

    data = {"listenTime": "41246", "signature": "2b1cc9ee020db596d28831cff8874d9c",
            "currentTimeMillis": "1596695606145", "uid": uid, "expire": False}

    response = requests.post('https://m.ximalaya.com/speed/web-earn/listen/bubbles',
                             headers=headers, cookies=cookies, data=json.dumps(data))
    result = response.json()
    if not result["data"]["effectiveBubbles"]:
        print("暂无有效气泡")
        return
    for i in result["data"]["effectiveBubbles"]:
        print(i["id"])
        receive(cookies, i["id"])
        time.sleep(1)
        ad_score(cookies, 7, i["id"])
    for i in result["data"]["expiredBubbles"]:
        ad_score(cookies, 6, i["id"])


def receive(cookies, taskId):
    headers = {
        'Host': 'm.ximalaya.com',
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'User-Agent': UserAgent,
        'Accept-Language': 'zh-cn',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-open-components/bubble',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    response = requests.get(
        f'https://m.ximalaya.com/speed/web-earn/listen/receive/{taskId}', headers=headers, cookies=cookies)
    print("receive: ", response.text)




def getOmnipotentCard(cookies):
    print("\n 【领取万能卡】")
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
    }
    count = requests.get('https://m.ximalaya.com/speed/web-earn/card/omnipotentCardInfo',
                         headers=headers, cookies=cookies,).json()["data"]["count"]
    if count == 5:
        print("今日已满")
        return
    
    token = requests.get('https://m.ximalaya.com/speed/web-earn/card/token/1',
                         headers=headers, cookies=cookies,).json()["data"]["id"]
    data = {
        "listenTime": mins-date_stamp,
        "signData": rsa_encrypt(f"{_datatime}{token}{uid}", pubkey_str),
        "token": token
    }

    response = requests.post('https://m.ximalaya.com/speed/web-earn/card/getOmnipotentCard',
                             headers=headers, cookies=cookies, data=json.dumps(data))
    print(response.text)


def cardReportTime(cookies):
    print("\n【收听获得抽卡机会】")
    headers = {
        'User-Agent': UserAgent,
        'Content-Type': 'application/json;charset=utf-8',
        'Host': 'm.ximalaya.com',
        'Origin': 'https://m.ximalaya.com',
        'Referer': 'https://m.ximalaya.com/xmds-node-spa/apps/speed-growth-activities/card-collection/home',
    }
    listenTime = mins-date_stamp
    data = {"listenTime": listenTime,
            "signData": rsa_encrypt(f"{_datatime}{listenTime}{uid}", pubkey_str), }
    response = requests.post('https://m.ximalaya.com/speed/web-earn/card/reportTime',
                             headers=headers, cookies=cookies, data=json.dumps(data)).json()
    if response["data"]["upperLimit"]:
        print("今日已达上限")


def account(cookies):
    print("\n【 打印账号信息】")
    headers = {
        'Host': 'm.ximalaya.com',
        'Content-Type': 'application/json;charset=utf-8',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': UserAgent,
        'Referer': 'https://m.ximalaya.com/speed/web-earn/wallet',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    response = requests.get(
        'https://m.ximalaya.com/speed/web-earn/account/coin', headers=headers, cookies=cookies)
    result = response.json()
    print(f"""
当前剩余:{result["total"]/10000}
今日获得:{result["todayTotal"]/10000}
累计获得:{result["historyTotal"]/10000}
""")


def answer(cookies):
    print("\n【答题】")
    ans_times = ans_getTimes(cookies)
    if ans_times["stamina"]==0:
        print("时间未到")
    for _ in range(ans_times["stamina"]):
        paperId, _, lastTopicId = ans_start(cookies)
        ans_receive(cookies, paperId, lastTopicId, 1)
        time.sleep(1)
        ans_receive(cookies, paperId, lastTopicId, 2)
        time.sleep(1)

    if ans_times["remainingTimes"] > 0:
        print("[看视频回复体力]")
        ans_restore(cookies)
        for _ in range(5):
            paperId, _, lastTopicId = ans_start(cookies)
            ans_receive(cookies, paperId, lastTopicId, 1)
            time.sleep(1)
            ans_receive(cookies, paperId, lastTopicId, 2)
            time.sleep(1)


##################################################################


for i in cookiesList:
    print(">>>>>>>>>【账号开始】")
    cookies = str2dict(i)
    uid = cookies["1&_token"].split("&")[0]
    uuid = cookies["XUM"]
    bubble(cookies)  # 收金币气泡
    checkin(cookies) #自动签到
    lottery_info(cookies) #大转盘4次
    answer(cookies)      # 答题赚金币
    cardReportTime(cookies)
    getOmnipotentCard(cookies) # 领取万能卡
    index_baoxiang_award(cookies) #首页、宝箱奖励及翻倍
    account(cookies)
