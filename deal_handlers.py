import json
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID
from database import *
from utils import *
from keyboards import *

# ============ APPROVE FORM (Admin clicks Both Agree) ============
async def approve_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id) and user_id != OWNER_ID:
        await query.edit_message_text(f"{to_stylish('Only admins can approve forms!')}")
        return
    
    data = query.data
    action, form_id = data.split('_', 1)
    form_id = int(form_id)
    
    if action == 'reject':
        delete_pending_form(form_id)
        await query.edit_message_text(f"{to_stylish('Form rejected!')}")
        return
    
    pending = get_pending_form(form_id)
    if not pending:
        await query.edit_message_text(f"{to_stylish('Form not found!')}")
        return
    
    form_data = json.loads(pending['form_data'])
    deal_id = generate_deal_id()
    create_deal(deal_id, form_data, user_id, pending['message_id'])
    add_log(deal_id, 'created', user_id, json.dumps(form_data))
    delete_pending_form(form_id)
    
    formatted = format_deal_form(form_data)
    buttons = get_deal_buttons(deal_id)
    
    try:
        await context.bot.edit_message_text(
            chat_id=pending['chat_id'],
            message_id=pending['message_id'],
            text=f"{formatted}\n\n---\n{to_stylish('DEAL CREATED!')}\n{to_stylish('Deal ID')}: {deal_id}\n{to_stylish('Approved by')}: @{query.from_user.username or 'admin'}",
            reply_markup=buttons
        )
    except:
        pass
    
    await query.edit_message_text(f"{to_stylish('Deal Created!')}\n{to_stylish('Deal ID')}: {deal_id}\n\n{formatted}")
    
    # Notify buyer and seller
    buyer = form_data.get('buyer', '').replace('@', '')
    seller = form_data.get('seller', '').replace('@', '')
    
    try:
        if buyer.isdigit():
            await context.bot.send_message(
                int(buyer),
                f"{to_stylish('Deal created!')}\n{to_stylish('Deal ID')}: {deal_id}\n{to_stylish('Amount')}: ₹{form_data.get('amount')}\n{to_stylish('Seller')}: {form_data.get('seller')}"
            )
    except:
        pass
    
    try:
        if seller.isdigit():
            await context.bot.send_message(
                int(seller),
                f"{to_stylish('Deal created!')}\n{to_stylish('Deal ID')}: {deal_id}\n{to_stylish('Amount')}: ₹{form_data.get('amount')}\n{to_stylish('Buyer')}: {form_data.get('buyer')}"
            )
    except:
        pass

# ============ DEAL ACTION (Buttons) ============
async def deal_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id) and user_id != OWNER_ID:
        await query.edit_message_text(f"{to_stylish('Only admins can perform this!')}")
        return
    
    data = query.data
    action, deal_id = data.split('_', 1)
    
    deal = get_deal(deal_id)
    if not deal:
        await query.edit_message_text(f"{to_stylish('Deal not found!')}")
        return
    
    if deal['status'] != 'pending':
        await query.edit_message_text(f"{to_stylish('Deal is already')} {deal['status'].upper()}!")
        return
    
    if deal['handled_by'] and deal['handled_by'] != user_id:
        await query.edit_message_text(f"{to_stylish('Another admin is handling this!')}")
        return
    
    if action == 'pay':
        update_deal_status(deal_id, 'payment_received', user_id)
        add_log(deal_id, 'payment_received', user_id)
        msg = format_deal_message(deal, 'payment')
        await query.edit_message_text(msg, reply_markup=get_deal_buttons(deal_id))
    
    elif action == 'hold':
        update_deal_status(deal_id, 'on_hold', user_id)
        add_log(deal_id, 'hold', user_id)
        msg = format_deal_message(deal, 'hold')
        await query.edit_message_text(msg, reply_markup=get_deal_buttons(deal_id))
    
    elif action == 'cancel':
        update_deal_status(deal_id, 'cancelled', user_id)
        add_log(deal_id, 'cancelled', user_id)
        msg = format_deal_message(deal, 'cancel')
        await query.edit_message_text(msg)

# ============ MAIN CALLBACK ROUTER ============
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Approve/Reject form
    if data.startswith('approve_') or data.startswith('reject_'):
        await approve_form(update, context)
        return
    
    # Deal actions
    if data.startswith('pay_') or data.startswith('hold_') or data.startswith('cancel_'):
        await deal_action(update, context)
        return
    
    # Admin panel
    if data.startswith('admin_'):
        from admin_panel import admin_callback
        await admin_callback(update, context)
        return
    
    # New deal
    if data == "new_deal":
        from handlers import new_deal_cmd
        await new_deal_cmd(update, context)
        return
    
    # Admin panel
    if data == "admin_panel":
        from admin_panel import admin_panel_cmd
        await admin_panel_cmd(update, context)
        return
    
    # Help
    if data == "help":
        from handlers import help_cmd
        await help_cmd(update, context)
        return

# ============ ERROR HANDLER ============
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)