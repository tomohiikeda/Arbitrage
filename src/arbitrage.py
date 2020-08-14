from enum import IntEnum
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..\\..\\ExchangeApi'))
from bitflyer_api_wrapper import BitflyerAPIWrapper
from coincheck_api_wrapper import CoincheckAPIWrapper
from gmo_api_wrapper import GmoAPIWrapper
from trade_sim import TradeSim
from trade import Trade
import configparser
import os
import time
import winsound

######################
# トレード種別クラス
######################
class TradeType(IntEnum):
    BF_BUY_CC_SELL = 0
    BF_BUY_GM_SELL = 1
    CC_BUY_BF_SELL = 2
    CC_BUY_GM_SELL = 3
    GM_BUY_BF_SELL = 4
    GM_BUY_CC_SELL = 5
    NO_TRADE = 6

######################
# トレード用の各種定数
######################
# 順方向トレードの最大数
MAX_TRADE_COUNT = 8
INITIAL_THRESHOLD = 1000
SETTLE_THRESHOLD = -100

# この価格差がついたらトレードする
TRADE_THRESHOLD = [INITIAL_THRESHOLD, \
                   INITIAL_THRESHOLD, \
                   INITIAL_THRESHOLD, \
                   INITIAL_THRESHOLD, \
                   INITIAL_THRESHOLD, \
                   INITIAL_THRESHOLD, \
                   0]

# トレードした回数
TRADE_COUNT = [0, 0, 0, 0, 0, 0, 0]

# 1回のトレード量
TRADE_SIZE = 0.01

