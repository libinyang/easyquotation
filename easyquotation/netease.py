# coding:utf8
import re
import time
import ast
import datetime

from . import basequotation, helpers


class netease(basequotation.BaseQuotation):
    """163免费行情获取"""

    max_num = 800

    """
    日内实时盘口（JSON）：
    http://api.money.163.com/data/feed/1000002,1000001,1000881,0601398,money.api

    历史成交数据（CSV）：
    http://quotes.money.163.com/service/chddata.html?code=0601398&start=20000720&end=20150508
    财务指标（CSV）：
    http://quotes.money.163.com/service/zycwzb_601398.html?type=report

    资产负债表（CSV）：
    http://quotes.money.163.com/service/zcfzb_601398.html

    利润表（CSV）：
    http://quotes.money.163.com/service/lrb_601398.html

    现金流表（CSV）：
    http://quotes.money.163.com/service/xjllb_601398.html

    杜邦分析（HTML）：
    http://quotes.money.163.com/f10/dbfx_601398.html
    """

    def get_urls(self, stock_list, mode=helpers.MOD_RT):
        if mode is helpers.MOD_RT:
            return [
                "http://api.money.163.com/data/feed/{0},money.api".format(code) for code in stock_list
                ]
        if mode is helpers.MOD_HISTORY:
            return [
                "http://quotes.money.163.com/service/chddata.html?code={0}&start={1}&end={2}".format(code, self.get_start_date(), self.get_end_date()) for code in stock_list
                ]
        else:
            return None

    def get_stock_type(self, stock_code):
        """判断股票ID对应的证券市场
        匹配规则
        ['50', '51', '60', '90', '110'] 为 sh
        ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
        ['5', '6', '9'] 开头的为 sh， 其余为 sz
        :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回0或1，否则使用内置规则判断
        :return '0' for sh or '1' for sz"""
        #print (stock_code)
        assert type(stock_code) is str, "stock code need str type"
        sh_head = ("50", "51", "60", "90", "110", "113",
                   "132", "204", "5", "6", "9", "7")
        if stock_code.startswith(("sh")):
            return "0"
        elif stock_code.startswith("sz"):
            return "1"
        else:
            return "0" if stock_code.startswith(sh_head) else "1"

    def gen_stock_prefix(self, stock_codes):
        return [
            self.get_stock_type(code) + code[-6:] for code in stock_codes
        ]

    def format_response_data(self, rep_data, prefix=False, mode=helpers.MOD_RT):
        if mode is helpers.MOD_RT:
            return self.format_rt_response_data(rep_data, prefix, mode)
        elif mode is helpers.MOD_HISTORY:
            return self.format_history_response_data(rep_data, prefix, mode)

    def format_rt_response_data(self, rep_data, prefix=False, mode=helpers.MOD_RT):
        rep=re.findall(r'[(](.*)[)]', str(rep_data))
        rep="".join(rep)
        tmpdict=ast.literal_eval(rep)
        stock_dict = dict()
        for key in tmpdict.keys():
            stock_dict[key] = dict(
                name=tmpdict[key]["name"],
                open=tmpdict[key]["open"],
                close=tmpdict[key]["yestclose"],
                now=tmpdict[key]["price"],
                high=tmpdict[key]["high"],
                low=tmpdict[key]["low"],
                turnover=tmpdict[key]["turnover"],
                volume=tmpdict[key]["volume"],
                bid1=tmpdict[key]["bid1"],
                bid1_volume=tmpdict[key]["bidvol1"],
                bid2=tmpdict[key]["bid2"],
                bid2_volume=tmpdict[key]["bidvol2"],
                bid3=tmpdict[key]["bid3"],
                bid3_volume=tmpdict[key]["bidvol3"],
                bid4=tmpdict[key]["bid4"],
                bid4_volume=tmpdict[key]["bidvol4"],
                bid5=tmpdict[key]["bid5"],
                bid5_volume=tmpdict[key]["bidvol5"],
                ask1=tmpdict[key]["ask1"],
                ask1_volume=tmpdict[key]["askvol1"],
                ask2=tmpdict[key]["ask2"],
                ask2_volume=tmpdict[key]["askvol2"],
                ask3=tmpdict[key]["ask3"],
                ask3_volume=tmpdict[key]["askvol3"],
                ask4=tmpdict[key]["ask4"],
                ask4_volume=tmpdict[key]["askvol4"],
                ask5=tmpdict[key]["ask5"],
                ask5_volume=tmpdict[key]["askvol5"],
                date=str(datetime.datetime.strptime(tmpdict[key]["update"], "%Y/%m/%d %H:%M:%S")).split()[0],
                time=str(datetime.datetime.strptime(tmpdict[key]["update"], "%Y/%m/%d %H:%M:%S")).split()[1],
                )
        return stock_dict

    # history data format:
    # '日期,股票代码,名称,收盘价,最高价,最低价,开盘价,前收盘,涨跌额,涨跌幅,换手率,成交量,成交金额,总市值,流通市值,成交笔数'
    # 开盘价 OPEN
    # 收盘价 CLOSE
    # 最高价 HIGH
    # 最低价 LOW
    # 最新价 NEW
    # 成交量 VOL
    # 成交额AMOUNT
    # 换手率EXCHANGE
    # 上涨家数ADVANCE
    # 下跌家数DECLINE
    # 内盘量BUYVOL
    # 外盘量SELLVOL
    # 是否内盘ISBUYORDER
    # 委买价BIDPRICE
    # 委买量BIDVOL
    # 委卖价ASKPRICE
    # ASKVOL(P1)
    # 即时数据DYNAINFO
    # 大盘开盘INDEXO
    # 大盘收盘INDEXC
    # 大盘最高INDEXH
    # 大盘最低 INDEXL
    # 大盘成交量INDEXV
    # 大盘成交额INDEXA
    # 大盘上涨家数INDEXADV
    # 大盘下跌家数INDEXDEC
    # 每手股数VOLUNIT
    # 流通盘CAPITAL
    # 总股本ZGB
    # 流通Ａ股AG
    # 流通Ｂ股BG
    # 总资产ZZC
    # 股东权益GDQY
    # 资本公积金ZBGJJ
    # 每股净资产MGJZC
    # 利润总额LRZE
    # 净利润JLR
    # 主营收入ZYSR
    # 中期每股收益ZQMGSY
    # 年度每股收益NDMGSY
    # 净资收益率SYL
    # 资产负债比ZCFZB
    # 市盈率MARKWIN
    # ５日均量AVGVOL5
    # 财务数据FINANCE
    # 当前日DAY
    # 当前星期WEEKDAY
    # 当前月MONTH
    # 当前年YEAR
    # 当前小时HOUR
    # 当前分钟MINUTE
    # 当前日期DATE
    # 当前时间TIME
    def format_history_response_data(self, rep_data, prefix=False, mode=helpers.MOD_HISTORY):
        rep="".join(rep_data) # remove '[]'
        rep=re.findall(r'[^\r\n]+', rep) # remove "\r\n" and store the data into an array
        stock_dict = dict()
        i=0
        for item in rep:
            # skip the first item, which is description, not real data
            if i == 0:
                i=i+1
                continue
            stock_item=re.findall(r'[^,]+', item)
            code=stock_item[1][-6:]
            stock_dict[stock_item[0]] = dict(
                name=stock_item[2], #名称
                open=float(stock_item[6]), #开盘价
                close=float(stock_item[3]), #收盘价
                high=float(stock_item[4]), #最高价
                low=float(stock_item[5]), #最低价
                prev_close=float(stock_item[7]), #前收盘
                change=float(stock_item[8]), #涨跌额
                change_rate=float(stock_item[9]), #涨跌幅
                exchange=float(stock_item[10]), #换手率
                volume=float(stock_item[11]), #成交量
                amount=float(stock_item[12]), #成交金额
                marketcap=float(stock_item[13]),  #Market capitalization 总市值
                cmarketcap=float(stock_item[14]), # circulation market capitalization 流通市值
                exlots=(stock_item[15]), #exchange lots 成交笔数
            )
            i=i+1

        return stock_dict
