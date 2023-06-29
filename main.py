import logging
import asyncio
import os
from dotenv import load_dotenv
from botdb import BotDB
from pydub import AudioSegment
from aiogram import Bot, Dispatcher, types
import speech_recognition as sr

load_dotenv()

logging.basicConfig(level=logging.INFO)

db = BotDB("botdb.sqlite")
bot = Bot(token= os.getenv("TG_TOKEN"))
dp = Dispatcher(bot)
rec = sr.Recognizer()

@dp.message_handler(content_types=['voice'])
async def voice_handler(message: types.Message):
    chat_id = message.chat.id
    file = message.voice
    file_name = f'{file.file_id}'
    file_dir = 'voice_files'

    os.makedirs(file_dir, exist_ok=True)
    ogg_file_path = os.path.join(file_dir, file_name + '.ogg')
    await file.download(destination_file=ogg_file_path)

    wav_file_path = os.path.join(file_dir, file_name + '.wav')
    audio = AudioSegment.from_ogg(ogg_file_path)
    audio.export(wav_file_path, format='wav')
    
    with sr.AudioFile(wav_file_path) as audio_file:
        audio = rec.record(audio_file)
    
    try:
        lang = db.get_lang(chat_id)
        if lang == None:
            await message.reply('To use the function, set the language (use /lang)')
            return
        
        text = rec.recognize_google(audio, language=f"{lang}")
        await message.reply(f'Voice Transcription ({lang}): {text}')
    except Exception as e:
        print(e)
        await message.reply('To use the function, set the language (use /lang)')
    finally:
        os.remove(ogg_file_path)
        os.remove(wav_file_path)
    

@dp.message_handler(commands=['all'])
async def ping_all_handler(message: types.Message):
    chat_id = message.chat.id
    try:
        notification = db.get_notification(chat_id)
        if notification == None:
            await message.reply('To use the function, create a notification message (use: /set)')
            return
        await message.reply(notification)
    except:
        await message.reply('To use the function, create a notification message (use: /set)')

@dp.message_handler(commands=['set'])
async def set_notification_handler(message: types.Message):
    set_text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    bot_info  = await bot.get_me()

    if set_text.endswith('/set') or set_text.endswith('/set ') or set_text.endswith('/set@' + bot_info['username']):
        await message.reply("Enter this command again and add the tags of the users you want to notify (example: /set @user1, @user2, @user3)")
        return

    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ('creator', 'administrator'):
        await message.reply("This command can only be used by the administrator.")
        return

    set_text = set_text.replace('@' + bot_info['username'], '').replace('/set', '')

    try:
        db.add_notification(chat_id, set_text)
        await message.reply(f"Notification message set to: {set_text}")
    except Exception as e:
        print(e)
        await message.reply("An error occurred")

@dp.message_handler(commands=['lang'])
async def lang_handler(message: types.Message):
    lang_text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    bot_info  = await bot.get_me()

    if lang_text.endswith('/lang') or lang_text.endswith('/lang ') or lang_text.endswith('lang@' + bot_info['username']):
        await message.reply("Enter this command again and add the tag of the language in which the transcription will work (example: /lang ru-RU)")
        return

    chat_member = await bot.get_chat_member(chat_id, user_id)
    if chat_member.status not in ('creator', 'administrator'):
        await message.reply("This command can only be used by the administrator.")
        return

    lang_text = lang_text.replace('@' + bot_info['username'], '').replace('/lang', '').replace(' ', '')

    try:
        db.add_lang(chat_id, lang_text)
        await message.reply(f"Language set to: {lang_text}")
    except Exception as e:
        print(e)
        await message.reply("An error occurred")

async def set_commands():
    commands = [
    types.BotCommand(command="/all", description="Pings all users"),
    types.BotCommand(command="/set", description="Sets users"),
    types.BotCommand(command="/lang", description="Set voice lang"),
    ]
    await bot.set_my_commands(commands)

async def main():
    try:
        await asyncio.gather(set_commands(),dp.start_polling())
    finally:
        db.disconnect()
        await dp.storage.close()
        await dp.storage.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
