# coding:utf8

from . import boc, daykline, hkquote, jsl, sina, tencent, timekline, netease


# pylint: disable=too-many-return-statements
def use(source):
    if source in ["sina"]:
        return sina.Sina()
    if source in ["jsl"]:
        return jsl.Jsl()
    if source in ["qq", "tencent"]:
        return tencent.Tencent()
    if source in ["boc"]:
        return boc.Boc()
    if source in ["timekline"]:
        return timekline.TimeKline()
    if source in ["daykline"]:
        return daykline.DayKline()
    if source in ["hkquote"]:
        return hkquote.HKQuote()
    if source in ["netease"]:
        return netease.netease()
    raise NotImplementedError
