import time
import pyupbit
import datetime

import pandas as pd
import numpy as np


access = "ywpr0uZlxxwTBoQOWZBLmlximfwDg3gCxspqQYLu"
secret = "QPSrajvJBK5WFQwhTMhkhY5xEVkCEaUE0G2lHjXy"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15



# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
buying_price = 0

OBV = []
flag = 1

# 자동매매 시작
while True:
    try:
        df = [0]
        df = pyupbit.get_ohlcv("KRW-SAND", interval ="minute1", count =10) #7일 동안의 데이터를 불러오는것

        #OBV.append(0)
        
        for i in range(1, len(df.close)):
            OBV = (df.volume * (~df.close.diff().le(0) *2 -1)).cumsum() #실제확인 했음
            OBV_MA9 = OBV.rolling(window=9).mean() #전9분의 거래량 평균
            lastnum = i
        
        if OBV_MA9[lastnum] > OBV[lastnum] and flag == 1:
            krw = get_balance("KRW")
            if krw > 5000:
                now = datetime.datetime.now()
                print("매수시점 시간:")
                print(now)
                print("매수시점 OBV %f OBV_MA9 %f"  %(OBV[lastnum] , OBV_MA9[lastnum]))
                upbit.buy_market_order("KRW-SAND", 5000) #5천원
                print("5천원 매수함")
                flag =0
                buying_price = pyupbit.get_current_price("KRW-SAND")
                print("매수시점 가격: %f" %buying_price)
                time.sleep(60)
            else:
                print("돈이 없어 끝냄")
                break

        if OBV_MA9[lastnum] < OBV[lastnum] and flag == 0:
            print("OBV %f OBV_MA9 %f"  %(OBV[lastnum] , OBV_MA9[lastnum]))
            print(get_current_price("KRW-SAND"))
            print("buying price는 아래")
            print(buying_price)
            if get_current_price("KRW-SAND") > buying_price*1.02:
                SAND = get_balance("SAND")
                print(SAND)
                upbit.sell_market_order("KRW-SAND", SAND * 0.6) #약 5천원
                print("5천매도")
                flag = 1
                buying_price = pyupbit.get_current_price("KRW-SAND")
                print("매도시점 가격: %f" %buying_price)
                time.sleep(60)

        krw = get_balance("KRW")
        print("Flag상태 : %d 잔액 : $d" %flag, krw)
        time.sleep(1)

        if krw < 5000:
            break

    except Exception as e:
        print(e)
        time.sleep(1)
