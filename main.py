import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==========================
# CONFIG
# ==========================
TOKEN = os.environ["BOT_TOKEN"]

# balances stored in memory (for demo; use DB for production)
user_data = {}

# ==========================
# TELEGRAM BOT COMMANDS
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data.setdefault(user.id, {"balance": 0, "withdrawable": 0})
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        "Use /balance to check your pesos 💰\n"
        "Use /captcha2earn to solve captchas 🧩\n"
        "Use /dice to gamble 🎲\n"
        "Use /scatterspin to spin 🎰\n"
        "Use /withdraw to cash out 💵"
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = user_data.get(user.id, {"balance": 0, "withdrawable": 0})
    await update.message.reply_text(
        f"⚖️ Balance: {data['balance']} pesos\n"
        f"💵 Withdrawable: {data['withdrawable']} pesos"
    )

async def captcha2earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reward = random.randint(1, 10)
    user_data.setdefault(user.id, {"balance": 0, "withdrawable": 0})
    user_data[user.id]["balance"] += reward
    await update.message.reply_text(
        f"🧩 Captcha solved!\nYou earned ₱{reward}.\n"
        f"💰 Total balance: {user_data[user.id]['balance']} pesos"
    )

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = user_data.get(user.id, {"balance": 0, "withdrawable": 0})
    if data["withdrawable"] <= 0:
        await update.message.reply_text(
            "🚫 You don’t have withdrawable balance yet.\n"
            "👉 Play games and invite friends first!"
        )
    else:
        await update.message.reply_text(
            "💵 Withdrawal request started!\n"
            "Please send your Full Name + GCash number here."
        )

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roll = random.randint(1, 6)
    await update.message.reply_text(f"🎲 You rolled: {roll}")

async def scatterspin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbols = ["🍒", "7️⃣", "⭐", "💎"]
    spin = [random.choice(symbols) for _ in range(3)]
    result = " ".join(spin)
    await update.message.reply_text(f"🎰 {result}")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ About this bot:\n"
        "Earn by solving captchas, playing games, and inviting friends!\n"
        "🔑 Rules:\n"
        "• Invite 10 people to unlock withdrawals\n"
        "• Must play before withdrawing\n"
        "• After 50 captchas, invite 1 person to continue"
    )

# ==========================
# MAIN
# ==========================
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("captcha2earn", captcha2earn))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("scatterspin", scatterspin))
    app.add_handler(CommandHandler("about", about))

    print("Bot is running...")
    app.run_polling()  # Long polling keeps the bot alive on Render Free plan

if __name__ == "__main__":
    main()
