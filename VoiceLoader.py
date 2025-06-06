from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from gtts import gTTS
import io

BOT_TOKEN = '7250396748:AAEmd-RhWClqO-VtCrSbQDX8vihfpZJaHbc'

# Словарь для хранения выбранных голосов
user_voice_choice = {}

# Доступные "голоса" (на деле — акценты/языки)
voice_options = {
    'ru': 'Русский',
    'en': 'Английский (США)',
    'en-uk': 'Английский (Великобритания)',
    'en-au': 'Английский (Австралия)',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=code)]
        for code, name in voice_options.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Отлично! Напишите мне текст, и я сделаю из него аудио.\n"
        "Сначала выберите голос 👇",
        reply_markup=reply_markup
    )

async def choose_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    voice_code = query.data
    user_id = query.from_user.id
    user_voice_choice[user_id] = voice_code

    await query.edit_message_text(
        text=f"✅ Голос «{voice_options[voice_code]}» выбран.\nТеперь отправьте мне текст для озвучки:"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_voice_choice:
        await update.message.reply_text("Сначала выберите голос, используя /start.")
        return

    lang = user_voice_choice[user_id]

    # Специальный случай: gTTS не знает 'en-uk' и 'en-au' — подменим на 'en'
    tts_lang = 'en' if lang.startswith('en') else lang

    # Генерация аудио
    tts = gTTS(text=text, lang=tts_lang)
    audio = io.BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)

    await update.message.reply_voice(voice=audio, caption="🎧 Вот ваше аудио!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_voice))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
