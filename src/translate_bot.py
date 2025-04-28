import discord
import requests
import os

# Discord Bot Token
DISCORD_TOKEN='you api key'


# DeepL API 配置（可以换成自己喜欢的翻译 API）
DEEPL_API_URL = 'https://api-free.deepl.com/v2/translate'
DEEPL_API_KEY = '你的 DeepL API Key'  # 注意用自己的key！

# 设置 Discord Intents
intents = discord.Intents.default()
intents.message_content = True  # 开启读取消息内容的权限
client = discord.Client(intents=intents)

# 翻译函数
def translate_text(text, target_lang='ZH'):
    response = requests.post(
        DEEPL_API_URL,
        data={
            'auth_key': DEEPL_API_KEY,
            'text': text,
            'target_lang': target_lang
        }
    )
    if response.status_code == 200:
        result = response.json()
        return result['translations'][0]['text']
    else:
        print('翻译失败:', response.text)
        return None

# Bot启动成功
@client.event
async def on_ready():
    print(f'✅ Bot已上线 - 登录账号: {client.user}')

# 监听消息
@client.event
async def on_message(message):
    # 不要翻译自己发的消息
    if message.author == client.user:
        return

    text = message.content.strip()

    print(f"收到消息: {text}")
    # 简单判断是不是纯英文（可以后面加更智能的检测）
    # if text and text.isascii():
    #     translated = translate_text(text)
    #     if translated:
    #         await message.reply(f"🌐 翻译结果: {translated}")

# 启动Bot
client.run(DISCORD_TOKEN)
