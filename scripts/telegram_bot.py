#!/usr/bin/env python3
"""
Polymarket Telegram Bot
Provides wallet analysis via Telegram interface
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to path for bot module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

from bot.config import BOT_TOKEN, is_user_allowed, validate_config, CACHE_DURATION_SECONDS
from bot.analysis import run_wallet_analysis, get_cached_analysis, cache_analysis, generate_html_report
from bot.formatters import (
    format_summary,
    format_detailed_metrics,
    format_hft_analysis,
    format_top_trades,
    format_error_message
)
from bot.charts import generate_all_charts

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WALLET_ADDRESS, TIMEFRAME = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user

    # Check authorization
    if not is_user_allowed(user.id):
        await update.message.reply_text(
            "⛔ <b>Access Denied</b>\n\n"
            "You are not authorized to use this bot.\n"
            "Contact the bot administrator for access.",
            parse_mode='HTML'
        )
        logger.warning(f"Unauthorized access attempt by user {user.id} ({user.username})")
        return ConversationHandler.END

    logger.info(f"User {user.id} ({user.username}) started conversation")

    welcome_message = f"""
👋 <b>Welcome to Polymarket Analyzer!</b>

Hi {user.first_name}! I can analyze Polymarket wallet performance and detect trading patterns.

<b>What I provide:</b>
📊 Comprehensive performance metrics
📈 Win rate and profit factor analysis
⚡ HFT bot detection
📉 PnL charts and visualizations
🏆 Top winning and losing trades

<b>To get started:</b>
Send me a wallet address (0x...)
"""

    await update.message.reply_text(welcome_message.strip(), parse_mode='HTML')
    return WALLET_ADDRESS


async def receive_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate wallet address"""
    wallet = update.message.text.strip()

    # Validate wallet address format
    if not wallet.startswith('0x'):
        await update.message.reply_text(
            "❌ Invalid format. Wallet address must start with '0x'\n\n"
            "Try again or send /cancel to stop."
        )
        return WALLET_ADDRESS

    if len(wallet) != 42:
        await update.message.reply_text(
            f"❌ Invalid length. Wallet address should be 42 characters (you sent {len(wallet)}).\n\n"
            "Try again or send /cancel to stop."
        )
        return WALLET_ADDRESS

    # Store wallet in context
    context.user_data['wallet'] = wallet

    logger.info(f"User {update.effective_user.id} analyzing wallet {wallet[:10]}...")

    # Ask for timeframe
    await update.message.reply_text(
        f"✅ Wallet: <code>{wallet[:10]}...{wallet[-6:]}</code>\n\n"
        f"<b>How many days back to analyze?</b>\n\n"
        f"Options:\n"
        f"• Send a number (e.g., <code>7</code>, <code>30</code>, <code>90</code>)\n"
        f"• Send <code>all</code> for complete history\n\n"
        f"Recommended: <b>30</b> days for best performance",
        parse_mode='HTML'
    )
    return TIMEFRAME


