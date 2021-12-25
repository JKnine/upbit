import time
import pyupbit
import datetime

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

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") #Defalut가 9시로 세팅되어 있음
        end_time = start_time + datetime.timedelta(days=1) #9:00시 +1일

        if start_time < now < end_time - datetime.timedelta(seconds=10): #8시59분 50초까지
            target_price = get_target_price("KRW-BTC", 0.5) #0.5는 K값
            current_price = get_current_price("KRW-BTC")
            
            ##JK test
            #btc = get_balance("BTC")
            #print(btc)    
            #upbit.sell_market_order("KRW-BTC", btc*0.3)
            #print(btc)    
            #time.sleep(100)
            #JK 테스트 끝

            if target_price < current_price:  ## and ma15 < current_price: #이동평균선보다 이상일때
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995) #수수료 감안
                    ##post_message(myToken,"#crypto", "BTC buy : " +str(buy_result))  ##slack message
        else:
            btc = get_balance("BTC")
            if btc > 0.00008: #약5천원 정도임
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
