# coding:utf8
import abc
import json
import multiprocessing.pool
import warnings
import datetime

import requests

from . import helpers


class BaseQuotation(metaclass=abc.ABCMeta):
    """行情获取基类"""

    max_num = 800  # 每次请求的最大股票数

    curr_time=datetime.datetime.now()
    time_str=curr_time.strftime("%Y%m%d")
    start_date = "20200101"
    end_date = time_str

    # start, end is the date of duration
    # the format is like 20210414
    def set_history_date(self, start, end):
        #todo: check start and end format is valid or not
        self.start_date = str(start)
        self.end_date = str(end)

    def get_history_date(self):
        print(self.start_date)
        print(self.end_date)

    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date

    def __init__(self):
        self._session = requests.session()
        stock_codes = self.load_stock_codes()
        self.stock_list = self.gen_stock_list(stock_codes)

    def gen_stock_list(self, stock_codes):
        stock_with_exchange_list = self.gen_stock_prefix(stock_codes)

        if self.max_num > len(stock_with_exchange_list):
            request_list = ",".join(stock_with_exchange_list)
            return [request_list]

        stock_list = []
        for i in range(0, len(stock_codes), self.max_num):
            request_list = ",".join(
                stock_with_exchange_list[i : i + self.max_num]
            )
            stock_list.append(request_list)
        return stock_list

    def gen_stock_prefix(self, stock_codes):
        return [
            helpers.get_stock_type(code) + code[-6:] for code in stock_codes
        ]

    @staticmethod
    def load_stock_codes():
        with open(helpers.STOCK_CODE_PATH) as f:
            return json.load(f)["stock"]

    @property
    def all(self):
        warnings.warn("use market_snapshot instead", DeprecationWarning)
        return self.get_stock_data(self.stock_list, prefix=False)

    @property
    def all_market(self):
        """return quotation with stock_code prefix key"""
        return self.get_stock_data(self.stock_list, prefix=True)

    def stocks(self, stock_codes, prefix=False):
        return self.real(stock_codes, prefix)

    def real(self, stock_codes, prefix=False):
        """return specific stocks real quotation
        :param stock_codes: stock code or list of stock code,
                when prefix is True, stock code must start with sh/sz
        :param prefix: if prefix i True, stock_codes must contain sh/sz market
            flag. If prefix is False, index quotation can't return
        :return quotation dict, key is stock_code, value is real quotation.
            If prefix with True, key start with sh/sz market flag

        """
        if not isinstance(stock_codes, list):
            stock_codes = [stock_codes]

        stock_list = self.gen_stock_list(stock_codes)
        return self.get_stock_data(stock_list, prefix=prefix)

    def market_snapshot(self, prefix=False):
        """return all market quotation snapshot
        :param prefix: if prefix is True, return quotation dict's  stock_code
             key start with sh/sz market flag
        """
        return self.get_stock_data(self.stock_list, prefix=prefix)

    def get_stocks_history(self, stock_code, prefix=False):
        if not isinstance(stock_code, list):
            stock_code = [stock_code]

        if len(stock_code) > 1:
            print ("it only supports fetch stock history data one by one, don't input multiple stock codes")
            return -1
        stock_list = self.gen_stock_list(stock_code)

        return self.get_stock_data(stock_list, prefix=prefix, mode=helpers.MOD_HISTORY)

    def get_stocks_by_range(self, params):
        headers = {
            "Accept-Encoding": "gzip, deflate, sdch",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/54.0.2840.100 "
                "Safari/537.36"
            ),
        }

        r = self._session.get(params, headers=headers)
        return r.text

    def get_stock_data(self, stock_list, prefix, mode=helpers.MOD_RT):
        """获取并格式化股票信息"""
        urls = self.get_urls(stock_list, mode)
        if urls is None:
            print ("URLs is none, please check if stock code is correct or if site supports the mode")
            return
        res = self._fetch_stock_data(urls)
        return self.format_response_data(res, prefix, mode)

    def _fetch_stock_data(self, urls):
        """获取股票信息"""
        pool = multiprocessing.pool.ThreadPool(len(urls))
        try:
            res = pool.map(self.get_stocks_by_range, urls)
        finally:
            pool.close()
        return [d for d in res if d is not None]

    def format_response_data(self, rep_data, prefix, mode):
        pass

    def format_rt_response_data(self, rep_data, prefix, mode):
        pass

    def get_urls(self, stock_list, mode):
        pass
