from trade_base import TradeBase
from balance import Balance

BF_FEE_RATE = 0.02
GM_FEE_RATE = 0.04

class TradeSim(TradeBase):

    #-------------------------------------------------
    # コストラクタ
    #-------------------------------------------------
    def __init__(self, bitflyer, coincheck, gmo):
        #super.__init__(bitflyer, coincheck, gmo)
        self.bf_balance = Balance(50000, 0.1)
        self.cc_balance = Balance(50000, 0.1)
        self.gm_balance = Balance(50000, 0.1)
        return

    #-------------------------------------------------
    # 現在の資産を表示
    #-------------------------------------------------
    def get_current_balance(self):
        bf_jpy = self.bf_balance.jpy
        bf_btc = self.bf_balance.btc
        cc_jpy = self.cc_balance.jpy
        cc_btc = self.cc_balance.btc
        gm_jpy = self.gm_balance.jpy
        gm_btc = self.gm_balance.btc
        print('BF:', bf_jpy, bf_btc)
        print('CC:', cc_jpy, cc_btc)
        print('GM:', gm_jpy, gm_btc)
        print('TOTAL:', bf_jpy + cc_jpy + gm_jpy, bf_btc + cc_btc + gm_btc)
        return bf_jpy, bf_btc, cc_jpy, cc_btc, gm_jpy, gm_btc

    #-------------------------------------------------
    # bitFlyerで買い
    #-------------------------------------------------
    def buy_bf(self, price, size):
        self.bf_balance.btc += size
        self.bf_balance.jpy -= (price * size)
        self.bf_balance.jpy -= (price * size * (BF_FEE_RATE / 100))
        return

    #-------------------------------------------------
    # bitFlyerで売り
    #-------------------------------------------------
    def sell_bf(self, price, size):
        self.bf_balance.btc -= size
        self.bf_balance.jpy += (price * size)
        self.bf_balance.jpy -= (price * size * (BF_FEE_RATE / 100))
        return

    #-------------------------------------------------
    # Coincheckで買い
    #-------------------------------------------------
    def buy_cc(self, price, size):
        self.cc_balance.btc += size
        self.cc_balance.jpy -= (price * size)
        return

    #-------------------------------------------------
    # Coincheckで売り
    #-------------------------------------------------
    def sell_cc(self, price, size):
        self.cc_balance.btc -= size
        self.cc_balance.jpy += (price * size)
        return

    #-------------------------------------------------
    # GMOで買い
    #-------------------------------------------------
    def buy_gm(self, price, size):
        self.gm_balance.btc += size
        self.gm_balance.jpy -= (price * size)
        self.gm_balance.jpy -= (price * size * (GM_FEE_RATE / 100))
        return

    #-------------------------------------------------
    # GMOで売り
    #-------------------------------------------------
    def sell_gm(self, price, size):
        self.gm_balance.btc -= size
        self.gm_balance.jpy += (price * size)
        self.gm_balance.jpy -= (price * size * (GM_FEE_RATE / 100))
        return

