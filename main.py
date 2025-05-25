import requests
import sqlite3
from json import JSONDecodeError
from pybit.unified_trading import HTTP
from pygame import mixer
from threading import *
from win10toast import ToastNotifier
mixer.init()
bildirim = ToastNotifier()
#Repeater
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args,**self.kwargs)
#sound
notification = mixer.Sound('Beep.mp3')
conn_database3 = sqlite3.connect("database3.sqlite", check_same_thread=False)
database3 = conn_database3.cursor()
database3.execute('CREATE TABLE IF NOT EXISTS informations (token,gate,kucoin,binance,bybit,decimal,percent,mexc)')
conn_database3.commit()

conn_database2 = sqlite3.connect("database2.sqlite", check_same_thread=False)
database2 = conn_database2.cursor()
database2.execute(
            'CREATE TABLE IF NOT EXISTS informations (token,gate,kucoin,binance,bybit,decimal,percent,mexc)')
conn_database2.commit()

conn_database = sqlite3.connect("database.sqlite", check_same_thread=False)
database = conn_database.cursor()

database.execute(
            'CREATE TABLE IF NOT EXISTS informations (token,gate,kucoin,binance,bybit,decimal,percent,mexc)')
conn_database.commit()
#Send msg on Discord
def sendMessage(information):

    url = 'https://discord.com/api/v9/channels/464752718435844096/messages'
    mesaj = {
        "content": f'{information}'
    }
    token = {
        "authorization": "NDQ4NTE2MjUwMDg4MjQzMjIw.GtM2wE.EjXa65-_ASJSfBxvr7Cx7ou2FuJFt_XFaLHFL8"
    }
    requests.post(url, headers=token, data=mesaj)

#Simple requests for checking price
def KuCoin(name):
    url = f'https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol={name}'
    r = requests.get(url)
    data = r.json()['data']
    asks = data['asks']
    bids = data['bids']
    return asks[0][0], bids[0][0]

def binance(name):
    url = f"https://api.binance.com/api/v3/depth?limit=10&symbol={name}"
    data = requests.get(url).json()
    bids = data["bids"]
    asks = data["asks"]
    return asks[0][0], bids[0][0]

def BYBIT(name):
    session = HTTP(testnet=False)
    data = session.get_orderbook(category="spot",symbol="AVAXUSDT")["result"]

    asks = data['a']
    bids = data['b']
    return asks[0][0], bids[0][0]

def GateR(name):

    host = "https://api.gateio.ws"
    prefix = "/api/v4"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    url = '/spot/order_book'
    query = f'currency_pair={name}'
    r = requests.request('GET', host + prefix + url + "?" + query, headers=headers)
    data = r.json()
    asks = data['asks']
    bids = data['bids']
    return asks[0][0], bids[0][0]

def mexc(name):
    url = f"https://api.mexc.com/api/v3/depth?symbol={name}"
    r = requests.get(url)
    data = r.json()
    asks = data["asks"]
    bids = data["bids"]
    return asks[0][0],bids[0][0]
def jupReq(token, decimal):
    
    url1 = f"https://quote-api.jup.ag/v6/quote?inputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&outputMint={token}&amount=500000000"
    response1 = requests.get(url1)
    response1.raise_for_status()  # HTTP hatalarını yakalar
    sell = int(response1.json()["outAmount"])
    sellPrice = 500000000 / sell * 10**(int(decimal)-6)
    sellDexes = []
    for i in (response1.json()["routePlan"]):
        sellDexes.append(str(i["swapInfo"]["label"]))
    #print(sellDexes)

    url2 = f"https://quote-api.jup.ag/v6/quote?inputMint={token}&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount={sell}"
    response2 = requests.get(url2)
    response2.raise_for_status()  # HTTP hatalarını yakalar
    buy = int(response2.json()["outAmount"]) / 1000000
    buyPrice = buy / (sell / 10**int(decimal))
    buyDexes = []
    for i in response2.json()["routePlan"]:
        buyDexes.append(str(i["swapInfo"]["label"]))
    #print(buyDexes)
    return sellPrice, buyPrice,sellDexes,buyDexes

