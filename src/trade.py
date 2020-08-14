from trade_base import TradeBase
from bitflyer_api_wrapper import BitflyerAPIWrapper
from coincheck_api_wrapper import CoincheckAPIWrapper
from gmo_api_wrapper import GmoAPIWrapper

class Trade(TradeBase):

    #-------------------------------------------------
    # コンストラクタ
    #-------------------------------------------------
    def __init__(self, bitflyer, coincheck, gmo):
        super.__init__(bitflyer, coincheck, gmo)

    #-------------------------------------------------
    # 現在の資産を表示
    #-------------------------------------------------
    def get_current_balance(self):
        # TODO 1分に1回だけ資産情報を取得して表示する予定
        return

    #-------------------------------------------------
    # bitFlyerで買い
    #-------------------------------------------------
    def buy_bf(self, price, size):
        return

    #-------------------------------------------------
    # bitFlyerで売り
    #-------------------------------------------------
    def sell_bf(self, price, size):
        return

    #-------------------------------------------------
    # Coincheckで買い
    #-------------------------------------------------
    def buy_cc(self, price, size):
        return

    #-------------------------------------------------
    # Coincheckで売り
    #-------------------------------------------------
    def sell_cc(self, price, size):
        return

    #-------------------------------------------------
    # GMOで買い
    #-------------------------------------------------
    def buy_gm(self, price, size):
        return

    #-------------------------------------------------
    # GMOで売り
    #-------------------------------------------------
    def sell_gm(self, price, size):
        return