async def receive_timeframe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive timeframe and start analysis"""
    timeframe_text = update.message.text.strip().lower()
    wallet = context.user_data['wallet']

    # Parse timeframe
    if timeframe_text == 'all':
        days_back = None
        timeframe_display = "all available data"
    else:
        try:
            days_back = int(timeframe_text)
            if days_back <= 0:
                raise ValueError
            timeframe_display = f"last {days_back} days"
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid timeframe. Send a positive number or 'all'.\n\n"
                "Examples: <code>7</code>, <code>30</code>, <code>90</code>, <code>all</code>",
                parse_mode='HTML'
            )
            return TIMEFRAME

    # Check cache first
    cache_key = f"{wallet}_{days_back}"
    cached_results = get_cached_analysis(cache_key, CACHE_DURATION_SECONDS)

    if cached_results:
        logger.info(f"Using cached results for {wallet[:10]}")
        await update.message.reply_text(
            "✨ <b>Using cached results</b> (generated in the last hour)\n\n"
            "Sending analysis...",
            parse_mode='HTML'
        )
        await send_analysis_results(update, context, cached_results)
        return ConversationHandler.END

    # Start analysis
    status_msg = await update.message.reply_text(
        f"🔍 <b>Analyzing wallet...</b>\n\n"
        f"Wallet: <code>{wallet[:10]}...{wallet[-6:]}</code>\n"
        f"Timeframe: {timeframe_display}\n\n"
        f"⏳ This may take 30-60 seconds...",
        parse_mode='HTML'
    )

    try:
        # Update status
        await status_msg.edit_text(
            "📊 <b>Fetching data from Polymarket API...</b>\n\n"
            "Please wait...",
            parse_mode='HTML'
        )

        # Run analysis
        results = run_wallet_analysis(wallet, days_back)

        # Cache results
        cache_analysis(cache_key, results)

        await status_msg.edit_text(
            "✅ <b>Analysis complete!</b>\n\n"
            "Sending results...",
            parse_mode='HTML'
        )

        # Send results
        await send_analysis_results(update, context, results)

        logger.info(f"Successfully analyzed {wallet[:10]} for user {update.effective_user.id}")

    except Exception as e:
        logger.error(f"Analysis error for {wallet[:10]}: {e}", exc_info=True)

        error_message = format_error_message(e)
        await status_msg.edit_text(error_message, parse_mode='HTML')

    return ConversationHandler.END


async def send_analysis_results(update: Update, context: ContextTypes.DEFAULT_TYPE, results: dict):
    """
    Send analysis results to user

    Args:
        update: Telegram update
        context: Callback context
        results: Analysis results dict
    """

    # 1. Send summary
    summary = format_summary(results)
    await update.message.reply_text(summary, parse_mode='HTML')

    # 2. Send detailed metrics table
    detailed_metrics = format_detailed_metrics(results['metrics'])
    await update.message.reply_text(detailed_metrics, parse_mode='HTML')

    # 3. Send HFT analysis
    hft_analysis = format_hft_analysis(results['metrics'])
    await update.message.reply_text(hft_analysis, parse_mode='HTML')

    # 4. Generate and send charts
    await update.message.reply_text("📈 <b>Generating charts...</b>", parse_mode='HTML')

    try:
        charts = generate_all_charts(results['df'])

        for chart_name, chart_buffer in charts.items():
            try:
                await update.message.reply_photo(
                    photo=chart_buffer,
                    caption=f"📊 <b>{chart_name}</b>",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"Error sending chart {chart_name}: {e}")

    except Exception as e:
        logger.error(f"Error generating charts: {e}", exc_info=True)
        await update.message.reply_text(
            "⚠️ Some charts could not be generated",
            parse_mode='HTML'
        )

    # 5. Send top trades
    try:
        top_trades_msg = format_top_trades(results['top_winners'], results['top_losers'])
        await update.message.reply_text(top_trades_msg, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error formatting top trades: {e}")

    # 6. Generate and send HTML report
    try:
        await update.message.reply_text(
            "📄 <b>Generating interactive HTML report...</b>",
            parse_mode='HTML'
        )

        html_path = generate_html_report(results)

        # Send HTML file
        with open(html_path, 'rb') as html_file:
            await update.message.reply_document(
                document=html_file,
                filename=os.path.basename(html_path),
                caption="📊 <b>Interactive HTML Report</b>\n\n"
                        "Open this file in your web browser for:\n"
                        "• Interactive charts (zoom, pan, hover)\n"
                        "• All positions with search & pagination\n"
                        "• Mobile-friendly responsive design\n"
                        "• Full analysis details",
                parse_mode='HTML'
            )

        logger.info(f"HTML report sent for {results['wallet'][:10]}")

    except Exception as e:
        logger.error(f"Error generating/sending HTML report: {e}", exc_info=True)
        await update.message.reply_text(
            "⚠️ Could not generate HTML report, but analysis is complete!",
            parse_mode='HTML'
        )

    # 7. Completion message
    await update.message.reply_text(
        "✅ <b>Analysis complete!</b>\n\n"
        "Want more?\n"
        "• Send <b>/analyze</b> to analyze another wallet\n"
        "• Send <b>/help</b> for more information",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""

    help_text = """
<b>📚 Polymarket Analyzer Bot - Help</b>

<b>Commands:</b>
/start - Start new analysis
/analyze - Analyze another wallet
/help - Show this help message
/cancel - Cancel current analysis

<b>How to use:</b>
1. Send /start or /analyze
2. Provide a wallet address (0x...)
3. Choose timeframe (days or 'all')
4. Receive comprehensive analysis

<b>What you get:</b>
• Performance metrics (PnL, win rate, profit factor)
• HFT bot detection
• Visual charts (cumulative PnL, distributions)
• Top winning and losing trades
• Trading frequency analysis

<b>Features:</b>
⚡ HFT Bot Detection - Identifies algorithmic trading
📊 Complete Metrics - Win rate, risk/reward, drawdown
📈 Visual Charts - Easy-to-read performance graphs
🏆 Top Trades - Best and worst positions
⏱️ Fast Analysis - Results in 30-60 seconds

<b>Timeframe Tips:</b>
• Use <b>7 days</b> for recent performance
• Use <b>30 days</b> for balanced analysis (recommended)
• Use <b>90 days</b> for long-term patterns
• Use <b>all</b> for complete history (may be slower)

<b>Note:</b> Analysis results are cached for 1 hour for faster re-queries.
"""

    await update.message.reply_text(help_text.strip(), parse_mode='HTML')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current conversation"""
    await update.message.reply_text(
        "❌ Analysis canceled.\n\n"
        "Send /start to begin a new analysis.",
        parse_mode='HTML'
    )
    logger.info(f"User {update.effective_user.id} canceled conversation")
    return ConversationHandler.END


async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analyze command (alias for /start)"""
    return await start(update, context)


def main():
    """Start the bot"""

    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for analysis
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('analyze', analyze_command)
        ],
        states={
            WALLET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_wallet)],
            TIMEFRAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_timeframe)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))

    # Start bot
    logger.info("Bot starting...")
    print("="*60)
    print("✓ Polymarket Telegram Bot is running!")
    print("="*60)
    print("Press Ctrl+C to stop the bot")
    print()

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
