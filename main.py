import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ==========================
# CONFIG
# ==========================
TOKEN = os.environ["BOT_TOKEN"]

# balances stored in memory (for demo; use DB for production)
user_data = {}

# store pending captcha answers
captcha_answers = {}

# ==========================
# TELEGRAM BOT COMMANDS
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data.setdefault(user.id, {"balance": 0})
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
    data = user_data.get(user.id, {"balance": 0})
    await update.message.reply_text(
        f"⚖️ Balance: {data['balance']} pesos"
    )

# ==========================
# CAPTCHA SYSTEM
# ==========================
async def captcha2earn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # generate a simple captcha (number addition)
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    answer = a + b
    captcha_answers[user.id] = answer
    await update.message.reply_text(
        f"🧩 Solve this captcha to earn reward:\n\n"
        f"{a} + {b} = ?\n\n"
        "Reply with the answer."
    )

async def check_captcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in captcha_answers:
        try:
            msg = int(update.message.text.strip())
            if msg == captcha_answers[user.id]:
                reward = random.randint(1, 10)
                user_data.setdefault(user.id, {"balance": 0})
                user_data[user.id]["balance"] += reward
                await update.message.reply_text(
                    f"✅ Correct! You earned ₱{reward}.\n"
                    f"💰 Total balance: {user_data[user.id]['balance']} pesos"
                )
            else:
                await update.message.reply_text("❌ Wrong answer! Try /captcha2earn again.")
        except ValueError:
            await update.message.reply_text("❌ Please enter a number.")
        del captcha_answers[user.id]

# ==========================
# OTHER COMMANDS
# ==========================
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = user_data.get(user.id, {"balance": 0})
    if data["balance"] <= 0:
        await update.message.reply_text("🚫 You don’t have any balance to withdraw yet.")
    else:
        await update.message.reply_text(
            f"💵 Withdrawal request started for ₱{data['balance']}.\n"
            "Please send your Full Name + GCash number here."
        )
        data["balance"] = 0  # reset balance after withdrawal

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
        "Earn by solving captchas and playing games!"
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

    # Handle answers to captchas
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_captcha))

    print("Bot is running...")
    app.run_polling()  # Long polling keeps the bot alive on Render Free plan

if __name__ == "__main__":
    main()
