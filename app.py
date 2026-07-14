import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK"

# ========== BOT LOGIC ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
QR_URL = "https://i.ibb.co/zH7n458d/IMG-20260710-WA0005.jpg"  # teri QR image

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["📱 Instagram", "instagram"],
        ["💳 UPI", "upi"],
        ["📞 Number", "number"],
        ["🆔 TG ID", "tg_id"],
        ["👤 TG Username", "tg_username"],
        ["🚗 Vehicle", "vehicle"],
        ["👨‍👩‍👧‍👦 Family", "family"],
        ["🪪 PAN", "pan"],
        ["🪪 Aadhar", "aadhar"],
        ["🏢 HiTek", "hitek"],
        ["📱 Paytm", "paytm"],
        ["📘 Facebook", "facebook"],
        ["👻 Snapchat", "snapchat"]
    ]
    await update.message.reply_text(
        "🔍 OSINT Search Bot\n\nSelect an option:\n\n⚠️ Paid Service: ₹150\n✅ Lifetime Access\n♾️ Unlimited Searches",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    category = query.data
    
    await context.bot.send_message(
        user.id,
        f"🔒 Access Denied\n\nPay ₹150 to unlock {category}.\n✅ Lifetime Access\n♾️ Unlimited Searches"
    )
    await context.bot.send_photo(
        user.id,
        QR_URL,
        caption="📸 Scan this QR to pay ₹150"
    )
    await context.bot.send_message(
        user.id,
        "After payment, click below:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ I have paid", callback_data="fake_verify")]
        ])
    )

async def fake_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    await context.bot.send_message(
        user.id,
        f"❌ Access Denied\n\nPayment not found.\nPlease pay ₹150 again.\n✅ Lifetime Access\n♾️ Unlimited Searches"
    )
    await context.bot.send_photo(
        user.id,
        QR_URL,
        caption="📸 Pay ₹150 to unlock"
    )
    await context.bot.send_message(
        user.id,
        "After payment, click below:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ I have paid", callback_data="fake_verify")]
        ])
    )

def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # Register all callbacks
    categories = [
        "instagram", "upi", "number", "tg_id", "tg_username",
        "vehicle", "family", "pan", "aadhar", "hitek",
        "paytm", "facebook", "snapchat", "fake_verify"
    ]
    for cat in categories:
        application.add_handler(CallbackQueryHandler(handle_selection, pattern=f"^{cat}$"))
    
    application.run_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
