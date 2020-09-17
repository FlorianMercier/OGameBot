import telegram
from date import get_time


def log(message):
    """Print messages on terminal and send them on Telegram"""
    trace = get_time() + " : " + message
    telegram.bot_sendtext(message)
    print(trace)
