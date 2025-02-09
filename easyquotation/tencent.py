# coding:utf8
import re
from datetime import datetime
from typing import Optional

from . import basequotation, helpers


class Tencent(basequotation.BaseQuotation):
    """腾讯免费行情获取"""

    grep_stock_code = re.compile(r"(?<=_)\w+")
    max_num = 60

    def get_urls(self, stock_list, mode=helpers.MOD_RT):
        if mode is helpers.MOD_RT:
            return [
                "http://qt.gtimg.cn/q=" + code for code in stock_list
            ]

    def format_response_data(self, rep_data, prefix=False, mode=helpers.MOD_RT):
        if mode is helpers.MOD_RT:
            return self.format_rt_response_data(rep_data, prefix, mode)

    def format_rt_response_data(self, rep_data, prefix=False, mode=helpers.MOD_RT):
        stocks_detail = "".join(rep_data)
        stock_details = stocks_detail.split(";")
        stock_dict = dict()
        for stock_detail in stock_details:
            stock = stock_detail.split("~")
            if len(stock) <= 49:
                continue
            stock_code = (
                self.grep_stock_code.search(stock[0]).group()
                if prefix
                else stock[2]
            )
            stock_dict[stock_code] = {
                "name": stock[1],
                "open": float(stock[5]),
                "close": float(stock[4]),
                "now": float(stock[3]),
                "high": float(stock[33]),
                "low": float(stock[34]),
                "turnover": stock[35].split('/')[2],
                "volume": float(stock[6]) * 100,
                "bid1": float(stock[9]),
                "bid1_volume": int(stock[10]) * 100,
                "bid2": float(stock[11]),
                "bid2_volume": int(stock[12]) * 100,
                "bid3": float(stock[13]),
                "bid3_volume": int(stock[14]) * 100,
                "bid4": float(stock[15]),
                "bid4_volume": int(stock[16]) * 100,
                "bid5": float(stock[17]),
                "bid5_volume": int(stock[18]) * 100,
                "ask1": float(stock[19]),
                "ask1_volume": int(stock[20]) * 100,
                "ask2": float(stock[21]),
                "ask2_volume": int(stock[22]) * 100,
                "ask3": float(stock[23]),
                "ask3_volume": int(stock[24]) * 100,
                "ask4": float(stock[25]),
                "ask4_volume": int(stock[26]) * 100,
                "ask5": float(stock[27]),
                "ask5_volume": int(stock[28]) * 100,
                "date": str(datetime.strptime(stock[30], "%Y%m%d%H%M%S")).split()[0],
                "time": str(datetime.strptime(stock[30], "%Y%m%d%H%M%S")).split()[1],
                "PE": self._safe_float(stock[39]),
                "流通市值": self._safe_float(stock[44]),
                "总市值": self._safe_float(stock[45]),
                "PB": float(stock[46]),
                "量比": self._safe_float(stock[49]),
                "委差": self._safe_acquire_float(stock, 50),
                "均价": self._safe_acquire_float(stock, 51),
                "市盈(动)": self._safe_acquire_float(stock, 52),
                "市盈(静)": self._safe_acquire_float(stock, 53),
            }
        return stock_dict

    def _safe_acquire_float(self, stock: list, idx: int) -> Optional[float]:
        """
        There are some securities that only have 50 fields. See example below:
        ['\nv_sh518801="1',
        '国泰申赎',
        '518801',
        '2.229',
        ......
         '', '0.000', '2.452', '2.006', '"']
        """
        try:
            return self._safe_float(stock[idx])
        except IndexError:
            return None

    def _safe_float(self, s: str) -> Optional[float]:
        try:
            return float(s)
        except ValueError:
            return None
