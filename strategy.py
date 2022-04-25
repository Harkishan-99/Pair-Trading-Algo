"""
This script contains a simple pairs strategy.

Step 1: Calculate the spread ratio.
Step 2: Calculate the z-score.
Step 3: Check if the z-score is above or below the threshold level.
Step 4: If trade is generated then return the trade.

Strategy -
1) BUY the spread when z-score if below the threshold level.
2) SELL the spread when z-score is above the threshold level.
3) Close the LONG position when z-score crosses 0 from below.
4) Close the SHORT position when z-score crosses 0 from above.

Betting strategy -

Bet equal dollar amount in both long and short position.
"""

import numpy as np

class PairsTrading:
    def __init__(self, long_threshold:float=-1.65,
                 short_threshold:float=1.65):
        """
        Create an instance of pairs trading strategy.

        :param long_threshold:(float) the threshold to trigger a long position
                                on the spread.
        :param short_threshold:(float) the threshold to trigger a short position
                                on the spread.
        """
        self.lt = long_threshold
        self.st = short_threshold
        self.position = None

    def zscore(self, spread:np.array)->float:
        """
        Get the latest zscore from the spread.

        :param spread:(np.array) the spread of that pair.
        :return:(float) zscore
        """
        return (spread[-1] - np.mean(spread)) / np.std(spread)

    def check_for_trades(self, spread:np.array)->str:
        """
        Check for trade signals i.e. if zscore exceeds any threshold.

        :param spread:(np.array) the spread of that pair.
        :return:(str) signals BUY, SELL or CLOSE
        """
        zscore = self.zscore(spread)
        if self.position is None:
            if zscore > self.lt:
                #short the spread
                self.position = 'short'
                return 'SHORT'
            elif zscore < self.st:
                #long the spread
                self.position = 'long'
                return 'LONG'
        else:
            if (self.position == 'short' and zscore <= 0) or\
                self.position == 'long' and zscore >= 0:
                #close the spread position
                self.position = None
                return 'CLOSE'
