import pytest
import time
import re
import socket
import logging


test_data_ban = [
    pytest.param(5001,
                 'Trade Disable',
                 id='money 5001')
                            ]

test_data_unban = [
    pytest.param(5000,
                 'Trade Enable',
                 id='money 5000')
                            ]


def send_request(query):
    wik_host = '127.0.0.1'
    wik_port = int(12345)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((wik_host, wik_port))
#    print("sending: ", query, "\n") #раскоменьть чтобы смотреть запросы
    s.send(query.encode())
    received = s.recv(4096)
    received = True
    response = ""
    while received:
        received = s.recv(4096)
        ureceived = str(received.decode("utf-8"))
        response += ureceived
    s.close()
    return response


def open_trade_order(login, buy_or_sell, lots, symbol):
    if buy_or_sell == 'buy' or 'BUY' or 'Buy':
        buy_or_sell = str(0)
    else:
        buy_or_sell = str(1)

    query = str(
        "action=openorder&login=" +
        str(login) +
        "&symbol=" +
        str(symbol) +
        "&cmd=" +
        buy_or_sell +
        "&volume=" +
        str(int(lots) * 100) +
        "&comment=Tristo")

    response = send_request(query)
    return response


def parse_order_id(response_from_wik):
    order_id = re.findall(r'(?<=orderid=)\d{0,10}|(?<=\n)\d{0,10}', str(response_from_wik))
    return order_id[0]


def deposit(login, value):
    query = str(
        "action=changebalance&login=" +
        str(login) +
        "&value=" +
        str(float(value)) +
        "&comment=Fus-Ro-Dah"
    )
    response = send_request(query)
    return response


def get_balance_info(login):
    query = str(
        "action=getaccountbalance&login=" +
        str(login)
    )
    response = send_request(query)
    reg = re.findall(r'(?<=balance=)\d{0,10}.\d{0,10}|(?<=\n)\d{0,10}', response)
    return reg[0]


def parse_balance_info(response):
    reg = re.findall(r'(?<=balance=)\d{0,10}.\d{0,10}|(?<=\n)\d{0,10}', response)
    return reg[0]


def make_zero_balance(login):
    response = get_balance_info(login)
    value = str("-" + str(response))
    deposit(login, value)
    return print("balance is zero")


def unban_akk(login):
    query = str(
        "action=modifyaccount&login=" +
        str(login) +
        "&enable_read_only=0"
    )
    response = send_request(query)
    return response


def banned_or_not(login):
    query = str(
        "action=getaccountinfo&login=" +
        str(login)
    )
    response = send_request(query)
    reg = re.findall(r'(?<=tradingblocked=)\d', response)
    if str(reg[0]) == '1':
        return "Trade Disable"
    elif str(reg[0]) == '0':
        return "Trade Enable"

#    (?<=enable=)\d{0,1}
#    getaccountinfo


#open_trade_order(login=300, buy_or_sell="buy", lots=1, symbol="EURUSD")

#deposit(300, 1000.51)

#print(get_balance_info(300))

#make_zero_balance(300)

#print(get_balance_info(300))

#time.sleep(2)

#deposit(300, 5000)

#unban_akk(300)

#print(get_balance_info(300))

#print(banned_or_not(300))


@pytest.mark.parametrize('test_input, expected', test_data_ban)
def test_ban(test_input, expected):
    login = 300
    make_zero_balance(login)
    deposit(300, test_input)
    unban_akk(login)
    open_trade_order(login, "buy", 1, "EURUSD")
    logging.info(banned_or_not(login))
    logging.info(expected)
    assert banned_or_not(login) == expected


@pytest.mark.parametrize('test_input, expected', test_data_unban)
def test_ban_unban(test_input, expected):
    login = 300
    make_zero_balance(login)
    deposit(300, test_input + 1)
    unban_akk(login)
    open_trade_order(login, "buy", 1, "EURUSD")
    time.sleep(1.0)
    make_zero_balance(login)
    deposit(300, test_input)
    unban_akk(login)
    logging.info(banned_or_not(login))
    logging.info(expected)
    assert banned_or_not(login) == expected

