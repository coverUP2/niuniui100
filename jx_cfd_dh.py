"""
cron: 50 59 * * * *
new Env('财富岛兑换红包');
"""
import os
import re
import time
import json
import datetime
import requests
from ql_util import get_random_str
from ql_api import get_envs, disable_env, post_envs, put_envs

# 默认配置(看不懂代码也勿动)
cfd_start_time = -0.15
cfd_offset_time = 0.01

# 基础配置勿动
cfd_url = "%68%74%74%70%73://%6d%2e%6a%69%6e%67%78%69%2e%63%6f%6d/%6a%78%62%66%64/%75%73%65%72/%45%78%63%68%61%6e%67%65%50%72%69%7a%65?%73%74%72%5a%6f%6e%65=%6a%78%62%66%64&%62%69%7a%43%6f%64%65=%6a%78%62%66%64&%73%6f%75%72%63%65=%6a%78%62%66%64&%64%77%45%6e%76=%37&%5f%63%66%64%5f%74=%31%36%34%37%38%35%30%31%38%32%31%37%30&%70%74%61%67=%37%31%35%35%2e%39%2e%34%37&%64%77%54%79%70%65=%33&%64%77%4c%76%6c=%37&%64%64%77%50%61%70%65%72%4d%6f%6e%65%79=%31%30%30%30%30%30&%73%74%72%50%6f%6f%6c%4e%61%6d%65=%6a%78%63%66%64%32%5f%65%78%63%68%61%6e%67%65%5f%68%62%5f%32%30%32%32%30%33&%73%74%72%50%67%74%69%6d%65%73%74%61%6d%70=%31%36%34%37%38%35%30%31%38%32%31%35%31&%73%74%72%50%68%6f%6e%65%49%44=%66%39%63%36%30%35%65%65%65%63%37%30%38%36%35%37&%73%74%72%50%67%55%55%4e%75%6d=%34%34%33%35%33%32%30%36%31%66%61%30%61%62%62%31%63%37%38%63%65%64%37%36%62%31%34%31%35%66%30%66&%5f%73%74%6b=%5f%63%66%64%5f%74%25%32%43%62%69%7a%43%6f%64%65%25%32%43%64%64%77%50%61%70%65%72%4d%6f%6e%65%79%25%32%43%64%77%45%6e%76%25%32%43%64%77%4c%76%6c%25%32%43%64%77%54%79%70%65%25%32%43%70%74%61%67%25%32%43%73%6f%75%72%63%65%25%32%43%73%74%72%50%67%55%55%4e%75%6d%25%32%43%73%74%72%50%67%74%69%6d%65%73%74%61%6d%70%25%32%43%73%74%72%50%68%6f%6e%65%49%44%25%32%43%73%74%72%50%6f%6f%6c%4e%61%6d%65%25%32%43%73%74%72%5a%6f%6e%65&%5f%73%74%65=%31&%68%35%73%74=%32%30%32%32%30%33%32%31%31%36%30%39%34%32%31%37%30%25%33%42%37%37%34%30%34%35%39%33%31%37%35%30%36%32%34%36%25%33%42%39%32%61%33%36%25%33%42%74%6b%30%32%77%61%38%38%30%31%63%33%62%31%38%6e%6e%4d%57%31%46%71%73%36%72%78%50%33%56%6c%68%4f%4d%59%4f%6f%4f%69%42%6c%25%32%46%46%32%58%53%57%54%7a%73%75%59%62%79%32%33%43%54%51%31%5a%42%35%55%51%52%31%79%4e%75%6f%65%6b%39%49%50%69%6f%74%39%48%64%53%55%42%6f%5a%78%42%61%62%6d%32%25%33%42%31%61%38%35%64%63%37%35%63%30%38%32%32%35%66%30%62%38%36%61%63%36%39%66%32%30%35%38%63%35%34%32%65%65%36%39%37%31%39%38%31%62%37%31%30%31%30%61%38%38%37%30%62%66%32%33%37%65%64%39%66%66%32%38%25%33%42%33%2e%30%25%33%42%31%36%34%37%38%35%30%31%38%32%31%37%30&%5f=%31%36%34%37%38%35%30%31%38%32%31%37%31&%73%63%65%6e%65%76%61%6c=%32&%67%5f%6c%6f%67%69%6e%5f%74%79%70%65=%31&%63%61%6c%6c%62%61%63%6b=%6a%73%6f%6e%70%43%42%4b%4c&%67%5f%74%79=%6c%73"

pattern_pin = re.compile(r'pt_pin=([\w\W]*?);')
pattern_data = re.compile(r'\(([\w\W]*?)\)')


