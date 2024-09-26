# -*- coding: utf-8 -*-
import importlib
import sys
import os
import urllib
import requests
import base64
import json
from datetime import datetime
import time
import pandas as pd
import numpy as np
import random
import hmac

# 824cd36ad5735dca8b9736e6dac82e07cd56bf1f0b90f3973a700cdb34d68583
# bg_c1a48e67154f2b46248f26bfcf3e8b8f
# MMClianghua130
# =========在此设置api-key,下单金额===========
# 默认设置BTC订单,不要修改
# 设置api-key,注意试用期只有3个月有效期
api_key = 'JnpWaymbVKZs'
API_URL = 'https://api.bitget.com'
API_SECRET_KEY = '91fe12942f61dee99e8b345c37c288b7e84ad89baab72fa79933f1a6509d0d6a'
API_KEY = 'bg_ad11f53fafe5c53fe72db05cb4d22e02'
PASSPHRASE = 'HBLww130130130'
btc_order_value = 400
btc_up_per = 1.015
symbol_list = ['ETHUSDT']
symbol_1 = 'ETHUSDT'
symbol_2 = 'ETH'
zhekou = 0.9989

# ================================================================================================================================================
# 第二个log日志打印接口,每隔60s打印一次
def get_timestamp():
    return int(time.time() * 1000)
def sign(message, secret_key):
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)
def pre_hash(timestamp, method, request_path, body):
    return str(timestamp) + str.upper(method) + request_path + body
def parse_params_to_str(params):
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'
    return url[0:-1]
def get_header(api_key, sign, timestamp, passphrase):
    header = dict()
    header['Content-Type'] = 'application/json'
    header['ACCESS-KEY'] = api_key
    header['ACCESS-SIGN'] = sign
    header['ACCESS-TIMESTAMP'] = str(timestamp)
    header['ACCESS-PASSPHRASE'] = passphrase
    # header[LOCALE] = 'zh-CN'
    return header

def truncate(number, decimals):
    factor = 10.0 ** decimals
    return int(number * factor) / factor

def write_txt(content):
    with open("/root/pendle_ordi/pendle.txt", "a") as file:
        print(content, file=file)
    return None

def get_price(symbol):
    w2 = 0
    g2 = 0 
    while w2 == 0:
        try:
            timestamp = get_timestamp()
            response = None
            request_path = "/api/v2/spot/market/tickers"
            url = API_URL + request_path
            params = {"symbol":symbol}
            request_path = request_path + parse_params_to_str(params)
            url = API_URL + request_path
            body = ""
            sign_cang = sign(pre_hash(timestamp, "GET", request_path, str(body)), API_SECRET_KEY)
            header = get_header(API_KEY, sign_cang, timestamp, PASSPHRASE)
            response = requests.get(url, headers=header)
            ticker = json.loads(response.text)
            price_d = float(ticker['data'][0]['lastPr'])
            if price_d > 0:
                w2 = 1
            else:
                w2 = 0
            g2 += 1

        except:
            time.sleep(1)
            g2 += 1
            continue
    return price_d


def open_long(symbol,order_usdt):
    logo_b = 0
    while logo_b == 0:
        try:
            timestamp = get_timestamp()
            response = None
            clientoid = "bitget%s"%(str(int(datetime.now().timestamp())))
            request_path = "/api/v2/spot/trade/place-order"
            url = API_URL + request_path
            params = {"symbol":symbol,"side":"buy","size":str(order_usdt),"force":"gtc","orderType":"market","clientOid":clientoid}
            body = json.dumps(params)
            sign_tranfer = sign(pre_hash(timestamp, "POST", request_path, str(body)), API_SECRET_KEY)
            header = get_header(API_KEY, sign_tranfer, timestamp, PASSPHRASE)
            response = requests.post(url, data=body, headers=header)
            #Log(str(response))
            buy_res_base = json.loads(response.text)
            content = '开多====' + str(buy_res_base['data'])
            write_txt(content)
            buy_id_base = int(buy_res_base['data']['orderId'])
            if buy_id_base  > 10:
                logo_b = 1
            else:
                logo_b = 0
        except:
            time.sleep(0.2)
            continue
    return buy_id_base

