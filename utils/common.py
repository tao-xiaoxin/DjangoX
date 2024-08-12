#!/bin/python
# coding: utf-8
"""
@Remark: 公用方法
"""
import os, re
import random
import time
from rest_framework.request import Request
from django.http import QueryDict
from urllib.parse import urlparse
import datetime
import ast
import base64
import hashlib
import json

# 手机号验证正则
REGEX_MOBILE = r"^1[356789]\d{9}$|^147\d{8}$|^176\d{8}$"

# 身份证正则
IDCARD_MOBILE = r"^[1-9]\d{5}(18|19|20|(3\d))\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$"


# 随机生成6位大写的邀请码:8614LY
def getinvitecode6():
    random_str = getRandomSet(6)
    return random_str.upper()


# 生成随机得指定位数字母+数字字符串
def getRandomSet(bits):
    """
    bits:数字是几就生成几位
    """
    num_set = [chr(i) for i in range(48, 58)]
    char_set = [chr(i) for i in range(97, 123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set


def hide4mobile(mobile):
    """
    隐藏手机号中间四位
    """
    if re.match(r"^\d{11}$", mobile):
        list = mobile[3:7]
        new_phone = mobile.replace(list, '****', 1)
        return new_phone
    else:
        return ""


def float2dot(str):
    """
    把数字或字符串10.00 转换成保留后两位（字符串）输出
    """
    try:
        return '%.2f' % round(float(str), 2)
    except:
        return str


"""
格式化日期时间为指定格式
"""


def formatdatetime(datatimes):
    """
    格式化日期时间为指定格式
    :param datatimes: 数据库中存储的datetime日期时间,也可以是字符串形式(2021-09-23 11:22:03.1232000)
    :return: 格式化后的日期时间如：2021-09-23 11:22:03
    """
    if datatimes:
        try:
            if isinstance(datatimes, str):
                if "." in datatimes:
                    arrays = datatimes.split(".", maxsplit=1)
                    if arrays:
                        return arrays[0]
            return datatimes.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return datatimes
    return datatimes


def formatdatetime_convert(datatimes):
    """
    格式化字符串日期时间为 python的日期时间
    :param datatimes: 字符串形式(2021-09-23 11:22:03 或 2021-09-23)
    :return: 反格式化后的日期时间如：datetime.datetime(2021, 9, 23, 11, 22, 3)
    """
    if datatimes:
        try:
            if isinstance(datatimes, str):
                if ':' in datatimes:
                    return datetime.datetime.strptime('datatimes', '%Y-%m-%d %H:%M:%S')
                else:
                    return datetime.datetime.strptime('datatimes', '%Y-%m-%d')
        except Exception as e:
            return datatimes
    return datatimes


# 上传图片名自定义
"""
参数为图片文件名
"""


def renameuploadimg(srcimg):
    # 文件扩展名
    ext = os.path.splitext(srcimg)[1]
    # File names longer than 255 characters can cause problems on older OSes.
    if len(srcimg) > 255:
        ext = ext[:255]
    # 定义文件名，年月日时分秒随机数
    fn = time.strftime('%Y%m%d%H%M%S')
    fn = fn + '_%d' % random.randint(100, 999)
    # 重写合成文件名
    name = fn + ext
    return name


"""
获取url地址中的path部分
"""


def geturlpath(url):
    # ParseResult(scheme='https', netloc='blog.xxx.net', path='/yilovexing/article/details/96432467', params='', query='', fragment='')
    all = urlparse(url)
    path = all.path
    return path


"""
重写数据库中的图片url前缀路径，返回相对路径的url路径，保证服务器更换环境导致图片访问失败情况
适用于图片存储在服务器本地
"""


# Define the ParameterDict class
class ParameterDict:
    def __init__(self, data):
        self.__dict__.update(data)

    def __getattr__(self, item):
        return self.__dict__.get(item, None)


# 获取get 或 post的参数
# 使用方法：get_parameter_dic(request).name ,name为获取的参数名 ,此种方式获取name不存在不会报错，不存在会返回None
def get_parameter_dict(request, *args, **kwargs):
    if not isinstance(request, Request):
        return ParameterDict({})

    query_params = request.query_params
    if isinstance(query_params, QueryDict):
        query_params = query_params.dict()
    result_data = request.data
    if isinstance(result_data, QueryDict):
        result_data = result_data.dict()

    if query_params:
        return ParameterDict(query_params)
    else:
        return ParameterDict(result_data)


"""
把字符串列表转换成列表类型
"""


def srttolist(str):
    # ['http://6fb77aa4dd1d.ngrok.io/media/tasks/2021-08-16/20210816103922_38.png']
    if str:
        str1 = str.replace('[', '').replace(']', '').replace("\"", '').replace("\'", '')
        str2 = str1.split(',')
        return str2
    else:
        return []


# 获取请求用户的真实ip地址
def getrealip(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    return regip


# 生成订单号(短订单号)
def getminrandomodernum():
    basecode = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    basecode = basecode[2:]
    chagecode1 = random.randint(10, 99)
    chagecode3 = random.randint(10, 99)
    return str(basecode) + str(chagecode1) + str(chagecode3)


# 生成订单号（长订单号）
def getrandomodernum():
    basecode = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    chagecode1 = random.randint(100, 999)
    chagecode2 = random.randint(10, 99)
    chagecode3 = str(time.time()).replace('.', '')[-7:]
    return str(basecode) + str(chagecode1) + str(chagecode2) + chagecode3


# 判断是否为金额(不包含0)，（正整数金额，不包含小数点）
def ismoney(num):
    try:
        pattern = re.compile(r'^[0-9]\d*$')
        if not num:
            return False
        val = int(num)
        if val <= 0:
            return False
        result = pattern.match(num)
        if result:
            return True
        else:
            return False
    except Exception as e:
        return False


# 判断是否为正确的价格（正整数、小数（小数点后两位）、非0）
def isRealPrice(num):
    try:
        if num == "" or num == None or num == 0 or num == '0':
            return False
        value = str(num)
        pattern = re.compile(r"(^[0-9]\d*$)|(^(([1-9]{1}\d*)|(0{1}))(\.\d{0,2})?$)")  # 正整数判断和小数判断
        result = pattern.match(value)
        if result:
            return True
        else:
            return False
    except Exception as e:
        return False


# 把字符串转换成数组对象等
def ast_convert(str):
    if str:
        try:
            myobject = ast.literal_eval(str)
            return myobject
        except Exception as e:
            return str

    return None


def bas64_encode_text(text):
    """
    base64加密字符串
    :param text:
    :return:
    """
    if isinstance(text, str):
        return str(base64.b64encode(text.encode('utf-8')), 'utf-8')
    return text


def bas64_decode_text(text):
    """
    base64解密字符串
    :param text:
    :return:
    """
    if isinstance(text, str):
        return str(base64.decodebytes(bytes(text, encoding="utf8")), 'utf-8')
    return text


class SnowflakeIDWorker:
    def __init__(self, datacenter_id, worker_id):
        """
        初始化 SnowflakeIDWorker
        :param datacenter_id: 数据中心ID (0-3)
        :param worker_id: 工作机器ID (0-3)
        """
        self.twepoch = int(time.time() * 1000)  # 设置起始时间戳（毫秒级）
        self.datacenter_id_bits = 2  # 数据中心ID所占位数
        self.worker_id_bits = 2  # 工作机器ID所占位数
        self.sequence_bits = 8  # 序列号所占位数

        # 计算最大值
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)  # 最大数据中心ID
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)  # 最大工作机器ID

        # 移位量
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        # 参数校验
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError(f"Datacenter ID不能大于{self.max_datacenter_id}或小于0")
        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError(f"Worker ID不能大于{self.max_worker_id}或小于0")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1

    def next_id(self):
        """
        生成下一个ID
        :return: 7-10位的唯一ID
        """
        timestamp = self.get_time()

        if timestamp < self.last_timestamp:
            raise ValueError("时钟回拨，拒绝生成ID")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                timestamp = self.til_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        # 生成ID
        new_id = ((timestamp - self.twepoch) << self.timestamp_left_shift) | \
                 (self.datacenter_id << self.datacenter_id_shift) | \
                 (self.worker_id << self.worker_id_shift) | \
                 self.sequence

        # 转换为字符串并取最后10位
        str_id = str(new_id)[-10:]

        # 确保ID至少有7位
        while len(str_id) < 7:
            str_id = '0' + str_id

        return str_id

    def til_next_millis(self, last_timestamp):
        """
        等待到下一个毫秒
        :param last_timestamp: 上次生成ID的时间戳
        :return: 新的时间戳
        """
        timestamp = self.get_time()
        while timestamp <= last_timestamp:
            timestamp = self.get_time()
        return timestamp

    def get_time(self):
        """
        获取当前时间戳（毫秒级）
        :return: 当前时间戳
        """
        return int(time.time() * 1000)


def getfulldomian(requests):
    host = '{scheme}://{host}'.format(scheme=requests.scheme, host=requests.get_host())
    return host


def md5(string):
    m = hashlib.md5()
    m.update(string.encode(encoding='utf-8'))
    return m.hexdigest()