# 获取下个整点和时间戳
def get_date() -> str and int:
    # 当前时间
    now_time = datetime.datetime.now()
    # 把根据当前时间计算下一个整点时间戳
    integer_time = (now_time + datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:00:00")
    time_array = time.strptime(integer_time, "%Y-%m-%d %H:%M:%S")
    time_stamp = int(time.mktime(time_array))
    return integer_time, time_stamp


# 获取要执行兑换的cookie
def get_cookie():
    ck_list = []
    pin = "null"
    cookie = None
    cookies = get_envs("CFD_COOKIE")
    for ck in cookies:
        if ck.get('status') == 0:
            ck_list.append(ck)
    if len(ck_list) >= 1:
        cookie = ck_list[0]
        re_list = pattern_pin.search(cookie.get('value'))
        if re_list is not None:
            pin = re_list.group(1)
        print('共配置{}条CK,已载入用户[{}]'.format(len(ck_list), pin))
    else:
        print('共配置{}条CK,请添加环境变量,或查看环境变量状态'.format(len(ck_list)))
    return pin, cookie


# 获取配置参数
def get_config():
    start_dist = {}
    start_times = get_envs("CFD_START_TIME")
    if len(start_times) >= 1:
        start_dist = start_times[0]
        start_time = float(start_dist.get('value'))
        print('从环境变量中载入时间变量[{}]'.format(start_time))
    else:
        start_time = cfd_start_time
        u_data = post_envs('CFD_START_TIME', str(start_time), '财富岛兑换时间配置,自动生成,勿动')
        if len(u_data) == 1:
            start_dist = u_data[0]
        print('从默认配置中载入时间变量[{}]'.format(start_time))
    return start_time, start_dist


# 抢购红包请求函数
def cfd_qq(def_start_time):
    # 进行时间等待,然后发送请求
    end_time = time.time()
    while end_time < def_start_time:
        end_time = time.time()
    # 记录请求时间,发送请求
    t1 = time.time()
    d1 = datetime.datetime.now().strftime("%H:%M:%S.%f")
    res = requests.get(cfd_url, headers=headers)
    t2 = time.time()
    # 正则对结果进行提取
    re_list = pattern_data.search(res.text)
    # 进行json转换
    data = json.loads(re_list.group(1))
    msg = data['sErrMsg']
    # 根据返回值判断
    if data['iRet'] == 0:
        # 抢到了
        msg = "可能抢到了"
        put_envs(u_cookie.get('_id'), u_cookie.get('name'), u_cookie.get('value'), msg)
        disable_env(u_cookie.get('_id'))
    elif data['iRet'] == 2016:
        # 需要减
        start_time = float(u_start_time) - float(cfd_offset_time)
        put_envs(u_start_dist.get('_id'), u_start_dist.get('name'), str(start_time)[:8])
    elif data['iRet'] == 2013:
        # 需要加
        start_time = float(u_start_time) + float(cfd_offset_time)
        put_envs(u_start_dist.get('_id'), u_start_dist.get('name'), str(start_time)[:8])
    elif data['iRet'] == 1014:
        # URL过期
        pass
    elif data['iRet'] == 2007:
        # 财富值不够
        put_envs(u_cookie.get('_id'), u_cookie.get('name'), u_cookie.get('value'), msg)
        disable_env(u_cookie.get('_id'))
    elif data['iRet'] == 9999:
        # 账号过期
        put_envs(u_cookie.get('_id'), u_cookie.get('name'), u_cookie.get('value'), msg)
        disable_env(u_cookie.get('_id'))
    print("实际发送[{}]\n耗时[{:.3f}]\n用户[{}]\n结果[{}]".format(d1, (t2 - t1), u_pin, msg))
 

if __name__ == '__main__':
    print("- 程序初始化")
    print("脚本进入时间[{}]".format(datetime.datetime.now().strftime("%H:%M:%S.%f")))
    # 从环境变量获取url,不存在则从配置获取
    u_url = os.getenv("CFD_URL", cfd_url)
    # 获取cookie等参数
    u_pin, u_cookie = get_cookie()
    # 获取时间等参数
    u_start_time, u_start_dist = get_config()
    # 预计下个整点为
    u_integer_time, u_time_stamp = get_date()
    print("抢购整点[{}]".format(u_integer_time))
    print("- 初始化结束\n")

    print("- 主逻辑程序进入")
    UA = "jdpingou;android;5.21.0;appBuild/20535;session/379;pap/JA2019_3111789;ef/1;ep/%7B%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22ts%22%3A1647615567752%2C%22ridx%22%3A-1%2C%22cipher%22%3A%7B%22bd%22%3A%22%22%2C%22ad%22%3A%22ZtvtDtK1ZWVvYzcmENY1Dm%3D%3D%22%2C%22sv%22%3A%22CJS%3D%22%2C%22od%22%3A%22CzvwCJK2ZQY1ENdvEWDsZK%3D%3D%22%2C%22ud%22%3A%22ZtvtDtK1ZWVvYzcmENY1Dm%3D%3D%22%7D%2C%22ciphertype%22%3A5%2C%22version%22%3A%221.2.0%22%2C%22appname%22%3A%22com.jd.pingou%22%7D;Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.74 Mobile Safari/537.36".format(
        get_random_str(45, True))
    if u_cookie is None:
        print("未读取到CFD_COOKIE,程序结束")
    else:
        headers = {
            "Host": "m.jingxi.com",
            "Accept": "*/*",
            "Connection": "keep-alive",
            'Cookie': u_cookie['value'],
            "User-Agent": UA,
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            "Referer": "https://st.jingxi.com/",
            "Accept-Encoding": "gzip, deflate, br"
        }
        u_start_sleep = float(u_time_stamp) + float(u_start_time)
        print("预计发送时间为[{}]".format(datetime.datetime.fromtimestamp(u_start_sleep).strftime("%H:%M:%S.%f")))
        if u_start_sleep - time.time() > 300:
            print("离整点时间大于5分钟,强制立即执行")
            cfd_qq(0)
        else:
            cfd_qq(u_start_sleep)
    print("- 主逻辑程序结束")