def close_order(symbol,order_num,volumePlace):
    logo_b = 0
    while logo_b == 0:
        try:
            timestamp = get_timestamp()
            response = None
            clientoid = "bitget%s"%(str(int(datetime.now().timestamp())))
            request_path = "/api/v2/spot/trade/place-order"
            url = API_URL + request_path
            params = {"symbol":symbol,"side":"sell","size":str(truncate(order_num,volumePlace)),"force":"gtc","orderType":"market","clientOid":clientoid}
            body = json.dumps(params)
            sign_tranfer = sign(pre_hash(timestamp, "POST", request_path, str(body)), API_SECRET_KEY)
            header = get_header(API_KEY, sign_tranfer, timestamp, PASSPHRASE)
            response = requests.post(url, data=body, headers=header)
            #Log(str(response))
            sell_res_base = json.loads(response.text)
            content = '平多====' + str(sell_res_base['data'])
            write_txt(content)
            sell_id_base = int(sell_res_base['data']['orderId'])
            if int(sell_id_base)  > 10:
                logo_b = 1
            else:
                logo_b = 0
        except:
            time.sleep(0.2)
            continue
    return sell_id_base

# 查看订单信息
def check_op(id_num):
    logo_s = 0
    while logo_s == 0:
        try:
            timestamp = get_timestamp()
            response = None
            request_path_spot = "/api/v2/spot/trade/orderInfo"
            params_spot = {"orderId":str(id_num)}
            request_path_spot = request_path_spot + parse_params_to_str(params_spot)
            url = API_URL + request_path_spot
            body = ""
            sign_spot = sign(pre_hash(timestamp, "GET", request_path_spot,str(body)), API_SECRET_KEY)
            header_spot = get_header(API_KEY, sign_spot, timestamp, PASSPHRASE)
            response_spot = requests.get(url, headers=header_spot)
            response_1 = json.loads(response_spot.text)
            # base_num状态
            base_price = float(response_1['data'][0]['priceAvg'])             
            base_num = float(response_1['data'][0]['baseVolume'])
            if base_price >0 and base_num > 0:
                logo_s = 1
            else:
                logo_s = 0
        except:
            time.sleep(0.2)
            continue
    return base_price,base_num

def get_num(symbol):
    w2 = 0 
    while w2 == 0:
        try:
            timestamp = get_timestamp()
            response = None
            request_path = "/api/v2/spot/public/symbols"
            url = API_URL + request_path
            params = {"symbol":symbol}
            request_path = request_path + parse_params_to_str(params)
            url = API_URL + request_path
            body = ""
            sign_cang = sign(pre_hash(timestamp, "GET", request_path, str(body)), API_SECRET_KEY)
            header = get_header(API_KEY, sign_cang, timestamp, PASSPHRASE)
            response = requests.get(url, headers=header)
            ticker = json.loads(response.text)
            crypto_num = int(ticker['data'][0]['quantityPrecision'])
            if crypto_num > 0:
                w2 = 1
            else:
                w2 = 0
        except:
            time.sleep(0.2)
            continue
    return crypto_num

def crypto_num(coin):
    logo_b = 0
    while logo_b == 0:
        try:
            timestamp = get_timestamp()
            response = None
            request_path = "/api/v2/spot/account/assets"
            url = API_URL + request_path
            params = {"coin":coin}
            request_path = request_path + parse_params_to_str(params)
            url = API_URL + request_path
            body = ""
            sign_cang = sign(pre_hash(timestamp, "GET", request_path, str(body)), API_SECRET_KEY)
            header = get_header(API_KEY, sign_cang, timestamp, PASSPHRASE)
            response = requests.get(url, headers=header)
            num_res_base = json.loads(response.text)
            num_res_base = float(num_res_base['data'][0]['available'])
            if num_res_base  > 0:
                logo_b = 1
            else:
                logo_b = 0

        except:
            time.sleep(0.2)
            continue
    return num_res_base





