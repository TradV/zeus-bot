from coindcx.client import CoinDCX
from wazirx.client import WazirX
from wazirx import utils as wx_utils
from coindcx import utils as dcx_utils
from utils.orderbook import Orderbook
from utils.constants import market_symbols
import datetime


dcx = CoinDCX()
wx = WazirX()

arb_markets = [
    'btcinr',
    'ethinr'
]


def get_market_symbol(exchange_name, market):
    return market_symbols.get(market, {}).get(exchange_name)


def compute_arb(market):
    # print(f"\n\n*** Checking arb for market: {market} ***")
    dcx_symbol = market_symbols.get(market, {}).get(dcx.name)
    wx_symbol = market_symbols.get(market, {}).get(wx.name)
    if dcx_symbol is None or wx_symbol is None:
        print(f"ERROR: symbol not found: dcx_symbol: {dcx_symbol}, wx_symbol: {wx_symbol}")
        return

    def get_spread_prices(client, market, util):
        raw_orderbook = client.get_orderbook(market=market)
        tf_orderbook = util.transform_raw_orderbook(raw_orderbook)
        ob = Orderbook(bids=tf_orderbook['bids'], asks=tf_orderbook['asks'])
        return ob.spread_info.get_spread_entries()

    # get wazirx price
    wx_lowest_ask, wx_highest_bid = get_spread_prices(wx, wx_symbol, wx_utils)
    # print(f"wx: {(wx_lowest_ask.price, wx_highest_bid.price)}")

    # get dcx price
    dcx_lowest_ask, dcx_highest_bid = get_spread_prices(dcx, dcx_symbol, dcx_utils)
    # print(f"dcx: {(dcx_lowest_ask.price, dcx_highest_bid.price)}")

    if wx_highest_bid.price > dcx_lowest_ask.price:
        max_arb_quantity = min(wx_highest_bid.quantity, dcx_lowest_ask.quantity)
        delta_price = wx_highest_bid.price - dcx_lowest_ask.price
        potential_profit = delta_price * max_arb_quantity
        print(f'Arb Opportunity in market: {market}')
        print(f'\tTime: {datetime.datetime.now()}')
        print(f'\tBuy @CoinDCX for {dcx_lowest_ask.price}')
        print(f'\tSell @WazirX for {wx_highest_bid.price}')
        print(f'\tDelta Price: {delta_price}')
        print(f'\tMax arb quantity: {max_arb_quantity}')
        print(f'\tPotential profit: {potential_profit}')
        print("\n\n")

    if dcx_highest_bid.price > wx_lowest_ask.price:
        max_arb_quantity = min(dcx_highest_bid.quantity, wx_lowest_ask.quantity)
        delta_price = dcx_highest_bid.price - wx_lowest_ask.price
        potential_profit = delta_price * max_arb_quantity
        print(f'Arb Opportunity in market: {market}')
        print(f'\tTime: {datetime.datetime.now()}')
        print(f'\tBuy @WazirX for {wx_lowest_ask.price}')
        print(f'\tSell @CoinDCX for {dcx_highest_bid.price}')
        print(f'\tDelta Price: {delta_price}')
        print(f'\tMax arb quantity: {max_arb_quantity}')
        print(f'\tPotential profit: {potential_profit}')
        print("\n\n")


if __name__ == '__main__':
    while True:
        for market in arb_markets:
            compute_arb(market)
