'''
负责翻译文本
'''
import hashlib
import logging
import os
import time
import uuid

import googletrans
import requests
# TranslatorEngine.py
# 翻译模块，调用googletrans库

from googletrans import Translator

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    """截断函数：用于签名"""
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[:10] + str(size) + q[-10:]

class TranslatorEngine:
    def __init__(self):
        self.translator = Translator()

    def translate(self, text, src='en', dest='zh-cn'):
        try:
            # 调用Google Translate进行翻译
            # result = self.translator.translate(text, src=src, dest=dest)
            start_time = time.time()
            # print(f"Translating text: {text} from {src} to {dest}")
            result = self.translator.translate(text, src=src, dest=dest)
            elapsed_time = time.time() - start_time
            logging.info(f"Translation took {elapsed_time:.2f} seconds")
            return result.text
        except Exception as e:
            # 出错返回提示
            return f"translation failure: {str(e)}"



    ########### 有道翻译 ##############

    def youdao_translate(self, query, src='en', dest='zh-cn'):
        appKey = os.getenv('YOUDAO_APP_KEY', '')  # Get AppKey from environment variable
        appSecret = os.getenv('YOUDAO_APP_SECRET', '')  # Get AppSecret from environment variable
        if not appKey or not appSecret:
            raise ValueError("YOUDAO_APP_KEY and YOUDAO_APP_SECRET environment variables must be set")
        url = 'https://openapi.youdao.com/api'

        salt = str(uuid.uuid4())
        curtime = str(int(time.time()))
        signStr = appKey + truncate(query) + salt + curtime + appSecret
        sign = encrypt(signStr)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'q': query,
            'from': src,
            'to': dest,
            'appKey': appKey,
            'salt': salt,
            'sign': sign,
            'signType': 'v3',
            'curtime': curtime,
        }

        response = requests.post(url, data=data, headers=headers)
        result = response.json()

        # 提取翻译结果
        translation = result.get('translation', [])
        return translation[0] if translation else "翻译失败"
