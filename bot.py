#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import threading
import time
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from config import BOT_TOKEN, OWNER_ID, CHANNEL_USERNAME, MAX_DEAL_LIMIT
from database import *
from utils import *
from keyboards import *
from handlers import *
from admin_panel import *
from deal_handlers import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ FLASK ============
flask_app = Flask(__name__)

@flask_app.route('/')
@flask_app.route('/health')
def health():
    return "BOT RUNNING", 200

def run_flask():
    try:
        port = int(os.environ.get('PORT', 5000))
        flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask error: {e}")

# ============ MAIN ============
def main():
    logger.info("Starting KALYUG ESCROW BOT...")
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info(f"Flask server started on port {os.environ.get('PORT', 5000)}")
    
    application = Application.builder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("newdeal", new_deal_cmd),
            CallbackQueryHandler(button_callback, pattern="^new_deal$")
        ],
        states={
            FORM_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_amount)],
            FORM_BUYER: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_buyer)],
            FORM_SELLER: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_seller)],
            FORM_DEAL_DETAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_deal_detail)],
            FORM_RLS_UPI: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_rls_upi)],
            FORM_CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_condition)],
            FORM_ESCROW_TILL: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_escrow_till)],
        },
        fallbacks=[CommandHandler("cancel", cancel_form)],
        per_message=True
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("status", deal_status_cmd))
    application.add_handler(CommandHandler("admin", admin_panel_cmd))
    application.add_handler(CommandHandler("approve", approve_cmd))
    application.add_handler(CommandHandler("removeadmin", removeadmin_cmd))
    application.add_handler(CommandHandler("setlimit", setlimit_cmd))
    
    # Manual commands
    application.add_handler(CommandHandler("recived", recived_cmd))
    application.add_handler(CommandHandler("hold", hold_cmd))
    application.add_handler(CommandHandler("cancel", cancel_cmd))
    
    # Callbacks
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    logger.info("=" * 50)
    logger.info("KALYUG ESCROW SERVICE BOT")
    logger.info(f"Owner ID: {OWNER_ID}")
    logger.info(f"Channel: {CHANNEL_USERNAME}")
    logger.info(f"Max Deal Limit: ₹{MAX_DEAL_LIMIT}")
    logger.info("Bot is ready!")
    logger.info("=" * 50)
    
    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Polling crashed: {e}")
            time.sleep(5)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith('approve_') or data.startswith('reject_'):
        await approve_form(update, context)
        return
    
    if data.startswith('pay_') or data.startswith('hold_') or data.startswith('cancel_'):
        await deal_action(update, context)
        return
    
    if data.startswith('admin_'):
        await admin_callback(update, context)
        return
    
    if data == "new_deal":
        await new_deal_cmd(update, context)
        return
    
    if data == "admin_panel":
        await admin_panel_cmd(update, context)
        return
    
    if data == "help":
        await help_cmd(update, context)
        return

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)

if __name__ == "__main__":
    main()