def loopP(database3):

    print(database3)
    database3.execute(
        'SELECT token,gate,kucoin,binance,bybit,decimal,percent,mexc FROM informations')
    boyut = len(database3.fetchall())
    database3.execute(
        'SELECT token,gate,kucoin,binance,bybit,decimal,percent,mexc FROM informations')

    for i in database3.fetchmany(int(boyut)):

        Mexc = []
        Binance = []
        Gate = []
        Kucoin = []
        Bybit = []
        Jup = []

        try:
            Jup.append(jupReq(i[0],i[5]))
            print(i[0],": ",Jup)

            if str(i[1]) != '0':
                Gate.append(GateR(i[1]))
            if str(i[2]) != '0':
                Kucoin.append(KuCoin(i[2]))
            if str(i[3]) != '0':
                Binance.append(binance(i[3]))
            if str(i[4]) != '0':
                Bybit.append(BYBIT(i[4]))
            if str(i[7]) != '0':
                Mexc.append(mexc(i[7]))

            print(" Binance: ",Binance,"\n","Gate: ",Gate,"\n","Kucoin: ",Kucoin,"\n","Bybit: ",Bybit)

            if Gate:

                if (float(Gate[0][1]) - float(Jup[0][0]))/float(Jup[0][0])>= float(i[6]):

                    p = (float(Gate[0][1]) - float(Jup[0][0]))/float(Jup[0][0])
                    sendMessage(f'{i[1]}: {p} \n(Gate-Jup)\n{float(Gate[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    bildirim.show_toast(title="Fark",msg=f'{i[1]}: {p} \n(Gate-Jup)\n{float(Gate[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    notification.play()

                elif (float(Jup[0][1])-float(Gate[0][0]))/float(Gate[0][0])>= float(i[6]):

                    p = (float(Jup[0][1])-float(Gate[0][0]))/float(Gate[0][0])
                    sendMessage(f"{i[1]}: {p} \n(Jup-Gate)\n{float(Jup[0][1])} - {float(Gate[0][0])}\n{Jup[0][3]}")
                    bildirim.show_toast(title="Fark",
                                        msg=f"{i[1]}: {p} \n(Jup-Gate)\n{float(Jup[0][1])} - {float(Gate[0][0])}\n{Jup[0][3]}")
                    notification.play()

            if Kucoin:

                if (float(Kucoin[0][1]) - float(Jup[0][0]))/float(Jup[0][0])>= float(i[6]):

                    p = (float(Kucoin[0][1]) - float(Jup[0][0])) / float(Jup[0][0])
                    sendMessage(f'{i[2]}: {p} \n(Kucoin-Jup)\n{float(Kucoin[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    bildirim.show_toast(title="Fark",
                                        msg=f'{i[2]}: {p} \n(Kucoin-Jup)\n{float(Kucoin[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    notification.play()

                elif (float(Jup[0][1])-float(Kucoin[0][0]))/float(Kucoin[0][0])>= float(i[6]):

                    p = (float(Jup[0][1]) - float(Kucoin[0][0])) / float(Kucoin[0][0])
                    sendMessage(f"{i[2]}: {p} \n(Jup-Kucoin)\n{float(Jup[0][1])} - {float(Kucoin[0][0])}\n{Jup[0][3]}")
                    bildirim.show_toast(title="Fark",
                                        msg=f"{i[2]}: {p} \n(Jup-Kucoin)\n{float(Jup[0][1])} - {float(Kucoin[0][0])}\n{Jup[0][3]}")
                    notification.play()

            if Binance:

                if (float(Binance[0][1]) - float(Jup[0][0]))/float(Jup[0][0])>= float(i[6]):

                    p = (float(Binance[0][1]) - float(Jup[0][0])) / float(Jup[0][0])
                    sendMessage(f'{i[3]}: {p} \n(Binance-Jup)\n{float(Binance[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    bildirim.show_toast(title="Fark",
                                        msg=f'{i[3]}: {p} \n(Binance-Jup)\n{float(Binance[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    notification.play()

                elif (float(Jup[0][1])-float(Binance[0][0]))/float(Binance[0][0])>= float(i[6]):

                    p = (float(Jup[0][1]) - float(Binance[0][0])) / float(Binance[0][0])
                    sendMessage(f"{i[3]}: {p} \n(Jup-Binance)\n{float(Jup[0][1])} - {float(Binance[0][0])}\n{Jup[0][3]}")
                    bildirim.show_toast(title="Fark",
                                        msg=f"{i[3]}: {p} \n(Jup-Binance)\n{float(Jup[0][1])} - {float(Binance[0][0])}\n{Jup[0][3]}")
                    notification.play()

            if Bybit:

                if (float(Bybit[0][1]) - float(Jup[0][0]))/float(Jup[0][0])>= float(i[6]):

                    p = (float(Bybit[0][1]) - float(Jup[0][0])) / float(Jup[0][0])
                    sendMessage(f'{i[4]}: {p} \n(Bybit-Jup)\n{float(Bybit[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    bildirim.show_toast(title="Fark",
                                        msg=f'{i[4]}: {p} \n(Bybit-Jup)\n{float(Bybit[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    notification.play()

                elif (float(Jup[0][1])-float(Bybit[0][0]))/float(Bybit[0][0])>= float(i[6]):

                    p = (float(Jup[0][1]) - float(Bybit[0][0])) / float(Bybit[0][0])
                    sendMessage(f"{i[4]}: {p} \n(Jup-Bybit)\n{float(Jup[0][1])} - {float(Bybit[0][0])}\n{Jup[0][3]}")
                    bildirim.show_toast(title="Fark",
                                        msg=f"{i[4]}: {p} \n(Jup-Bybit)\n{float(Jup[0][1])} - {float(Bybit[0][0])}\n{Jup[0][3]}")
                    notification.play()

            if Mexc:

                if (float(Mexc[0][1]) - float(Jup[0][0])) / float(Jup[0][0]) >= float(i[6]):

                    p = (float(Mexc[0][1]) - float(Jup[0][0])) / float(Jup[0][0])
                    sendMessage(f'{i[7]}: {p} \n(Mexc-Jup)\n{float(Mexc[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    bildirim.show_toast(title="Fark",
                                        msg=f'{i[7]}: {p} \n(Mexc-Jup)\n{float(Mexc[0][1])} - {float(Jup[0][0])}\n{Jup[0][2]}')
                    notification.play()

                elif (float(Jup[0][1]) - float(Mexc[0][0])) / float(Mexc[0][0]) >= float(i[6]):

                    p = (float(Jup[0][1]) - float(Mexc[0][0])) / float(Mexc[0][0])
                    sendMessage(f"{i[7]}: {p} \n(Jup-Mexc)\n{float(Jup[0][1])} - {float(Mexc[0][0])}\n{Jup[0][3]}")
                    bildirim.show_toast(title="Fark",
                                        msg=f"{i[7]}: {p} \n(Jup-Mexc)\n{float(Jup[0][1])} - {float(Mexc[0][0])}\n{Jup[0][3]}")
                    notification.play()

        except requests.exceptions.ConnectionError:
            print('internet hatası')
            continue

        except requests.exceptions.ReadTimeout:
            print('internet hatası')
            continue

        except requests.exceptions.HTTPError:
            print('internet hatası')
            continue

        except requests.exceptions.ConnectTimeout:
            print('internet hatası')
            continue

        except IndexError:
            print('internet hatası')
            continue

        except JSONDecodeError:
            print('json hatası')
            print(i)
            continue

        except KeyError:

            print('jup borsa hatası1')

            continue
        
        except TypeError:

            print('jup borsa hatası2')

            continue


start = input("enter 1 for start: ")

if int(start) == 1:
    threads = []
    thread1 = RepeatTimer(0.1,loopP,[database])
    #thread2 = RepeatTimer(1,loopP,[database2])
    #thread3 = RepeatTimer(1,loopP,[database3])
    threads.append(thread1)
    #threads.append(thread2)
    #threads.append(thread3)
    threads[0].start()
    #threads[1].start()
    #threads[2].start()
else:
    print("Close and try again.")
