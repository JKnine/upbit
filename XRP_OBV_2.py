import time
import pyupbit
import datetime
#import schedule
#import Prophet

import pandas as pd
import numpy as np


access = "ywpr0uZlxxwTBoQOWZBLmlximfwDg3gCxspqQYLu"
secret = "QPSrajvJBK5WFQwhTMhkhY5xEVkCEaUE0G2lHjXy"

OBV = []
OBV_MA9 = []
flag = 0
firstcheck = 0
best_ticker = "KRW-XRP"
best_tiker_name ="XRP" # get balance check 할때

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

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_ma20(ticker):
    """20일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    return ma20

def get_ma35(ticker):
    """35일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=35)
    ma35 = df['close'].rolling(35).mean().iloc[-1]
    return ma35

def get_ma100(ticker):
    """35일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=100)
    ma100 = df['close'].rolling(100).mean().iloc[-1]
    return ma100

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
buying_price = 0


# 자동매매 시작
while True:
    try:
        df = [0]
        OBV = []
        OBV_MA9 = []
        #predict_price(best_ticker)
        df = pyupbit.get_ohlcv(best_ticker, interval ="minute1", count =200) #7일 동안의 데이터를 불러오는것
     
        for i in range(1, len(df.close)):
            OBV = (df.volume * (~df.close.diff().le(0) *2 -1)).cumsum() #실제확인 했음
            OBV_MA9 = OBV.rolling(window=9).mean() #전9분의 거래량 평균
            lastnum = i
        
        #df.to_excel("obv.xlsx")
        #OBV.to_excel("obv6.xlsx")
        #OBV_MA9.to_excel("obv7.xlsx")
        #print("현재 가격: ", get_current_price(best_ticker))


        print("OVB값 :%d OBV_MA9값:%d" %(OBV[lastnum], OBV_MA9[lastnum]))
        if OBV_MA9[lastnum] > OBV[lastnum]*1.03 and flag == 1 and firstcheck == 1:
            krw = get_balance("KRW")
            print("1차 매수조건 pass")
            #print("current price: %d selling price:%d" %(pyupbit.get_current_price(best_ticker),selling_price))
            
            if selling_price == 0:
                if krw > 5000 and pyupbit.get_current_price(best_ticker) < get_ma100(best_ticker)*0.99 and firstcheck ==1:
                    upbit.buy_market_order(best_ticker, 10000) #5천원
                    flag =0
                    buying_price = pyupbit.get_current_price(best_ticker)
                    print("매수시점 가격: %f" %buying_price)
                    time.sleep(60)
                
            elif krw > 5000 and pyupbit.get_current_price(best_ticker) < selling_price *0.98 and get_ma5(best_ticker) < get_ma100(best_ticker):
                if firstcheck ==1:
                    upbit.buy_market_order(best_ticker, 10000) #5천원
                    print("만원 매수함")
                    flag =0
                    buying_price = pyupbit.get_current_price(best_ticker)
                    print("매수시점 가격: %f" %buying_price)
                    time.sleep(10)

            if krw <5000:
                print("돈이 없어 끝냄")
                break
       
        if OBV_MA9[lastnum]*1.05 < OBV[lastnum] and flag == 0:
            print("OBV %f OBV_MA9 %f"  %(OBV[lastnum] , OBV_MA9[lastnum]))
            print("현재 가격: ", get_current_price(best_ticker))
            print("매수 가격: ", buying_price)
            if get_current_price(best_ticker) > buying_price*1.05:
                current_balance = get_balance(best_tiker_name)
                print(current_balance)
                upbit.sell_market_order(best_ticker, current_balance * 0.995) #약 5천원
                #print("매도")
                flag = 1
                selling_price = pyupbit.get_current_price(best_ticker)
                #print("매도시점 가격: ", selling_price)
                time.sleep(20)
            firstcheck = 1
            print("매수전 준비완료")


        krw = get_balance("KRW")
        #print("Flag상태:%d firstcheck상태:%d 잔액:%d " %(flag, firstcheck, krw))
        #print("MA5:%d MA100:%d " %(get_ma5(best_ticker),get_ma100(best_ticker)))

        time.sleep(5)

        if krw < 5000:
            break

    except Exception as e:
        print(e)
        time.sleep(1)
