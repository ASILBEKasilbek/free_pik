import asyncio
import logging
import os
import zipfile
from urllib.parse import urlparse

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile

import url_images2  # SENING ISHLAYDIGAN MODULING

# ================== SOZLAMALAR ==================

BOT_TOKEN = "7761371107:AAH4EKOJYENanQTnWMXbt0q-ekdtfxdG-OA"

# Ruxsat berilgan guruhlar
ALLOWED_GROUPS = [
    -1002938796047,
    -1003651094836
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== YORDAMCHI ==================

def is_freepik_link(text: str) -> bool:
    return text and "freepik.com" in text

# ================== HANDLER ==================

@dp.message(F.text)
async def handle_freepik(message: Message):
    chat_id = message.chat.id
    chat_type = message.chat.type
    url = message.text.strip()

    # Freepik link emas
    if not is_freepik_link(url):
        return

    # Guruh tekshiruvi
    if chat_type in ("group", "supergroup"):
        if chat_id not in ALLOWED_GROUPS:
            return

    # ⏳ Yuklanmoqda (reply)
    loading_msg = await message.answer(
        "⏳ Sahifa ochilmoqda va rasm qidirilmoqda...\n(10–20 sekund olishi mumkin)",
        reply_to_message_id=message.message_id
    )

    try:
        # 🔥 ASINXRON BAJARISH (har bir request alohida)
        loop = asyncio.get_event_loop()
        folder, files = await loop.run_in_executor(None, url_images2.url_image, url)

        if not folder or not files:
            await loading_msg.delete()
            await message.answer(
                "😔 Rasm topilmadi yoki sahifada xato bor.",
                reply_to_message_id=message.message_id
            )
            return

        # ZIP nomi
        parsed = urlparse(url)
        name_slug = os.path.basename(parsed.path).replace(".htm", "").replace(".html", "")
        zip_name = f"{name_slug}.zip"

        # ZIP qilish
        with zipfile.ZipFile(zip_name, "w") as zipf:
            for file in files:
                zipf.write(file, arcname=os.path.basename(file))

        await loading_msg.delete()

        # ZIP ni reply qilib yuborish
        zip_file = FSInputFile(zip_name)
        await message.answer_document(
            zip_file,
            reply_to_message_id=message.message_id
        )

        # Tozalash
        os.remove(zip_name)
        for file in files:
            os.remove(file)

    except Exception as e:
        logging.exception(e)
        await message.answer(
            "❌ Xatolik yuz berdi",
            reply_to_message_id=message.message_id
        )
        try:
            await loading_msg.delete()
        except:
            pass

# ================== START ==================

async def main():
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
