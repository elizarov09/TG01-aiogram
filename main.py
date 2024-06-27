import asyncio
from aiogram import Bot, Dispatcher, F

from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import TOKEN

import random

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('photo'))
async def photo(message: Message):
    list = ['https://vet-centre.by/wp-content/uploads/2016/11/kot-eti-udivitelnye-kotiki.jpg', 'https://dorinvest.ru/media/k2/items/cache/ac9ff722ccee9f796dea38c810f03e02_XL.jpg', 'https://s0.rbk.ru/v6_top_pics/media/img/7/65/755540270893657.jpg', 'https://vestart.ru/images/2022/03/31/5_large.jpg']
    rand_photo = random.choice(list)
    await message.answer_photo(rand_photo, caption="Зачетная фотка!")

@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Зачетная фотка!', 'Давайте еще раз!', 'Прикол!', 'Блеск!']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)
@dp.message(F.text == 'Что такое ИИ?')
async def aitext(message: Message):
    await message.answer("Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ")

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды: \n /start \n /help")

@dp.message(CommandStart())
async def bot_start(message: Message):
    await message.answer(f"Привет, {message.from_user.full_name}!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())