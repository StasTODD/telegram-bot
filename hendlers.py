from main import bot, dp, ADMINS_IDS


async def send_to_admin(dp):
    # TODO: send message all admins, not one
    await bot.send_message(chat_id=ADMINS_IDS[0], text="Bot was start. Again... /start")
