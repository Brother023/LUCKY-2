import os
import logging
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to TimeZone Assistant!\n\n"
        "Send me a city name (e.g., *Tokyo*) and I'll tell you the current time.\n\n"
        "Commands:\n"
        "/time - Get time for a city\n"
        "/convert - Compare two cities\n"
        "/help - Show this message",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n\n"
        "/time <city> - Get current time\n"
        "/convert <city1> <city2> - Compare times\n\n"
        "Or just type a city name directly!"
    )

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please specify a city. Example: /time Tokyo")
        return
    
    city = " ".join(context.args)
    try:
        # Common city to timezone mapping
        timezone_map = {
            "tokyo": "Asia/Tokyo",
            "new york": "America/New_York",
            "london": "Europe/London",
            "paris": "Europe/Paris",
            "sydney": "Australia/Sydney",
            "dubai": "Asia/Dubai",
            "los angeles": "America/Los_Angeles",
            "chicago": "America/Chicago",
            "berlin": "Europe/Berlin",
            "moscow": "Europe/Moscow",
            "singapore": "Asia/Singapore",
            "hong kong": "Asia/Hong_Kong",
        }
        
        tz_name = timezone_map.get(city.lower())
        if not tz_name:
            # Try direct timezone lookup
            try:
                tz = pytz.timezone(city)
                tz_name = city
            except:
                await update.message.reply_text(f"Sorry, I don't know '{city}'. Try a major city name.")
                return
        
        tz = pytz.timezone(tz_name)
        current_time = datetime.now(tz)
        formatted = current_time.strftime("%A, %B %d, %Y at %I:%M %p")
        
        await update.message.reply_text(
            f"🕐 **{city.title()}**\n{formatted}\n\nTimezone: `{tz_name}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text("Error looking up that city. Please try another.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
    
    # Treat any text as a city query
    context.args = text.split()
    await time_command(update, context)

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /convert <city1> <city2>\nExample: /convert London Tokyo")
        return
    
    # Simple conversion - just shows both times
    city1, city2 = context.args[0], context.args[1]
    
    timezone_map = {
        "tokyo": "Asia/Tokyo",
        "new york": "America/New_York",
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "sydney": "Australia/Sydney",
        "dubai": "Asia/Dubai",
    }
    
    tz1_name = timezone_map.get(city1.lower())
    tz2_name = timezone_map.get(city2.lower())
    
    if not tz1_name or not tz2_name:
        await update.message.reply_text("I only know major cities. Try: London, Tokyo, New York, Paris, Sydney, Dubai")
        return
    
    tz1 = pytz.timezone(tz1_name)
    tz2 = pytz.timezone(tz2_name)
    
    time1 = datetime.now(tz1)
    time2 = datetime.now(tz2)
    
    diff = time2.utcoffset() - time1.utcoffset()
    hours = int(diff.total_seconds() // 3600)
    minutes = int((diff.total_seconds() % 3600) // 60)
    
    sign = "+" if hours >= 0 else ""
    
    await update.message.reply_text(
        f"🕐 **{city1.title()}:** {time1.strftime('%I:%M %p')}\n"
        f"🕐 **{city2.title()}:** {time2.strftime('%I:%M %p')}\n\n"
        f"Difference: {sign}{hours}h {minutes}m",
        parse_mode="Markdown"
    )

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("time", time_command))
    application.add_handler(CommandHandler("convert", convert_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
