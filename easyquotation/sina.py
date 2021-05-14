# coding:utf8
import re
import time

from . import basequotation, helpers


class Sina(basequotation.BaseQuotation):
    """新浪免费行情获取"""

    max_num = 800
    grep_detail = re.compile(
        r"(\d+)=[^\s]([^\s,]+?)%s%s"
        % (r",([\.\d]+)" * 29, r",([-\.\d:]+)" * 2)
    )
    grep_detail_with_prefix = re.compile(
        r"(\w{2}\d+)=[^\s]([^\s,]+?)%s%s"
        % (r",([\.\d]+)" * 29, r",([-\.\d:]+)" * 2)
    )
    del_null_data_stock = re.compile(
        r"(\w{2}\d+)=\"\";"
    )

    def get_urls(self, stock_list, mode=helpers.MOD_RT):
        if mode is helpers.MOD_RT:
            return [
                f"http://hq.sinajs.cn/rn={int(time.time() * 1000)}&list=" + code for code in stock_list
            ]
        else:
            return None

    def format_response_data(self, rep_data, prefix=False, mode=helpers.MOD_RT):
        if mode is helpers.MOD_RT:
            return self.format_rt_response_data(rep_data, prefix, mode)
        else:
            return None

    def format_rt_response_data(self, rep_data, prefix=False, mode=helpers.MOD_RT):
        stocks_detail = "".join(rep_data)
        stocks_detail = self.del_null_data_stock.sub('', stocks_detail)
        stocks_detail = stocks_detail.replace(' ', '')
        grep_str = self.grep_detail_with_prefix if prefix else self.grep_detail
        result = grep_str.finditer(stocks_detail)
        stock_dict = dict()
        for stock_match_object in result:
            stock = stock_match_object.groups()
            stock_dict[stock[0]] = dict(
                name=stock[1],
                open=float(stock[2]), 		# 开盘价
                close=float(stock[3]),		# 收盘价
                now=float(stock[4]),		# 当前价
                high=float(stock[5]),		# 最高价
                low=float(stock[6]),		# 最低价
                turnover=float(stock[10]),	# 成交额
                volume=int(stock[9]),		# 成交量
                bid1=float(stock[12]),
                bid1_volume=int(stock[11]),
                bid2=float(stock[14]),
                bid2_volume=int(stock[13]),
                bid3=float(stock[16]),
                bid3_volume=int(stock[15]),
                bid4=float(stock[18]),
                bid4_volume=int(stock[17]),
                bid5=float(stock[20]),
                bid5_volume=int(stock[19]),
                ask1=float(stock[22]),
                ask1_volume=int(stock[21]),
                ask2=float(stock[24]),
                ask2_volume=int(stock[23]),
                ask3=float(stock[26]),
                ask3_volume=int(stock[25]),
                ask4=float(stock[28]),
                ask4_volume=int(stock[27]),
                ask5=float(stock[30]),
                ask5_volume=int(stock[29]),
                date=stock[31],
                time=stock[32],
            )
        return stock_dict
