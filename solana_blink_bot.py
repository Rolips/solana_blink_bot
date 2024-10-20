import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define conversation states
AMOUNT, RECIPIENT = range(2)

# Simulated user balances (In a real application, this would be securely stored and managed)
user_balances = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! Welcome to the Solana Blink simulator. "
        f"Use /blink to simulate a quick transaction."
    )
    # Initialize user balance for demonstration
    user_balances[user.id] = 1000

async def blink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the blink transaction process."""
    await update.message.reply_text(
        "Let's simulate a quick Solana Blink transaction. "
        "How much SOL would you like to send? (Enter a number)"
    )
    return AMOUNT

async def amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the transaction amount and ask for recipient."""
    user = update.effective_user
    text = update.message.text
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
        if amount > user_balances[user.id]:
            await update.message.reply_text("Insufficient balance. Please enter a smaller amount.")
            return AMOUNT
        context.user_data['amount'] = amount
        await update.message.reply_text("Great! Now, enter the recipient's address.")
        return RECIPIENT
    except ValueError:
        await update.message.reply_text("Please enter a valid positive number.")
        return AMOUNT

async def recipient(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Complete the transaction simulation."""
    user = update.effective_user
    recipient_address = update.message.text
    amount = context.user_data['amount']
    
    # Simulate transaction
    user_balances[user.id] -= amount
    
    await update.message.reply_text(
        f"Transaction simulated successfully!\n"
        f"Sent {amount} SOL to {recipient_address}\n"
        f"Your new balance: {user_balances[user.id]} SOL"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the transaction."""
    await update.message.reply_text("Transaction cancelled.")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    application = Application.builder().token("7254013696:AAG519IuaV1R1ijyFelAXVJWaSRipIV8esk").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("blink", blink)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount)],
            RECIPIENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, recipient)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))

    application.run_polling()

if __name__ == "__main__":
    main()