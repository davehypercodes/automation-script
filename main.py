import time
from bot import WhatsTweetBot

LONG_SLEEP_TIME = 30
MID_SLEEP_TIME = 15

bot = WhatsTweetBot()
bot.open_browser()
time.sleep(MID_SLEEP_TIME)
bot.open_whatsapp()
time.sleep(LONG_SLEEP_TIME)
bot.get_messages()
bot.extract_links()
bot.engage_tweets()
