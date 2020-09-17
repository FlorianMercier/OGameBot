import requests


def bot_sendtext(bot_message):
    bot_token = "YOUR_BOT_TOKEN_HERE"
    bot_chatID = "YOUR_BOT_CHAT_ID_HERE"
    send_text = (
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + bot_chatID
        + "&parse_mode=Markdown&text="
        + bot_message
    )
    response = requests.get(send_text)
    return response.json()
