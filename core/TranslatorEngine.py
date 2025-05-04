'''
负责翻译文本
'''
import time

import googletrans
# TranslatorEngine.py
# 翻译模块，调用googletrans库

from googletrans import Translator

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
            print(f"Translation took {elapsed_time:.2f} seconds")
            return result.text
        except Exception as e:
            # 出错返回提示
            return f"翻译失败: {str(e)}"