# 获取币种的价格小数位,开仓量小数位
btc_volumePlace = get_num(symbol=symbol_list[0])
content = 'btc数量和价格精度：'+str(btc_volumePlace)
write_txt(content)

raw_data_btc = pd.DataFrame({'crypto_id':'ceshi','crypto_start_time':1,'crypto_time':pd.to_datetime('2023-01-01 12:30:30'),'base_price':1,'base_num':1,'up_one_price':1,'up_one_num':1, \
            'down_one_price':1,'down_one_num':1,'down_two_price':1,'down_two_num':1,'down_three_price':1,'down_three_num':1,'down_four_price':1,'down_four_num':1, \
            'down_five_price':1,'down_five_num':1,'down_six_price':1,'down_six_num':1,'down_seven_price':1,'down_seven_num':1,'down_eight_price':1,'down_eight_num':1,'down_nine_price':1,'down_nine_num':1,\
            'finish':1},index=[0])

js = 0
while True:
    time.sleep(0.5)
    # 没有订单的重新下单,有订单的监控起状态
    date = str(datetime.utcnow())[0:10]
    # 需要的是未完成订单
    symbol = symbol_1
    raw_data_btc = raw_data_btc[raw_data_btc.finish==0]
    if len(raw_data_btc) == 0:
        btc_price = get_price(symbol)
        content = '没有任何btc一网  ---- 下初始单'
        write_txt(content)
        #开仓
        buy_id_base = open_long(symbol,btc_order_value)
        content = '买入base的btc'
        write_txt(content)
        #查看订单信息
        base_price,base_num = check_op(buy_id_base)
        base_num = base_num*zhekou 
        #其它仓位信息
        up_one_price = base_price * btc_up_per
        up_one_num = 0
        down_one_price = base_price * (1-(btc_up_per-1))
        down_one_num = 0
        down_two_price = base_price * (1-2*(btc_up_per-1))
        down_two_num = 0
        down_three_price = base_price * (1-3*(btc_up_per-1))
        down_three_num = 0
        down_four_price = base_price * (1-4*(btc_up_per-1))
        down_four_num = 0
        down_five_price = base_price * (1-5*(btc_up_per-1))
        down_five_num = 0
        down_six_price = base_price * (1-6*(btc_up_per-1))
        down_six_num = 0
        down_seven_price = base_price * (1-7*(btc_up_per-1))
        down_seven_num = 0
        down_eight_price = base_price * (1-8*(btc_up_per-1))
        down_eight_num = 0
        down_nine_price = base_price * (1-9*(btc_up_per-1))
        down_nine_num = 0
        finish = 0
        timestamp = int(time.time() * 1000)
        crypto_id = 'A' + str(timestamp)
        crypto_time = str(datetime.utcnow())[0:19]
        df = pd.DataFrame({'crypto_id':crypto_id,'crypto_start_time':timestamp,'crypto_time':pd.to_datetime(crypto_time),'base_price':base_price,'base_num':base_num,'up_one_price':up_one_price,'up_one_num':up_one_num, \
        'down_one_price':down_one_price,'down_one_num':down_one_num,'down_two_price':down_two_price,'down_two_num':down_two_num,'down_three_price':down_three_price,'down_three_num':down_three_num,'down_four_price':down_four_price,'down_four_num':down_four_num, \
        'down_five_price':down_five_price,'down_five_num':down_five_num,'down_six_price':down_six_price,'down_six_num':down_six_num,'down_seven_price':down_seven_price,'down_seven_num':down_seven_num,'down_eight_price':down_eight_price,'down_eight_num':down_eight_num,'down_nine_price':down_nine_price,'down_nine_num':down_nine_num,\
        'finish':finish},index=[0])
        raw_data_btc = pd.concat([raw_data_btc,df])
        content = '初始化btc,网格总数：'+str(len(raw_data_btc))
        write_txt(content)
    else:
        if js%30==0:
            content = '对既有的btc网格进行监控'
            write_txt(content)
    # 订单监控
    max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
    raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
    sub_raw_data_btc = raw_data_btc[raw_data_btc.finish==0]
    sub_raw_data_btc = sub_raw_data_btc.sort_values(by='crypto_start_time',ascending=False)
    sub_raw_data_btc = sub_raw_data_btc.reset_index(drop=True)
    if js%30==0:
        content = '初始化btc,网格总数：'+str(len(sub_raw_data_btc))
        write_txt(content)
    btc_base_price = sub_raw_data_btc['base_price'][0]
    btc_base_num = sub_raw_data_btc['base_num'][0]
    btc_up_one_price = sub_raw_data_btc['up_one_price'][0]
    btc_up_one_num = sub_raw_data_btc['up_one_num'][0]
    btc_down_one_price = sub_raw_data_btc['down_one_price'][0]
    btc_down_one_num = sub_raw_data_btc['down_one_num'][0]
    btc_down_two_price = sub_raw_data_btc['down_two_price'][0]
    btc_down_two_num = sub_raw_data_btc['down_two_num'][0]
    btc_down_three_price = sub_raw_data_btc['down_three_price'][0]
    btc_down_three_num = sub_raw_data_btc['down_three_num'][0]
    btc_down_four_price = sub_raw_data_btc['down_four_price'][0]
    btc_down_four_num = sub_raw_data_btc['down_four_num'][0]
    btc_down_five_price = sub_raw_data_btc['down_five_price'][0]
    btc_down_five_num = sub_raw_data_btc['down_five_num'][0]
    btc_down_six_price = sub_raw_data_btc['down_six_price'][0]
    btc_down_six_num = sub_raw_data_btc['down_six_num'][0]
    btc_down_seven_price = sub_raw_data_btc['down_seven_price'][0]
    btc_down_seven_num = sub_raw_data_btc['down_seven_num'][0]
    btc_down_eight_price = sub_raw_data_btc['down_eight_price'][0]
    btc_down_eight_num = sub_raw_data_btc['down_eight_num'][0]
    btc_down_nine_price = sub_raw_data_btc['down_nine_price'][0]
    btc_down_nine_num = sub_raw_data_btc['down_nine_num'][0]
    btc_finish = sub_raw_data_btc['finish'][0]
    btc_crypto_id = sub_raw_data_btc['crypto_id'][0]
    btc_crypto_start_time = sub_raw_data_btc['crypto_start_time'][0]
    btc_crypto_time = str(datetime.utcnow())[0:19]
    btc_price = get_price(symbol)
    if js%30==0:
        content_1 = 'btc各网格价格'+str('--')+str(btc_up_one_price)+str('--')+str(btc_base_price)+str('--')+str(btc_down_one_price)+str('--')+str(btc_down_two_price)+str('--')+str(btc_down_three_price)+str('--')+str(btc_down_four_price)+str('--')+str(btc_down_five_price)+str('--')+str(btc_down_six_price)\
                +str('--')+str(btc_down_seven_price)+str('--')+str(btc_down_eight_price)+str('--')+str(btc_down_nine_price)
        content_2 = 'btc各网格数量'+str('--')+str(btc_base_num)+str('--')+str(btc_down_one_num)+str('--')+str(btc_down_two_num)+str('--')+str(btc_down_three_num)+str('--')+str(btc_down_four_num)+str('--')+str(btc_down_five_num)+str('--')+str(btc_down_six_num)\
                +str('--')+str(btc_down_seven_num)+str('--')+str(btc_down_eight_num)+str('--')+str(btc_down_nine_num)
        content_3 = 'btc当前价格'+str(btc_price)
        write_txt(content_1)
        write_txt(content_2)
        write_txt(content_3)
    
    if btc_base_num > 0 and btc_down_one_num==0 and btc_down_two_num==0 and btc_down_three_num==0 and btc_down_four_num==0 and btc_down_five_num==0 and btc_down_six_num==0 and btc_down_seven_num==0 and btc_down_eight_num==0 and btc_down_nine_num==0:
        if btc_price >= btc_up_one_price:
            # 卖出初始化格
            sell_base_id = close_order(symbol,btc_base_num,btc_volumePlace)
            content = '卖出base的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_one_price and btc_price > btc_down_two_price:
            #买入第1格
            buy_id_down_one = open_long(symbol,btc_order_value)
            content = '买入第1格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_one_price,btc_down_one_num = check_op(buy_id_down_one)
            btc_down_one_num = btc_down_one_num*zhekou
            btc_down_two_price = btc_down_one_price * (1-(btc_up_per-1))
            btc_down_three_price = btc_down_one_price * (1-2*(btc_up_per-1))
            btc_down_four_price = btc_down_one_price * (1-3*(btc_up_per-1))
            btc_down_five_price = btc_down_one_price * (1-4*(btc_up_per-1))
            btc_down_six_price = btc_down_one_price * (1-5*(btc_up_per-1))
            btc_down_seven_price = btc_down_one_price * (1-6*(btc_up_per-1))
            btc_down_eight_price = btc_down_one_price * (1-7*(btc_up_per-1))
            btc_down_nine_price = btc_down_one_price * (1-8*(btc_up_per-1))
            # down_one_num状态
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_up_one_price and btc_price > btc_down_one_price:
            if js%30==0:
                content = 'btc监控平仓初始化格,或者在第1格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)

    # 在base,up_one,down_one处有三网
    elif btc_base_num > 0 and btc_down_one_num>0 and btc_down_two_num==0 and btc_down_three_num==0 and btc_down_four_num==0 and btc_down_five_num==0 and btc_down_six_num==0 and btc_down_seven_num==0 and btc_down_eight_num==0 and btc_down_nine_num==0:
        if btc_price >= btc_base_price and btc_price < btc_up_one_price:
            # 卖出第1格
            sell_one_id = close_order(symbol,btc_down_one_num,btc_volumePlace)
            content = '卖出第1格的btc'
            write_txt(content)
            #down_one_num状态
            btc_down_one_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_two_price and btc_price > btc_down_three_price:
            #买入第2格
            buy_id_down_two = open_long(symbol,btc_order_value)
            content = '买入第2格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_two_price,btc_down_two_num = check_op(buy_id_down_two)
            btc_down_two_num = btc_down_two_num*zhekou
            btc_down_three_price = btc_down_two_price * (1-(btc_up_per-1))
            btc_down_four_price = btc_down_two_price * (1-2*(btc_up_per-1))
            btc_down_five_price = btc_down_two_price * (1-3*(btc_up_per-1))
            btc_down_six_price = btc_down_two_price * (1-4*(btc_up_per-1))
            btc_down_seven_price = btc_down_two_price * (1-5*(btc_up_per-1))
            btc_down_eight_price = btc_down_two_price * (1-6*(btc_up_per-1))
            btc_down_nine_price = btc_down_two_price * (1-7*(btc_up_per-1))
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_base_price and btc_price > btc_down_two_price:
            if js%30==0:
                content = 'btc监控平仓第1格,或者在第2格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two处有四网
    elif btc_base_num > 0  and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num==0 and btc_down_four_num==0 and btc_down_five_num==0 and btc_down_six_num==0 and btc_down_seven_num==0 and btc_down_eight_num==0 and btc_down_nine_num==0:
        if btc_price >= btc_down_one_price and btc_price < btc_base_price:
            # 卖出第2格
            sell_two_id = close_order(symbol,btc_down_two_num,btc_volumePlace)
            content = '卖出第2格的btc'
            write_txt(content)
            btc_down_two_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_three_price and btc_price > btc_down_four_price:
            #买入第3格
            buy_id_down_three = open_long(symbol,btc_order_value)
            content = '买入第3格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_three_price,btc_down_three_num = check_op(buy_id_down_three)
            btc_down_three_num = btc_down_three_num*zhekou
            btc_down_four_price = btc_down_three_price * (1-(btc_up_per-1))
            btc_down_five_price = btc_down_three_price * (1-2*(btc_up_per-1))
            btc_down_six_price = btc_down_three_price * (1-3*(btc_up_per-1))
            btc_down_seven_price = btc_down_three_price * (1-4*(btc_up_per-1))
            btc_down_eight_price = btc_down_three_price * (1-5*(btc_up_per-1))
            btc_down_nine_price = btc_down_three_price * (1-6*(btc_up_per-1))

            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_one_price and btc_price > btc_down_three_price:
            if js%30==0:
                content = 'btc监控平仓第2格,或者在第3格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two,down_three处有五网
    elif btc_base_num > 0  and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num>0 and btc_down_four_num==0 and btc_down_five_num==0 and btc_down_six_num==0 and btc_down_seven_num==0 and btc_down_eight_num==0 and btc_down_nine_num==0:
        if btc_price >= btc_down_two_price and btc_price < btc_down_one_price:
            # 卖出低3格
            sell_three_id = close_order(symbol,btc_down_three_num,btc_volumePlace)
            content = '卖出第3格的btc'
            write_txt(content)
            # down_three_num 状态
            btc_down_three_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_four_price and btc_price > btc_down_five_price:
            #买入第4格
            buy_id_down_four = open_long(symbol,btc_order_value)
            content = '买入第4格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_four_price,btc_down_four_num = check_op(buy_id_down_four)
            btc_down_four_num = btc_down_four_num*zhekou
            btc_down_five_price = btc_down_four_price * (1-(btc_up_per-1))
            btc_down_six_price = btc_down_four_price * (1-2*(btc_up_per-1))
            btc_down_seven_price = btc_down_four_price * (1-3*(btc_up_per-1))
            btc_down_eight_price = btc_down_four_price * (1-4*(btc_up_per-1))
            btc_down_nine_price = btc_down_four_price * (1-5*(btc_up_per-1))
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_two_price and btc_price > btc_down_four_price:
            if js%30==0:
                content = 'btc监控平仓第3格,或者在第4格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two,down_three,down_four处有六网
    elif btc_base_num > 0  and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num>0 and btc_down_four_num>0 and btc_down_five_num==0 and btc_down_six_num==0 and btc_down_seven_num==0 and btc_down_eight_num==0 and btc_down_nine_num==0:
        if btc_price >= btc_down_three_price and btc_price < btc_down_two_price:
            # 卖出第4格
            sell_four_id = close_order(symbol,btc_down_four_num,btc_volumePlace)
            content = '卖出第4格的btc'
            write_txt(content)
            btc_down_four_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_five_price and btc_price > btc_down_six_price:
            #买入第5格
            buy_id_down_five = open_long(symbol,btc_order_value)
            content = '买入第5格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_five_price,btc_down_five_num = check_op(buy_id_down_five)
            btc_down_five_num = btc_down_five_num*zhekou
            btc_down_six_price = btc_down_five_price * (1-1*(btc_up_per-1))
            btc_down_seven_price = btc_down_five_price * (1-2*(btc_up_per-1))
            btc_down_eight_price = btc_down_five_price * (1-3*(btc_up_per-1))
            btc_down_nine_price = btc_down_five_price * (1-4*(btc_up_per-1))
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_three_price and btc_price > btc_down_five_price:
            if js%30==0:
                content = 'btc监控平仓第4格,或者在第5格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two,down_three,down_four,down_five处有七网
    elif btc_base_num > 0  and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num>0 and btc_down_four_num>0 and btc_down_five_num>0 and btc_down_six_num==0 and btc_down_seven_num==0 and btc_down_eight_num==0 and btc_down_nine_num==0:
        if btc_price >= btc_down_four_price and btc_price < btc_down_three_price:
            # 卖出第5格
            sell_five_id = close_order(symbol,btc_down_five_num,btc_volumePlace)
            content = '卖出第5格的btc'
            write_txt(content)
            btc_down_five_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_six_price and btc_price > btc_down_seven_price:
            #买入第6格
            buy_id_down_six = open_long(symbol,btc_order_value)
            content = '买入第6格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_six_price,btc_down_six_num = check_op(buy_id_down_six)
            btc_down_six_num = btc_down_six_num*zhekou
            btc_down_seven_price = btc_down_six_price * (1-1*(btc_up_per-1))
            btc_down_eight_price = btc_down_six_price * (1-2*(btc_up_per-1))
            btc_down_nine_price = btc_down_six_price * (1-3*(btc_up_per-1))
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_four_price and btc_price > btc_down_six_price:
            if js%30==0:
                content = 'btc监控平仓第5格,或者在第6格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two,down_three,down_four,down_five处有七网
    elif btc_base_num> 0  and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num>0 and btc_down_four_num>0 and btc_down_five_num>0 and btc_down_six_num>0 and btc_down_seven_num==0 and btc_down_eight_num==0 and btc_down_nine_num==0 :
        if btc_price >= btc_down_five_price and btc_price < btc_down_four_price:
            # 卖出第6格
            sell_six_id = close_order(symbol,btc_down_six_num,btc_volumePlace)
            content = '卖出第6格的btc'
            write_txt(content)
            btc_down_six_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish,'finish_time':pd.to_datetime('2023-01-01 12:30:30')},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_seven_price and btc_price > btc_down_eight_price:
            #d买入第7格
            buy_id_down_seven = open_long(symbol,btc_order_value)
            content = '买入第7格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_seven_price,btc_down_seven_num = check_op(buy_id_down_seven)
            btc_down_seven_num = btc_down_seven_num*zhekou
            btc_down_eight_price = btc_down_seven_price * (1-1*(btc_up_per-1))
            btc_down_nine_price = btc_down_seven_price * (1-2*(btc_up_per-1))
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_five_price and btc_price > btc_down_seven_price:
            if js%30==0:
                content = 'btc监控平仓第6格,或者在第7格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two,down_three,down_four,down_five处有七网
    elif btc_base_num > 0  and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num>0 and btc_down_four_num>0 and btc_down_five_num>0 and btc_down_six_num>0 and btc_down_seven_num>0 and btc_down_eight_num==0 and btc_down_nine_num==0 :
        if btc_price >= btc_down_six_price and btc_price < btc_down_five_price:
            # 卖出第7格
            sell_seven_id = close_order(symbol,btc_down_seven_num,btc_volumePlace)
            content = '卖出第7格的btc'
            write_txt(content)
            btc_down_seven_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_eight_price and btc_price > btc_down_nine_price:
            #买入第8格
            buy_id_down_eight = open_long(symbol,btc_order_value)
            content = '买入第8格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_eight_price,btc_down_eight_num = check_op(buy_id_down_eight)
            btc_down_eight_num = btc_down_eight_num*zhekou
            btc_down_nine_price = btc_down_eight_price * (1-1*(btc_up_per-1))
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_six_price and btc_price > btc_down_eight_price:
            if js%30==0:
                content = 'btc监控平仓第7格,或者在第8格下单'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two,down_three,down_four,down_five处有七网
    elif  btc_base_num > 0   and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num>0 and btc_down_four_num>0 and btc_down_five_num>0 and btc_down_six_num>0 and btc_down_seven_num>0 and btc_down_eight_num>0 and btc_down_nine_num==0:
        if btc_price >= btc_down_seven_price and btc_price < btc_down_six_price:
            # 卖出第8格
            sell_eight_id = close_order(symbol,btc_down_eight_num,btc_volumePlace)
            content = '卖出第8格的btc'
            write_txt(content)
            btc_down_eight_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price <= btc_down_nine_price:
            #买入第9格
            buy_id_down_nine = open_long(symbol,btc_order_value)
            content = '买入第9格的btc'
            write_txt(content)
            # 查看订单状态
            btc_down_nine_price,btc_down_nine_num = check_op(buy_id_down_nine)
            btc_down_nine_num = btc_down_nine_num*zhekou
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_seven_price and btc_price > btc_down_nine_price:
            if js%30==0:
                content = 'btc监控平仓第8格,或者在第9格下单'
                write_txt(content)
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    # 在base,up_one,down_one,down_two,down_three,down_four,down_five处有七网
    elif btc_base_num > 0  and btc_down_one_num>0 and btc_down_two_num>0 and btc_down_three_num>0 and btc_down_four_num>0 and btc_down_five_num>0 and btc_down_six_num>0 and btc_down_seven_num>0 and btc_down_eight_num>0 and btc_down_nine_num>0:
        if btc_price >= btc_down_eight_price and btc_price < btc_down_seven_price:
            # 卖出第9格
            sell_nine_id = close_order(symbol,btc_down_nine_num,btc_volumePlace)
            content = '卖出第9格的btc'
            write_txt(content)
            btc_down_nine_num = 0
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
        elif btc_price < btc_down_eight_price:
            if js%30==0:
                content = '目前btc满仓状态,监控平仓9格子'
                write_txt(content)
            else:
                crypto = 0
        else:
            content = 'btc价格异常报警'
            write_txt(content)
            all_num = crypto_num(symbol_2)*0.99
            sell_all_id = close_order(symbol,all_num,btc_volumePlace)
            content = '卖出所有的btc'
            write_txt(content)
            # base_num状态
            btc_base_num = 0
            btc_finish = 1
            df = pd.DataFrame({'crypto_id':btc_crypto_id,'crypto_start_time':btc_crypto_start_time,'crypto_time':pd.to_datetime(btc_crypto_time),'base_price':btc_base_price,'base_num':btc_base_num,'up_one_price':btc_up_one_price,'up_one_num':btc_up_one_num,\
            'down_one_price':btc_down_one_price,'down_one_num':btc_down_one_num,'down_two_price':btc_down_two_price,'down_two_num':btc_down_two_num,'down_three_price':btc_down_three_price,'down_three_num':btc_down_three_num,'down_four_price':btc_down_four_price,'down_four_num':btc_down_four_num,\
            'down_five_price':btc_down_five_price,'down_five_num':btc_down_five_num,'down_six_price':btc_down_six_price,'down_six_num':btc_down_six_num,'down_seven_price':btc_down_seven_price,'down_seven_num':btc_down_seven_num,'down_eight_price':btc_down_eight_price,'down_eight_num':btc_down_eight_num,'down_nine_price':btc_down_nine_price,'down_nine_num':btc_down_nine_num,\
            'finish':btc_finish},index=[0])
            raw_data_btc = pd.concat([raw_data_btc,df])
            max_select_btc = raw_data_btc.groupby(['crypto_id'],as_index=False)['crypto_time'].max()
            raw_data_btc = raw_data_btc.merge(max_select_btc,how='inner',on=['crypto_id','crypto_time'])
            raw_data_btc = raw_data_btc.sort_values(by='crypto_time')
            raw_data_btc = raw_data_btc.reset_index(drop=True)
    else:
        if js%1000==0:
            content = 'btc程序异常'
            write_txt(content)
    js += 1