######################
# アービトラージクラス
######################
class Arbitrage:

    #---------------------------------------------------
    # コンストラクタ
    #---------------------------------------------------
    def __init__(self):

        # 取引所APIの作成
        bf_api_key, bf_api_secret = self.__get_api_key('bitFlyer')
        cc_api_key, cc_api_secret = self.__get_api_key('Coincheck')
        gm_api_key, gm_api_secret = self.__get_api_key('GMO')
        self.bitflyer = BitflyerAPIWrapper(bf_api_key, bf_api_secret, 'BTC_JPY')
        self.coincheck = CoincheckAPIWrapper(cc_api_key, cc_api_secret, 'btc_jpy')
        self.gmo = GmoAPIWrapper(gm_api_key, gm_api_secret, 'BTC')
        return

    #---------------------------------------------------
    # APIキーとシークレットをファイルから読み出す
    #---------------------------------------------------
    def __get_api_key(self, exchange_name):
        path = os.path.dirname(os.path.abspath(__file__))
        inifile = configparser.SafeConfigParser()
        inifile.read(os.path.join(path, "api_key.ini"))
        api_key = inifile.get(exchange_name, 'key')
        api_secret = inifile.get(exchange_name, 'secret')
        return api_key, api_secret

    #---------------------------------------------------
    # アービトラージを開始する
    # modeが 'SIM' ならTradeSimクラスを、それ以外ならTradeクラスを作る
    #---------------------------------------------------
    def start(self, mode):
        if mode == 'SIM':
            self.trade = TradeSim(self.bitflyer, self.coincheck, self.gmo)
        else:
            self.trade = Trade(self.bitflyer, self.coincheck, self.gmo)

        while True:
            self.tick()
            time.sleep(1)

    #---------------------------------------------------
    # 一定時間処理
    #---------------------------------------------------
    def tick(self):

        # 現在の資産状況を取得
        self.__get_current_balance()

        # 現在の価格情報を取得
        bf_ltp, bf_bid, bf_ask = self.bitflyer.get_ticker()
        cc_ltp, cc_bid, cc_ask = self.coincheck.get_ticker()
        gm_ltp, gm_bid, gm_ask = self.gmo.get_ticker()
        
        # 価格情報を表示
        self.__print_table(bf_bid, bf_ask, cc_bid, cc_ask, gm_bid, gm_ask)
        
        # アビトラ実行
        self.__exec_arbitrage(bf_bid, bf_ask, cc_bid, cc_ask, gm_bid, gm_ask)
        
        # 後処理
        self.__post_process()

        return

    #---------------------------------------------------
    # アビトラを実行
    #---------------------------------------------------
    def __exec_arbitrage(self, bf_bid, bf_ask, cc_bid, cc_ask, gm_bid, gm_ask):

        # 取引タイプを求める
        trade_type = self.__judge_trade_type(bf_bid, bf_ask, cc_bid, cc_ask, gm_bid, gm_ask)
        print(trade_type)

        # NO_TRADEなら何もしないで終わり
        if trade_type == TradeType.NO_TRADE:
            return False

        winsound.Beep(880, 500)

        # 発注する
        if trade_type == TradeType.BF_BUY_CC_SELL:
            self.trade.buy_bf(bf_ask, TRADE_SIZE)
            self.trade.sell_cc(cc_bid, TRADE_SIZE)
        elif trade_type == TradeType.BF_BUY_GM_SELL:
            self.trade.buy_bf(bf_bid, TRADE_SIZE)
            self.trade.sell_gm(gm_ask, TRADE_SIZE)
        elif trade_type == TradeType.CC_BUY_BF_SELL:
            self.trade.buy_cc(cc_bid, TRADE_SIZE)
            self.trade.sell_bf(bf_ask, TRADE_SIZE)
        elif trade_type == TradeType.CC_BUY_GM_SELL:
            self.trade.buy_cc(cc_bid, TRADE_SIZE)
            self.trade.sell_gm(gm_ask, TRADE_SIZE)
        elif trade_type == TradeType.GM_BUY_BF_SELL:
            self.trade.buy_gm(gm_bid, TRADE_SIZE)
            self.trade.sell_bf(bf_ask, TRADE_SIZE)
        elif trade_type == TradeType.GM_BUY_CC_SELL:
            self.trade.buy_gm(gm_bid, TRADE_SIZE)
            self.trade.sell_cc(cc_ask, TRADE_SIZE)

        # テーブルを更新する
        self.__update_trade_table(trade_type)

        time.sleep(5)

        return True

    #---------------------------------------------------
    # 価格情報からトレード種別を求める
    #---------------------------------------------------
    def __judge_trade_type(self, bf_bid, bf_ask, cc_bid, cc_ask, gm_bid, gm_ask):
        bf_cc = bf_bid - cc_ask
        bf_gm = bf_bid - gm_ask
        cc_bf = cc_bid - bf_ask
        cc_gm = cc_bid - gm_ask
        gm_bf = gm_bid - bf_ask
        gm_cc = gm_bid - cc_ask
        diff_list = [cc_bf, gm_bf, bf_cc, gm_cc, bf_gm, cc_gm]

        # しきい値超えのトレードをリスト化する
        over_th_list = []
        for trtype in TradeType:
            if trtype != TradeType.NO_TRADE:
                if diff_list[int(trtype)] > TRADE_THRESHOLD[int(trtype)] and \
                   TRADE_COUNT[int(trtype)] < MAX_TRADE_COUNT:
                   over_th_list.append(trtype)

        # しきい値超えのもののから、
        # 逆トレード回数が0のもの＞逆トレード回数が多いもの の順でトレードする種別を決める
        max_trade_count = 0
        max_trade = TradeType.NO_TRADE
        for trtype in over_th_list:
            rev_trtype = self.__get_reverse_trade_type(trtype)
            if TRADE_COUNT[int(rev_trtype)] == 0:
                return trtype
            elif TRADE_COUNT[int(rev_trtype)] > max_trade_count:
                max_trade_count = TRADE_COUNT[int(rev_trtype)]
                max_trade = trtype

        return max_trade

    #---------------------------------------------------
    # 最大価格差とトレード種別を求める
    #---------------------------------------------------
    def __get_reverse_trade_type(self, trade_type):
        if trade_type == TradeType.BF_BUY_CC_SELL:
            return TradeType.CC_BUY_BF_SELL
        elif trade_type == TradeType.BF_BUY_GM_SELL:
            return TradeType.GM_BUY_BF_SELL
        elif trade_type == TradeType.CC_BUY_BF_SELL:
            return TradeType.BF_BUY_CC_SELL
        elif trade_type == TradeType.CC_BUY_GM_SELL:
            return TradeType.GM_BUY_CC_SELL
        elif trade_type == TradeType.GM_BUY_BF_SELL:
            return TradeType.BF_BUY_GM_SELL
        elif trade_type == TradeType.GM_BUY_CC_SELL:
            return TradeType.CC_BUY_GM_SELL
        else:
            return TradeType.NO_TRADE

    #---------------------------------------------------
    # 実行したトレード種別に従ってテーブルを更新する
    #---------------------------------------------------
    def __update_trade_table(self, trade_type):
        
        rev_trtype = self.__get_reverse_trade_type(trade_type)

        if TRADE_COUNT[int(rev_trtype)] == 0:
            TRADE_COUNT[int(trade_type)] += 1
            TRADE_THRESHOLD[int(rev_trtype)] = SETTLE_THRESHOLD * TRADE_COUNT[int(trade_type)]
        else:
            TRADE_COUNT[int(rev_trtype)] -= 1
            if TRADE_COUNT[int(rev_trtype)] == 0:
                TRADE_THRESHOLD[int(trade_type)] = INITIAL_THRESHOLD
            else:
                TRADE_THRESHOLD[int(trade_type)] = SETTLE_THRESHOLD * TRADE_COUNT[int(rev_trtype)]

    #---------------------------------------------------
    # 現在の板情報を表示
    #---------------------------------------------------
    def __print_table(self, bf_bid, bf_ask, cc_bid, cc_ask, gm_bid, gm_ask):
        bf_cc = bf_bid - cc_ask
        bf_gm = bf_bid - gm_ask
        cc_bf = cc_bid - bf_ask
        cc_gm = cc_bid - gm_ask
        gm_bf = gm_bid - bf_ask
        gm_cc = gm_bid - cc_ask
        print(time.time())
        print('-------------------------------------------------------------')
        print('|              | BF売', bf_bid, '| CC売', cc_bid, '| GM売', gm_bid)
        print('---------------+--------------+--------------+---------------')
        print('| BF買', bf_ask, '|       -      |    ', cc_bf, '    |    ', gm_bf, '    |')
        print('| CC買', cc_ask, '|     ', bf_cc, '    |       -      |    ', gm_cc ,'    |')
        print('| GM買', gm_ask, '|     ', bf_gm, '    |    ', cc_gm, '      |       -      |')
        print('-------------------------------------------------------------')

    #---------------------------------------------------
    # 後処理
    #---------------------------------------------------
    def __post_process(self):
        for trtype in TradeType:
            itrtype = int(trtype)
            print(trtype, TRADE_THRESHOLD[itrtype], TRADE_COUNT[itrtype])

        return

    #---------------------------------------------------
    # 現在資産を表示
    #---------------------------------------------------
    def __get_current_balance(self):
        self.trade.get_current_balance()
        return
