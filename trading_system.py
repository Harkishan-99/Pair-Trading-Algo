"""
This script contains the main trading system.
"""
import time
import logging
import numpy as np
from time import sleep
from datetime import datetime, timedelta
from alpaca_trade_api.rest import TimeFrame

from connection import Client
from strategy import PairsTrading

MAX_BUDGET = 10000

# logging init
logging.basicConfig(
    filename='error.log',
    level=logging.WARNING,
    format='%(asctime)s:%(levelname)s:%(message)s')


# setup the connection with the API
client = Client()
websocket = client.streaming_api()
api = client.rest_api()

class System:
    def __init__(self, pair:list, thresholds:list, lookback_window:int):
        """
        Create an instance of the Trading System for Pairs-Trading.
        """
        #create a strategy object with long and short threshold
        self.strategy = PairsTrading(thresholds[0], thresholds[1])
        self.window = lookback_window
        self.S1, self.S2 = pair[0], pair[1]

    def close_position(self):
        """
        Close the current market position of the pair.
        """
        try:
            # close the position if exist
            res_1 = api.close_position(self.S1)
            res_2 = api.close_position(self.S2)
            # check if filled
            status = [api.get_order(res_1.id).status,
                      api.get_order(res_2.id).status]
            return status
        except Exception as e:
            logging.exception(e)

    def _check_market_open(self):
        """
        A function to check if the market open. If not the sleep till
        the market opens.
        """
        clock = api.get_clock()
        if clock.is_open:
            pass
        else:
            time_to_open = clock.next_open - clock.timestamp
            print(
                f"Market is closed now going to sleep for {time_to_open.total_seconds()//60} minutes")
            time.sleep(time_to_open.total_seconds())

    def get_dollar_qty(self, symbol:str)->int:
        """
        Get the Quantity of stocks to trade based on the dollar value.

        :param symbol:(str) ticker symbol of the stock.
        :return :(int)Quantity to trade.
        """
        current_asset_price = api.get_latest_trade('ALK').price
        qty = (MAX_BUDGET/2) // current_asset_price
        return qty

    def OMS(self, side:str):
        """
        A simple Order Management System that sends out orders to the Broker
        on arrival of a trading signal.

        :param side:(str) side of the signal either BUY or SELL the spread.
        :return: (None)
        """
        sides = ['buy', 'sell']
        if side=='SELL':
            sides = ['sell', 'buy']
        try:
            order_info_1 = api.submit_order(
                            symbol=self.S1,
                            qty=get_dollar_qty(self.S1),
                            side=sides[0],
                            type='market',
                            time_in_force='day')

            order_info_2 = api.submit_order(
                            symbol=self.S2,
                            qty=get_dollar_qty(self.S2),
                            side=sides[0],
                            type='market',
                            time_in_force='day')
            print(order_info_1, order_info_2)
        except Exception as e:
            logging.exception(e)

    def get_latest_spread(self):
        """
        Calculates the latest spread using the daily data bars.

        :return :(None)
        """
        start = str((datetime.now() - timedelta(days=window_size)).date())
        end = (datetime.now().date())
        try:
            S1_price = api.get_bars(self.S1, TimeFrame.Day,
                              start, end, adjustment='all').df.close.values
            S2_price = api.get_bars(self.S2, TimeFrame.Day,
                              start, end, adjustment='all').df.close.values
        except Exception as e:
            logging.exception(e)
        self.spread = self.S1_price/self.S2_price


    def run(self):
        """
        Start the Trading System
        """
        while True:
            self._check_market_open()
            #close any open positions
            self.close_position()
            #get the check for position using latest data
            self.get_latest_spread
            signal = self.strategy.check_for_trades(self.spread)
            if signal=='BUY' or signal=='SELL':
                self.OMS(signal)
            elif signal=='CLOSE':
                self.close_position()
            #sleep for till next day
            time.sleep(24*60*60)
