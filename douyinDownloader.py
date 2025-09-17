#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
抖音下载器 - 支持Windows、Linux、macOS和Android系统

功能特性：
- 支持用户主页视频下载
- 支持合集视频下载
- 支持单个视频下载
- 支持图片作品下载
- 支持直播录制
- 自动检测操作系统并设置合适的下载路径
- Android系统自动使用/sdcard/Download/目录

使用方法：
1. 安装依赖: pip install requests gmssl m3u8
2. 运行脚本: python douyinDownloader.py
3. 在Android上使用Termux运行

Android安装步骤：
1. 安装Termux: https://f-droid.org/packages/com.termux/
2. 安装Python: pkg install python
3. 安装依赖: pip install requests gmssl m3u8
4. 运行脚本: python douyinDownloader.py
"""
import sys

import requests
import json
import os
import time
import re
import random
import string
import m3u8

from gmssl import sm3, func
from typing import Union, Callable, List, Dict


class StringProcessor:
    """简化的字符串处理工具类"""
    
    @staticmethod
    def to_ord_array(s: str) -> List[int]:
        """将字符串转换为 ASCII 码列表"""
        return [ord(char) for char in s]

    @staticmethod
    def to_char_str(s: List[int]) -> str:
        """将 ASCII 码列表转换为字符串"""
        return "".join([chr(i) for i in s])

    @staticmethod
    def js_shift_right(val: int, n: int) -> int:
        """实现 JavaScript 中的无符号右移运算"""
        return (val % 0x100000000) >> n

    @staticmethod
    def generate_random_bytes(length: int = 3) -> str:
        """生成伪随机字节字符串"""
        def generate_byte_sequence() -> List[str]:
            _rd = int(random.random() * 10000)
            return [
                chr(((_rd & 255) & 170) | 1),
                chr(((_rd & 255) & 85) | 2),
                chr((StringProcessor.js_shift_right(_rd, 8) & 170) | 5),
                chr((StringProcessor.js_shift_right(_rd, 8) & 85) | 40),
            ]

        result = []
        for _ in range(length):
            result.extend(generate_byte_sequence())
        return "".join(result)


class CryptoUtility:
    """简化的加密工具类"""
    
    def __init__(self, salt: str, custom_base64_alphabet: List[str]):
        self.salt = salt
        self.base64_alphabet = custom_base64_alphabet
        # 简化的加密数组
        self.big_array = [
            121, 243, 55, 234, 103, 36, 47, 228, 30, 231, 106, 6, 115, 95, 78, 101, 250, 207, 198, 50,
            139, 227, 220, 105, 97, 143, 34, 28, 194, 215, 18, 100, 159, 160, 43, 8, 169, 217, 180, 120,
            247, 45, 90, 11, 27, 197, 46, 3, 84, 72, 5, 68, 62, 56, 221, 75, 144, 79, 73, 161,
            178, 81, 64, 187, 134, 117, 186, 118, 16, 241, 130, 71, 89, 147, 122, 129, 65, 40, 88, 150,
            110, 219, 199, 255, 181, 254, 48, 4, 195, 248, 208, 32, 116, 167, 69, 201, 17, 124, 125, 104,
            96, 83, 80, 127, 236, 108, 154, 126, 204, 15, 20, 135, 112, 158, 13, 1, 188, 164, 210, 237,
            222, 98, 212, 77, 253, 42, 170, 202, 26, 22, 29, 182, 251, 10, 173, 152, 58, 138, 54, 141,
            185, 33, 157, 31, 252, 132, 233, 235, 102, 196, 191, 223, 240, 148, 39, 123, 92, 82, 128, 109,
            57, 24, 38, 113, 209, 245, 2, 119, 153, 229, 189, 214, 230, 174, 232, 63, 52, 205, 86, 140,
            66, 175, 111, 171, 246, 133, 238, 193, 99, 60, 74, 91, 225, 51, 76, 37, 145, 211, 166, 151,
            213, 206, 0, 200, 244, 176, 218, 44, 184, 172, 49, 216, 93, 168, 53, 21, 183, 41, 67, 85,
            224, 155, 226, 242, 87, 177, 146, 70, 190, 12, 162, 19, 137, 114, 25, 165, 163, 192, 23, 59,
            9, 94, 179, 107, 35, 7, 142, 131, 239, 203, 149, 136, 61, 249, 14, 156
        ]

    @staticmethod
    def sm3_to_array(input_data: Union[str, List[int]]) -> List[int]:
        """计算SM3哈希值并转换为整数数组"""
        if isinstance(input_data, str):
            input_data_bytes = input_data.encode("utf-8")
        else:
            input_data_bytes = bytes(input_data)
        
        hex_result = sm3.sm3_hash(func.bytes_to_list(input_data_bytes))
        return [int(hex_result[i : i + 2], 16) for i in range(0, len(hex_result), 2)]

    def add_salt(self, param: str) -> str:
        """添加盐值"""
        return param + self.salt

    def params_to_array(self, param: Union[str, List[int]], add_salt: bool = True) -> List[int]:
        """获取输入参数的哈希数组"""
        if isinstance(param, str) and add_salt:
            param = self.add_salt(param)
        return self.sm3_to_array(param)

    def transform_bytes(self, bytes_list: List[int]) -> str:
        """对字节列表进行加密操作"""
        bytes_str = StringProcessor.to_char_str(bytes_list)
        result_str = []
        index_b = self.big_array[1]
        initial_value = 0

        for index, char in enumerate(bytes_str):
            if index == 0:
                initial_value = self.big_array[index_b]
                sum_initial = index_b + initial_value
                self.big_array[1] = initial_value
                self.big_array[index_b] = index_b
            else:
                sum_initial = initial_value + value_e

            char_value = ord(char)
            sum_initial %= len(self.big_array)
            value_f = self.big_array[sum_initial]
            encrypted_char = char_value ^ value_f
            result_str.append(chr(encrypted_char))

            # 交换数组元素
            value_e = self.big_array[(index + 2) % len(self.big_array)]
            sum_initial = (index_b + value_e) % len(self.big_array)
            initial_value = self.big_array[sum_initial]
            self.big_array[sum_initial] = self.big_array[(index + 2) % len(self.big_array)]
            self.big_array[(index + 2) % len(self.big_array)] = initial_value
            index_b = sum_initial

        return "".join(result_str)

    def abogus_encode(self, abogus_bytes_str: str, selected_alphabet: int) -> str:
        """自定义Base64编码"""
        abogus = []
        for i in range(0, len(abogus_bytes_str), 3):
            if i + 2 < len(abogus_bytes_str):
                n = ((ord(abogus_bytes_str[i]) << 16) | (ord(abogus_bytes_str[i + 1]) << 8) | ord(abogus_bytes_str[i + 2]))
            elif i + 1 < len(abogus_bytes_str):
                n = (ord(abogus_bytes_str[i]) << 16) | (ord(abogus_bytes_str[i + 1]) << 8)
            else:
                n = ord(abogus_bytes_str[i]) << 16

            for j, k in zip(range(18, -1, -6), (0xFC0000, 0x03F000, 0x0FC0, 0x3F)):
                if j == 6 and i + 1 >= len(abogus_bytes_str):
                    break
                if j == 0 and i + 2 >= len(abogus_bytes_str):
                    break
                abogus.append(self.base64_alphabet[selected_alphabet][(n & k) >> j])

        abogus.append("=" * ((4 - len(abogus) % 4) % 4))
        return "".join(abogus)


class BrowserFingerprintGenerator:
    """简化的浏览器指纹生成器"""
    
    @staticmethod
    def generate_fingerprint(browser_type: str = "Edge") -> str:
        """生成浏览器指纹"""
        inner_width = random.randint(1024, 1920)
        inner_height = random.randint(768, 1080)
        outer_width = inner_width + random.randint(24, 32)
        outer_height = inner_height + random.randint(75, 90)
        screen_x = 0
        screen_y = random.choice([0, 30])
        avail_width = random.randint(1280, 1920)
        avail_height = random.randint(800, 1080)
        platform = "Win32"

        return (
            f"{inner_width}|{inner_height}|{outer_width}|{outer_height}|"
            f"{screen_x}|{screen_y}|0|0|{avail_width}|{avail_height}|"
            f"{avail_width}|{avail_height}|{inner_width}|{inner_height}|24|24|{platform}"
        )


class ABogus:
    """简化的ABogus参数生成器"""
    
    def __init__(self, fp: str = "", user_agent: str = ""):
        self.aid = 6383
        self.pageId = 0
        self.salt = "cus"
        self.options = [0, 1, 14]  # GET, POST, JSON
        
        self.character = "Dkdpgh2ZmsQB80/MfvV36XI1R45-WUAlEixNLwoqYTOPuzKFjJnry79HbGcaStCe"
        self.character2 = "ckdp1h4ZKsUB80/Mfvw36XIgR25+WQAlEi7NLboqYTOPuzmFjJnryx9HVGDaStCe"
        self.character_list = [self.character, self.character2]
        
        self.crypto_utility = CryptoUtility(self.salt, self.character_list)
        
        self.user_agent = (
            user_agent if user_agent and user_agent != ""
            else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
        )
        
        self.browser_fp = (
            fp if fp and fp != ""
            else BrowserFingerprintGenerator.generate_fingerprint("Edge")
        )
        
        self.sort_index = [
            18, 20, 52, 26, 30, 34, 58, 38, 40, 53, 42, 21, 27, 54, 55, 31, 35, 57, 39, 41, 43, 22, 28,
            32, 60, 36, 23, 29, 33, 37, 44, 45, 59, 46, 47, 48, 49, 50, 24, 25, 65, 66, 70, 71
        ]
        self.sort_index_2 = [
            18, 20, 26, 30, 34, 38, 40, 42, 21, 27, 31, 35, 39, 41, 43, 22, 28, 32, 36, 23, 29, 33, 37,
            44, 45, 46, 47, 48, 49, 50, 24, 25, 52, 53, 54, 55, 57, 58, 59, 60, 65, 66, 70, 71
        ]

    def generate_abogus(self, params: str, request: str = "") -> tuple:
        """生成ABogus参数"""
        ab_dir = {
            8: 3, 15: {"aid": self.aid, "pageId": self.pageId, "boe": False, "ddrt": 7, 
                      "paths": {"include": [{} for _ in range(7)], "exclude": []},
                      "track": {"mode": 0, "delay": 300, "paths": []}, "dump": True, "rpU": ""},
            18: 44, 19: [1, 0, 1, 5], 66: 0, 69: 0, 70: 0, 71: 0
        }

        start_encryption = int(time.time() * 1000)
        array1 = self.crypto_utility.params_to_array(self.crypto_utility.params_to_array(params))
        array2 = self.crypto_utility.params_to_array(self.crypto_utility.params_to_array(request))
        array3 = [212, 61, 87, 195, 104, 163, 124, 28, 92, 126, 187, 53, 218, 38, 254, 253, 252, 73, 83, 197, 194, 142, 113, 37, 9, 67, 166, 36, 56, 72, 56, 64]
        end_encryption = int(time.time() * 1000)

        # 插入时间戳
        ab_dir[20] = (start_encryption >> 24) & 255
        ab_dir[21] = (start_encryption >> 16) & 255
        ab_dir[22] = (start_encryption >> 8) & 255
        ab_dir[23] = start_encryption & 255
        ab_dir[24] = int(start_encryption / 256 / 256 / 256 / 256) >> 0
        ab_dir[25] = int(start_encryption / 256 / 256 / 256 / 256 / 256) >> 0

        # 插入请求配置
        ab_dir[26] = (self.options[0] >> 24) & 255
        ab_dir[27] = (self.options[0] >> 16) & 255
        ab_dir[28] = (self.options[0] >> 8) & 255
        ab_dir[29] = self.options[0] & 255
        ab_dir[30] = int(self.options[1] / 256) & 255
        ab_dir[31] = (self.options[1] % 256) & 255
        ab_dir[32] = (self.options[1] >> 24) & 255
        ab_dir[33] = (self.options[1] >> 16) & 255
        ab_dir[34] = (self.options[2] >> 24) & 255
        ab_dir[35] = (self.options[2] >> 16) & 255
        ab_dir[36] = (self.options[2] >> 8) & 255
        ab_dir[37] = self.options[2] & 255

        # 插入加密数据
        ab_dir[38] = array1[21]
        ab_dir[39] = array1[22]
        ab_dir[40] = array2[21]
        ab_dir[41] = array2[22]
        ab_dir[42] = array3[23]
        ab_dir[43] = array3[24]

        # 插入结束时间
        ab_dir[44] = (end_encryption >> 24) & 255
        ab_dir[45] = (end_encryption >> 16) & 255
        ab_dir[46] = (end_encryption >> 8) & 255
        ab_dir[47] = end_encryption & 255
        ab_dir[48] = ab_dir[8]
        ab_dir[49] = int(end_encryption / 256 / 256 / 256 / 256) >> 0
        ab_dir[50] = int(end_encryption / 256 / 256 / 256 / 256 / 256) >> 0

        # 插入固定值
        ab_dir[51] = (self.pageId >> 24) & 255
        ab_dir[52] = (self.pageId >> 16) & 255
        ab_dir[53] = (self.pageId >> 8) & 255
        ab_dir[54] = self.pageId & 255
        ab_dir[55] = self.pageId
        ab_dir[56] = self.aid
        ab_dir[57] = self.aid & 255
        ab_dir[58] = (self.aid >> 8) & 255
        ab_dir[59] = (self.aid >> 16) & 255
        ab_dir[60] = (self.aid >> 24) & 255

        # 插入浏览器指纹
        ab_dir[64] = len(self.browser_fp)
        ab_dir[65] = len(self.browser_fp)

        sorted_values = [ab_dir.get(i, 0) for i in self.sort_index]
        edge_fp_array = StringProcessor.to_ord_array(self.browser_fp)
        ab_xor = (len(self.browser_fp) & 255) >> 8 & 255

        for index in range(len(self.sort_index_2) - 1):
            if index == 0:
                ab_xor = ab_dir.get(self.sort_index_2[index], 0)
            ab_xor ^= ab_dir.get(self.sort_index_2[index + 1], 0)

        sorted_values.extend(edge_fp_array)
        sorted_values.append(ab_xor)

        abogus_bytes_str = StringProcessor.generate_random_bytes() + self.crypto_utility.transform_bytes(sorted_values)
        abogus = self.crypto_utility.abogus_encode(abogus_bytes_str, 0)
        params = f"{params}&a_bogus={abogus}"
        return params, abogus, self.user_agent


# if __name__ == "__main__":
    # 24/06/16 晚点开源自定义ua
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
    # url = "https://www.douyin.com/aweme/v1/web/aweme/detail/?"
    # params = "device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id=7380308675841297704&update_version_code=170400&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=125.0.0.0&browser_online=true&engine_name=Blink&engine_version=125.0.0.0&os_name=Windows&os_version=10&cpu_core_num=12&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7376294349792396827"
    # request = "GET"
    #
    # chrome_fp = BrowserFingerprintGenerator.generate_fingerprint("Chrome")
    # abogus = ABogus(user_agent=user_agent, fp=chrome_fp)
    # print(abogus.generate_abogus(params=params, request=request))

    # # 测试生成100个abogus参数 和 100个指纹所需时间
    # start = time.time()
    # for _ in range(100):
    #     abogus.generate_abogus(params=params, request=request)
    # end = time.time()
    # print("生成100个abogus参数和指纹所需时间:", end - start)  # 生成100个abogus参数和指纹所需时间: 2.203000783920288

    # start = time.time()
    # for _ in range(100):
    #     BrowserFingerprintGenerator.generate_fingerprint("Chrome")
    # end = time.time()
    # print("生成100个指纹所需时间:", end - start)  # 生成100个指纹所需时间: 0.00400090217590332


class douyinDownloader:
    # 检测是否为Android系统
    @staticmethod
    def is_android():
        """检测是否为Android系统"""
        return os.path.exists('/system/build.prop') or 'ANDROID_ROOT' in os.environ

    # 初始化
    def __init__(self):
        # 根据系统设置User-Agent
        if self.is_android():
            user_agent = 'Mozilla/5.0 (Linux; Android 11; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
        else:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
        
        self.headers = {
            'user-agent': user_agent,
            'referer': 'https://www.douyin.com/',
            'Cookie': 'ttwid=1%7CAG25HBrn0oFWg1_l0IYs59Q0hF9ehKFyBpQqn_aga3s%7C1718182905%7C2070d8e77618180759d841e4cb1ecb5aeee0ea2b51c155d49e72fac109bdcf35; my_rd=2; d_ticket=3c1dba76f0dcc8fb1ef1977e831deccb9c78b; n_mh=aPIs8xaRtR3B_zHGw2ftRJqrGDuyul4EWlN5pPpc7qo; store-region=cn-sc; store-region-src=uid; UIFID_TEMP=3c3e9d4a635845249e00419877a3730e2149197a63ddb1d8525033ea2b3354c2d034cdad383062616043932af89f3b20e62ccae8688abb9a0ffe0ed36195be02f9b61df1d615cbf20316f05dd0be3c76; fpk1=U2FsdGVkX19SWd5bq85yqh0+Kc9IqnHKC3pOdRR40JWRfqSQJulsPp5fTQuCxk587ZuRjPPMH88wtb+E4ojjGw==; fpk2=f1f6b29a6cc1f79a0fea05b885aa33d0; UIFID=3c3e9d4a635845249e00419877a3730e2149197a63ddb1d8525033ea2b3354c2d034cdad383062616043932af89f3b20727531bfa3d3cc0b327796376e670ce1ac61f7402fea653f88f334994436e3ce2ac34eb09be65bd4b974b630350149c052a53eea444e554e17a1a22f916430cfce239d3f07001ee34971cbb9f51a6229bb698c57fb3c497289b2fbef59d72f084e6df4400970ffabefaf6327cf23a163; __ac_nonce=06710dd0a0035ce58b4a8; __ac_signature=_02B4Z6wo00f01Nq.ojwAAIDDqriTdXXrkyTan6aAAFHE17; s_v_web_id=verify_m2d49wod_qTywt3sq_opDq_400u_Acat_ncM66TzjeauW; hevc_supported=true; dy_swidth=2560; dy_sheight=1440; csrf_session_id=cb92b555e16c0e96f8243c8e1e28045c; passport_csrf_token=622a71b7094ec94f76860dc302ffb0a5; passport_csrf_token_default=622a71b7094ec94f76860dc302ffb0a5; strategyABtestKey=%221729158419.703%22; is_staff_user=false; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A2560%2C%5C%22screen_height%5C%22%3A1440%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A16%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A9.7%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A100%7D%22; bd_ticket_guard_client_web_domain=2; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; passport_mfa_token=CjUS74P9fQGGa36yxPX2um8%2BOLGhddLDw%2FcebBChnwLquBkuTgEQN4PV%2BnHP8p4I%2FCKzHJbGfRpKCjya%2B2HOMp0wfmIFpkEJcw7uUT%2Btnt0EjNn6XITFB1l0gfxlCGr16uFa6ltHRzihVskcsxckLeEcwrx9cIMQtP3eDRj2sdFsIAIiAQPZLUvy; biz_trace_id=8000aa6a; passport_assist_user=Cj1VIZllBU6a_eCr8131A-N0gmBhcTgo-L0K8EG_NPoyNqd1hsNccKKVoRI3mrQgytFo5FgApkrXMR-cEUplGkoKPBGfC-MKmR4_2iScJA5Pdk2RVdY9rY_E0clempONfef1zqWvcwb0GOInMfXN5TQ83Mka_7nKFpjSUBnSPRCy_t4NGImv1lQgASIBA1vi6FE%3D; sso_uid_tt=25ec3306acaa6c17973c16ff2fa86a76; sso_uid_tt_ss=25ec3306acaa6c17973c16ff2fa86a76; toutiao_sso_user=af2cea8ff77f9534d7616324d9f09f7f; toutiao_sso_user_ss=af2cea8ff77f9534d7616324d9f09f7f; sid_ucp_sso_v1=1.0.0-KDNjZWMzZTMxMWEwZDM0NmYyM2ZhNGZkMjExMjAwZDk4ZjQwZjQ1YmMKHwiX_ruh-AIQsbrDuAYY7zEgDDDdxtfZBTgFQPsHSAYaAmxxIiBhZjJjZWE4ZmY3N2Y5NTM0ZDc2MTYzMjRkOWYwOWY3Zg; ssid_ucp_sso_v1=1.0.0-KDNjZWMzZTMxMWEwZDM0NmYyM2ZhNGZkMjExMjAwZDk4ZjQwZjQ1YmMKHwiX_ruh-AIQsbrDuAYY7zEgDDDdxtfZBTgFQPsHSAYaAmxxIiBhZjJjZWE4ZmY3N2Y5NTM0ZDc2MTYzMjRkOWYwOWY3Zg; uid_tt=c6ffbadd708e805e9d15019894e6710c; uid_tt_ss=c6ffbadd708e805e9d15019894e6710c; sid_tt=f945d0d8a24ac11cb85f1f1b29dcc64f; sessionid=f945d0d8a24ac11cb85f1f1b29dcc64f; sessionid_ss=f945d0d8a24ac11cb85f1f1b29dcc64f; IsDouyinActive=true; SelfTabRedDotControl=%5B%5D; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA0mql-gtOiN9GVwlQ8VSBy3cf-etmG7Fcn2nnA55XRkY%2F1729180800000%2F0%2F1729158455273%2F0%22; home_can_add_dy_2_desktop=%221%22; passport_fe_beating_status=true; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=6c4031f93280411e0028645bc31233df; __security_server_data_status=1; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCR3hpVzFhM2ZRQTF2b3F2TTNhY3RTV2phL2FadEphRzAzbHRXZlBOMEd3R0FXMFJadlNNWUZ1TUdDY1JJK3N6SzE3WjFlY3hlbVI0MFFyZUlaWHNBc0k9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoyfQ%3D%3D; publish_badge_show_info=%220%2C0%2C0%2C1729158456816%22; odin_tt=bf035b8e79cb3198e865ba81fed2c0d09ab43a118c16305a68129bb7f5e909f26e3875e8ab7ec996e4ba284d21150de1; sid_guard=f945d0d8a24ac11cb85f1f1b29dcc64f%7C1729158456%7C5183996%7CMon%2C+16-Dec-2024+09%3A47%3A32+GMT; sid_ucp_v1=1.0.0-KDRjZTI5MTExYzM5YzY2MmRjN2Y3Nzg3MzBjNDRlZmNjOWI1MTAyYWIKGQiX_ruh-AIQuLrDuAYY7zEgDDgFQPsHSAQaAmxmIiBmOTQ1ZDBkOGEyNGFjMTFjYjg1ZjFmMWIyOWRjYzY0Zg; ssid_ucp_v1=1.0.0-KDRjZTI5MTExYzM5YzY2MmRjN2Y3Nzg3MzBjNDRlZmNjOWI1MTAyYWIKGQiX_ruh-AIQuLrDuAYY7zEgDDgFQPsHSAQaAmxmIiBmOTQ1ZDBkOGEyNGFjMTFjYjg1ZjFmMWIyOWRjYzY0Zg'
            # 'Cookie': 'ttwid=%s; '
            #           'passport_csrf_token=1ee41c8a38f52bef28e7d877c15422a3; '
            #           'passport_csrf_token_default=1ee41c8a38f52bef28e7d877c15422a3; '
            #           'msToken=%s;' % (self.generate_ttwid(), self.generate_random_string(107))
        }

        # 根据操作系统设置保存路径
        import os
        if os.name == 'nt':  # Windows系统
            self.save = 'D:\\Download\\'
            self.separator = '\\'
            print('检测到Windows系统，下载目录: D:\\Download\\')
        elif self.is_android():  # Android系统
            self.save = '/sdcard/Download/'
            self.separator = '/'
            print('检测到Android系统，下载目录: /sdcard/Download/')
        else:  # 其他系统 (Linux/macOS)
            self.save = os.path.join(os.getcwd(), 'Download')
            self.separator = '/'
            print(f'检测到非Windows/Android系统，下载目录: {self.save}')
        self.download_info = 'download_info.json'
        self.dir_path = ''
        self.mode = 'post'
        self.nickname = ''
        self.signature = ''
        self.avatar_url = ''
        self.max_cursor = 0  # 请求的游标，首次为0，以后每次请求带上上次请求返回的max_cursor
        self.has_more = True
        self.domain = 'https://www.douyin.com/aweme/v1/web/'
        self.request_params = 'device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Edge&browser_version=122.0.0.0&browser_online=true&engine_name=Blink&engine_version=122.0.0.0&os_name=Windows&os_version=10&cpu_core_num=12&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=100'
        self.mix_sec_uid = ''
        self.mix_name = ''
        self.is_mix = False

    # 匹配粘贴的url地址
    @staticmethod
    def find_url(string):
        # findall() 查找匹配正则表达式的字符串
        url = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
        return url[0]

    def get_params_with_xbogus(self, url):
        get_xbogus_path = 'http://127.0.0.1:8889/xg/path?url='
        url = url.replace('&', '%26')
        post_url = get_xbogus_path + url
        # print(post_url)
        response = json.loads(requests.post(post_url, headers=self.headers).text)
        # print(response['result'][0]['paramsencode'])
        return response['result'][0]['paramsencode']

    def get_params_with_abogus(self, params):
        browser_fp = BrowserFingerprintGenerator.generate_fingerprint('Edge')
        abogus = ABogus(fp=browser_fp, user_agent=self.headers.get('user-agent')).generate_abogus(params)
        return abogus[0]

    @staticmethod
    def generate_ttwid():
        url = 'https://ttwid.bytedance.com/ttwid/union/register/'
        data = '{"region":"cn","aid":1768,"needFid":false,"service":"www.ixigua.com","migrate_info":{"ticket":"","source":"node"},"cbUrlProtocol":"https","union":true}'
        response = requests.request('POST', url, data=data)
        # print(response.cookies.get('ttwid'))
        return response.cookies.get('ttwid')

    @staticmethod
    def generate_random_string(length):
        letters = string.ascii_letters + string.digits + '='
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def convert_seconds(seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return '%d分%.2f秒' % (int(minutes), seconds)

    # 替换非法字符
    @staticmethod
    def clean_str(string):
        r = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        # 替换为下划线
        new = re.sub(r, "_", string)
        return new

    @staticmethod
    def convert_size(size):
        k, m = 1024, 1024*1024
        if size >= m:
            return str(round(size / m, 2)) + 'MB'
        else:
            return str(round(size / k, 2)) + 'KB'

    @staticmethod
    def cut_item_desc(desc):
        # Code From RobotJohns https://github.com/RobotJohns
        # 移除文件名称  /r/n
        desc = '.'.join(desc.splitlines())
        if len(desc) > 60:
            print("文件名称太长，进行截取...")
            print(desc)
            desc = desc[0:60]
            print(f"截取后的文案：{desc}")
        return desc

    @staticmethod
    def read_json_file(file_location):
        with open(file_location, 'r', encoding='utf-8') as f:
            content = json.load(f)
        f.close()
        return content

    @staticmethod
    def write_json_file(file_location, dict_data):
        with open(file_location, 'w', encoding='utf-8') as f:
            json.dump(dict_data, f, ensure_ascii=False, indent=4)
        f.close()

    def update_json_file(self, file_location, key, value):
        data = self.read_json_file(file_location)
        data[key] = value
        self.write_json_file(file_location, data)

    @staticmethod
    def verify_url(url):
        print('正在分析输入的链接，请稍等...')
        r = requests.get(url)
        real_url = r.request.url
        # print(real_url)
        if 'user/' in real_url:
            sec_uid = real_url.split('user/', 1)[1].split('?', 1)[0].replace('/', '')
            url_type = 'homepage'
            return url_type, sec_uid
        elif 'video/' in real_url:
            video_aweme_id = real_url.split('video/', 1)[1].split('?', 1)[0].replace('/', '')
            url_type = 'video'
            return url_type, video_aweme_id
        elif 'note/' in real_url:
            url_type = 'note'
            note_aweme_id = real_url.split('note/', 1)[1].split('?', 1)[0].replace('/', '')
            return url_type, note_aweme_id
        elif 'live.' in real_url:
            url_type = 'live1'
            web_rid = real_url.split('/')[-1].split('?', 1)[0]
            return url_type, web_rid
        elif 'webcast' in real_url:
            url_type = 'live2'
            params = real_url.split('reflow/')[-1]
            room_id = params.split('?')[0]
            sec_uid = re.search(r'sec_user_id=([\w\d_\-]+)&', params).group(1)
            return url_type, [room_id, sec_uid]
        elif 'collection' in real_url:
            url_type = 'collection'
            collection_id = real_url.split('collection/', 1)[1].split('?', 1)[0].replace('/', '')
            return url_type, collection_id
        else:
            print('你输入的链接有误，请检查！')
            sys.exit()

    # 获取数据
    def get_all_items(self, sec_uid_or_mix_id):
        request_page = 1
        item_list = []
        while self.has_more:
            if self.is_mix:
                print(f'正在查找合集作品: 第 {request_page} 页...')
            elif self.mode == 'post':
                print(f'正在查找作者发布的作品: 第 {request_page} 页...')
            else:
                print(f'正在查找作者喜欢的作品: 第 {request_page} 页...')
            json_data, request_url = self._get_one_page_items(sec_uid_or_mix_id)
            
            # 检查返回的数据结构
            if 'aweme_list' not in json_data:
                # 如果status_code为0但没有aweme_list，说明已到达最后一页
                if json_data.get('status_code') == 0:
                    print(f'第 {request_page} 页没有更多作品数据，已到达最后一页')
                    break
                else:
                    print(f'API返回数据格式异常，缺少aweme_list字段')
                    print(f'返回的数据结构：{list(json_data.keys())}')
                    print(f'返回的完整数据：{json_data}')
                    print(f'当前请求链接为：{request_url}')
                    sys.exit()
            
            # 检查是否有作品数据
            if not json_data['aweme_list'] or len(json_data['aweme_list']) == 0:
                print(f'第 {request_page} 页没有找到作品数据')
                break
            
            if 'max_cursor' in json_data:
                self.max_cursor = json_data['max_cursor']
            elif 'cursor' in json_data:
                self.max_cursor = json_data['cursor']
            else:
                print(f'第 {request_page} 页返回数据中缺少游标信息，可能已到达最后一页')
                break
                
            self.has_more = json_data.get('has_more', False)
            item_list += json_data['aweme_list']
            request_page += 1
        item_count = len(item_list)
        print(f'总共获取到 {item_count} 部作品。')
        if item_count == 0:
            print('该作者未发布任何作品，请检查输入的链接！')
            sys.exit()
        return item_list

    def make_get_request(self, request_url, headers=None):
        # print(request_url)
        if headers is None:
            headers = self.headers
        response = requests.get(url=request_url, headers=headers)
        while response.text == '' or response.status_code != 200:
            print('获取数据失败，正在重新获取...')
            time.sleep(3)
            response = requests.get(url=request_url, headers=headers)
        
        try:
            json_data = json.loads(response.content.decode('utf-8'))
        except json.JSONDecodeError as e:
            print(f'JSON解析失败: {e}')
            print(f'响应内容: {response.text[:500]}...')
            sys.exit()
        
        # 检查API是否返回错误
        if 'status_code' in json_data and json_data.get('status_code') != 0:
            print(f'API返回错误，状态码: {json_data.get("status_code")}')
            print(f'错误信息: {json_data.get("status_msg", "未知错误")}')
            print(f'请求URL: {request_url}')
            return json_data  # 返回错误数据，让上层处理
        
        # json_formatted_str = json.dumps(json_data, indent=4, ensure_ascii=False)
        # print(json_formatted_str)
        return json_data

    def _get_one_page_items(self, sec_uid_or_mix_id):
        if not self.is_mix:
            sec_uid = sec_uid_or_mix_id
            request_params = f'sec_user_id={sec_uid}&count=35&max_cursor={self.max_cursor}&' + self.request_params
            params_with_abogus = self.get_params_with_abogus(request_params)
            if self.mode == 'post':
                request_url = self.domain + 'aweme/post/?' + params_with_abogus
            else:
                request_url = self.domain + 'aweme/favorite/?' + params_with_abogus
        else:
            collection_id = sec_uid_or_mix_id
            request_params = f'mix_id={collection_id}&cursor={self.max_cursor}&count=35&' + self.request_params
            params_with_abogus = self.get_params_with_abogus(request_params)
            request_url = self.domain + 'mix/aweme/?' + params_with_abogus
        json_data = self.make_get_request(request_url)
        return json_data, request_url

    @staticmethod
    def get_stream_url_from_json(json_data, web_rid=None):
        status = json_data['status']
        if status == 4:
            print('NOT living now, quit!')
            sys.exit()
        else:
            print('Living now, getting stream url...')
        host_name = json_data['owner']['nickname']
        live_url = json_data['stream_url']['hls_pull_url_map']
        if web_rid is None:
            web_rid = json_data['owner']['web_rid']
        name_and_id = host_name + '_' + web_rid
        if 'FULL_HD1' in live_url:
            return name_and_id, live_url['FULL_HD1']
        elif 'HD1' in live_url:
            return name_and_id, live_url['HD1']
        else:
            print('No high definition steaming, quit!')
            sys.exit()

    def get_by_room_id(self, room_id, sec_uid):
        requests_params = f'verifyFp=verify_lk07kv74_QZYCUApD_xhiB_405x_Ax51_GYO9bUIyZQVf&type_id=0&live_id=1&room_id={room_id}&sec_user_id={sec_uid}&app_id=1128'
        params_with_abogus = self.get_params_with_abogus(requests_params)
        request_url = 'https://webcast.amemv.com/webcast/room/reflow/info/?' + params_with_abogus
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Cookie': 's_v_web_id=verify_lk07kv74_QZYCUApD_xhiB_405x_Ax51_GYO9bUIyZQVf'
        }
        json_data = self.make_get_request(request_url, headers)
        # json_formatted_str = json.dumps(json_data, indent=4, ensure_ascii=False)
        # print(json_formatted_str)
        json_info = json_data['data']['room']
        return self.get_stream_url_from_json(json_info)

    def get_by_web_rid(self, web_rid):
        request_params = f'aid=6383&device_platform=web&web_rid={web_rid}'
        params_with_abogus = self.get_params_with_abogus(request_params)
        request_url = 'https://live.douyin.com/webcast/room/web/enter/?' + params_with_abogus
        json_data = self.make_get_request(request_url)
        json_info = json_data['data']['data'][0]
        return self.get_stream_url_from_json(json_info, web_rid)

    @staticmethod
    def get_items_ids(item_list):
        item_ids = []
        for i in range(len(item_list)):
            item_ids.append(item_list[i]['aweme_id'])
        return sorted(item_ids)

    def get_mix_info(self, mix_id):
        response, _ = self._get_one_page_items(mix_id)
        author_info = response['aweme_list'][0]['author']
        self.nickname = author_info['nickname']
        self.signature = author_info['signature']
        self.avatar_url = author_info['avatar_thumb']['url_list'][0].replace('100x100', '1080x1080')
        self.mix_sec_uid = author_info['sec_uid']
        self.mix_name = response['aweme_list'][0]['mix_info']['mix_name']

    def get_author_info(self, sec_uid):
        request_params = f'sec_user_id={sec_uid}&' + self.request_params
        params_with_abogus = self.get_params_with_abogus(request_params)
        request_url = self.domain + 'user/profile/other/?' + params_with_abogus
        json_data = self.make_get_request(request_url)
        # print(json_data)
        author_info = json_data['user']
        self.nickname = author_info['nickname']
        self.signature = author_info['signature']
        self.avatar_url = author_info['avatar_larger']['url_list'][0]

    def get_item_info(self, item_id):
        request_params = f'aweme_id={item_id}&' + self.request_params
        params_with_abogus = self.get_params_with_abogus(request_params)
        request_url = self.domain + 'aweme/detail/?' + params_with_abogus
        # print(request_url)
        res = requests.get(url=request_url, headers=self.headers).text
        if res is None or res == '':
            print(f'Response of url {request_url} is: {res}, exit!')
            sys.exit()
        else:
            response = json.loads(res)
            item = response['aweme_detail']
            # print(response)
            desc = item['desc'] if item['desc'] is not None else ''
            create_time = time.strftime("%Y-%m-%d_%H.%M.%S", time.localtime(item['create_time']))
            author_name = item['author']['nickname']
            if item['images'] is None:
                item_type = 'video'
                video_url = item['video']['bit_rate'][0]['play_addr']['url_list'][0]
                return item_type, video_url, create_time, desc, author_name
            else:
                item_type = 'image'
                image_urls = []
                for i in range(len(item['images'])):
                    image_urls.append(item['images'][i]['url_list'][0])
                return item_type, image_urls, create_time, desc, author_name

    def make_dirs(self):
        if self.is_mix:
            self.dir_path = os.path.join(self.save, self.clean_str(self.nickname) + '-' + self.clean_str(self.mix_name))
        elif self.mode == 'post':
            self.dir_path = os.path.join(self.save, self.clean_str(self.nickname))
        else:
            self.dir_path = os.path.join(self.save, self.clean_str(self.nickname) + '_like')
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def download(self, download_url, save_location, item_id):
        request = requests.get(url=download_url, headers=self.headers, stream=True)
        content_length = int(request.headers.get('content-length', 0))
        number = 0
        while (request.status_code != 200 or content_length < 1000) and number < 10:
            print(f'文件获取失败，重试 {number+1} 次')
            request = requests.get(url=download_url, headers=self.headers, stream=True)
            content_length = int(request.headers.get('content-length', 0))
            number += 1
        
        file_size = self.convert_size(content_length)
        if content_length > 0:
            downloaded_size = 0
            with open(save_location, 'wb') as file:
                for chunk in request.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        # 显示下载进度
                        progress = (downloaded_size / content_length) * 100
                        print(f'\r[下载中]: {file_size} - {progress:.1f}%', end='', flush=True)
            print(f'\n[下载完成]: 文件大小为: {file_size}\n')
        else:
            print(f'[下载失败！]: 文件大小为: {file_size}\n文件id为：{item_id}\n')

    def download_stream_video(self, name_and_id, stream_url, max_count=10000, max_size=500*1024*1024):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
        start_time = time.strftime("%Y%m%d_%H%M%S")
        filename = name_and_id + '_' + start_time + '.ts'
        max_id = None
        size = 0
        for i in range(1, max_count + 1):
            playlist = m3u8.load(uri=stream_url, headers=headers)
            for seg in playlist.segments:
                current_id = seg.uri.split('.ts')[0].split('-')[-1]
                if max_id and current_id <= max_id:
                    continue
                with open(os.path.join(self.save, filename), "ab" if max_id else "wb") as f:
                    r = requests.get(url=seg.absolute_uri, headers=headers)
                    size += int(r.headers['content-length'])
                    f.write(r.content)
                    print(f"\r第 {i} 次请求该直播的m3u8链接，已下载：{size / 1024 / 1024:.2f}MB。", end="")
                    if size >= max_size:
                        print("\n文件已经超过大小限制，下载结束！")
                        return
                max_id = current_id
            time.sleep(2)

    @staticmethod
    def get_m3u8_info(url):
        playlist = m3u8.load(uri=url)
        # print(playlist.keys)
        # print(type(playlist.segments))
        # print(playlist.data)
        for seg in playlist.segments:
            print(seg)
            print('*' * 20)

    def init_download_info_file(self, input_url, sec_uid_or_mix_id):
        download_info_file = os.path.join(self.dir_path, self.download_info)
        if not os.path.exists(download_info_file):
            if not self.is_mix:
                download_info = {'homepage': input_url,
                                 'sec_uid': sec_uid_or_mix_id,
                                 'nickname': self.nickname,
                                 'signature': self.signature,
                                 'avatar': self.avatar_url,
                                 'download_mode': self.mode,
                                 'downloaded_items': []
                                 }
            else:
                download_info = {'mix_page': input_url,
                                 'mix_id': sec_uid_or_mix_id,
                                 'sec_uid': self.mix_sec_uid,
                                 'nickname': self.nickname,
                                 'signature': self.signature,
                                 'avatar': self.avatar_url,
                                 'mix_name': self.mix_name,
                                 'downloaded_items': []
                                 }
            self.write_json_file(download_info_file, download_info)
        else:
            pass

    def get_latest_update_items(self, folder):
        self.dir_path = folder
        print(f'正在对文件夹 {folder} 进行更新...')
        json_file = os.path.join(self.dir_path, self.download_info)
        if os.path.exists(json_file):
            data = self.read_json_file(json_file)
            if 'mix_id' in data:
                sec_uid_or_mix_id = data['mix_id']
                self.is_mix = True
            elif 'sec_uid' in data and 'download_mode' in data:
                sec_uid_or_mix_id = data['sec_uid']
                self.mode = data['download_mode']
            else:
                print('json文件中找不到作者的sec_uid, 可以通过输入作者主页链接进行更新！\n')
                return
            downloaded_items = data['downloaded_items']
            request_page = 1
            item_list = []
            item_already_downloaded = False
            while not item_already_downloaded and self.has_more:
                print(f'正在查找第 {request_page} 页新作品...')
                json_data, request_url = self._get_one_page_items(sec_uid_or_mix_id)
                if 'max_cursor' in json_data and len(json_data['aweme_list']) > 0:
                    self.max_cursor = json_data['max_cursor']
                elif 'cursor' in json_data and len(json_data['aweme_list']) > 0:
                    self.max_cursor = json_data['cursor']
                else:
                    print('获取作品失败，请检查请求链接！')
                    print(f'当前请求链接为：{request_url}')
                    break
                item_list += json_data['aweme_list']
                last_id_in_request = item_list[-1]['aweme_id']
                request_page += 1
                self.has_more = json_data['has_more']
                if last_id_in_request in downloaded_items:
                    item_already_downloaded = True
            item_ids = self.get_items_ids(item_list)
            items_to_download = list(set(item_ids) - set(downloaded_items))
            self.has_more = True
            self.is_mix = False
            return sorted(items_to_download)
        else:
            print('输入的文件夹中找不到json文件, 可以通过输入作者主页链接进行更新！\n')
            return

    def get_items_to_download(self, sec_uid_or_mix_id):
        if not self.is_mix:
            self.get_author_info(sec_uid_or_mix_id)
            mode = input('输入的链接为作者主页，输入 2 下载作者喜欢的作品，输入1或直接回车下载作者发布的作品：')
            if mode == '2':
                self.mode = 'like'
                print(f'下面将下载 {self.nickname} 喜欢的所有作品...')
            else:
                print(f'下面将下载 {self.nickname} 发布的所有作品...')
        else:
            self.get_mix_info(sec_uid_or_mix_id)
            print(f'下面将下载合集中的所有作品到 {self.nickname}-{self.mix_name}...')
        self.make_dirs()
        download_info_file = os.path.join(self.dir_path, self.download_info)
        if os.path.exists(download_info_file):
            items_to_download = self.get_latest_update_items(self.dir_path)
        else:
            item_list = self.get_all_items(sec_uid_or_mix_id)
            items_to_download = self.get_items_ids(item_list)
        if len(items_to_download) == 0:
            print('查找到的所有作品均已下载，当前无新作品，跳过...')
            return
        else:
            return items_to_download

    def multi_download(self, items_to_download):
        items_count = len(items_to_download)
        print(f'本次将下载 {items_count} 部新作品到: {self.dir_path}\n')
        if items_count:
            download_info_file = os.path.join(self.dir_path, self.download_info)
            items_temp = []
            for i in range(0, items_count):
                print(f'正在下载第 {i+1}/{items_count} 个作品...')
                item_id = items_to_download[i]
                item_type, unknown, create_time, desc, author_name = self.get_item_info(item_id)
                if item_type == 'video':
                    video_url = unknown
                    if self.mode == 'post':
                        self.video_download(self.dir_path, create_time, desc, video_url, item_id)
                    else:
                        self.video_download(self.dir_path, create_time, author_name + '_' + desc, video_url, item_id)
                elif item_type == 'image':
                    url_list = unknown
                    if self.mode == 'post':
                        self.image_download(self.dir_path, create_time, desc, url_list, item_id)
                    else:
                        self.image_download(self.dir_path, create_time, author_name + '_' + desc, url_list, item_id)
                items_temp.append(items_to_download[i])
                if (i+1) % 5 == 0:
                    downloaded_items = self.read_json_file(download_info_file)['downloaded_items']
                    self.update_json_file(download_info_file, 'downloaded_items', (items_temp + downloaded_items))
                    items_temp = []
            downloaded_items = self.read_json_file(download_info_file)['downloaded_items']
            self.update_json_file(download_info_file, 'downloaded_items', (items_temp + downloaded_items))

    def video_download(self, folder, create_time, file_name, video_url, item_id):
        video_name = create_time + '_' + self.cut_item_desc(self.clean_str(file_name)) + '.mp4'
        save_location = os.path.join(folder, video_name)
        if not os.path.exists(save_location):
            print(f'[开始下载]: {video_name}...')
            self.download(video_url, save_location, item_id)
        else:
            print(f'文件 {video_name} 已存在，跳过...')

    def image_download(self, folder, create_time, file_name, url_list, item_id):
        for i in range(len(url_list)):
            image_name = create_time + '_' + self.cut_item_desc(self.clean_str(file_name)) + '_' + str(i + 1) + '.jpg'
            save_location = os.path.join(folder, image_name)
            download_link = url_list[i]
            if not os.path.exists(save_location):
                print(f'[开始下载]: {image_name}...')
                self.download(download_link, save_location, item_id)
            else:
                print(f'文件 {image_name} 已存在，跳过...')

    def main_flow(self):
        input_str = input('-> 直接回车，将对Download文件夹下所有已存在文件夹进行更新\n'
                          '-> 输入已存在的下载文件夹路径可对文件夹进行更新\n'
                          '-> 输入抖音作者主页链接（不需要去除无效字符）可下载作者发布的全部作品\n'
                          '-> 输入单个作品链接（不需要去除无效字符）可直接下载该作品\n').replace('"', '')
        start = time.time()
        if input_str == '':
            print('无输入，将对Download文件夹下所有已存在文件夹进行更新...')
            for path in os.scandir(self.save):
                if path.is_dir():
                    items_to_download = self.get_latest_update_items(path.path)
                    if items_to_download is not None:
                        self.multi_download(items_to_download)
                        self.max_cursor = 0
                    else:
                        continue
        elif os.path.isdir(input_str):
            print('输入的为已下载文件夹路径，将查找并下载最新的作品...')
            items_to_download = self.get_latest_update_items(input_str)
            self.multi_download(items_to_download)
        else:
            url = self.find_url(input_str)
            url_type, unknown_id = self.verify_url(url)
            if url_type == 'homepage':
                # print('输入链接为作者主页, 将下载作者发布的所有作品...')
                sec_uid = unknown_id
                items_to_download = self.get_items_to_download(sec_uid)
                if items_to_download:
                    self.init_download_info_file(url, sec_uid)
                    self.multi_download(items_to_download)

            elif url_type == 'video':
                print(f'输入链接为单个视频链接, 下载到: {self.save}')
                video_id = unknown_id
                _, video_url, create_time, desc, author_name = self.get_item_info(video_id)
                self.video_download(self.save, create_time, author_name + '_' + desc, video_url, video_id)

            elif url_type == 'note':
                print(f'输入链接为一个图片作品, 下载到: {self.save}')
                image_id = unknown_id
                _, image_urls, create_time, desc, author_name = self.get_item_info(image_id)
                self.image_download(self.save, create_time, author_name + '_' + desc, image_urls, image_id)

            elif url_type == 'collection':
                print('输入链接为一个合集, 将下载合集中的所有作品...')
                self.is_mix = True
                mix_id = unknown_id
                items_to_download = self.get_items_to_download(mix_id)
                self.init_download_info_file(url, mix_id)
                self.multi_download(items_to_download)
                self.is_mix = False
            elif url_type == 'live1':
                web_rid = unknown_id
                name_and_id, stream_url = self.get_by_web_rid(web_rid)
                self.download_stream_video(name_and_id, stream_url)
            elif url_type == 'live2':
                room_id = unknown_id[0]
                sec_uid = unknown_id[1]
                name_and_id, stream_url = self.get_by_room_id(room_id, sec_uid)
                self.download_stream_video(name_and_id, stream_url)

        end = time.time()
        print('\n完成！总耗时: %s' % self.convert_seconds(end-start))


# 主模块执行
if __name__ == "__main__":
    # test_url = '长按复制此条消息，打开抖音搜索，查看TA的更多作品。 https://v.douyin.com/6PfoWH8/'
    # 新建实例
    dd = douyinDownloader()
    dd.main_flow()
    # print(dd.get_by_web_rid('234666557566'))
    # dd.get_m3u8_info('http://pull-hls-l11.douyincdn.com/third/stream-691323759338455516_or4.m3u8?expire=1712210189&sign=55f0ce8ee57dbdf5c8719100c2959aba')
    # dd.get_author_info('MS4wLjABAAAAJlkP08ipW2Yr08E7HHg7nEinZJyRwRf_y9OrOsgXjsQvNvkl3g0URuvS-7TLjmgk')
    # dd.get_item_info('7221097242948619558')
    # dd.get_collection_info('7093490319085307918')
