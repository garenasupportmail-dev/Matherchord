import json
from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER_ID, MAX_DEAL_LIMIT
from database import *
from utils import *
from keyboards import *

async def admin_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(f"{to_stylish('Admin panel only!')}")
        return
    
    total_deals = len(get_all_deals())
    pending_deals = len(get_deals_by_status('pending'))
    completed_deals = len(get_deals_by_status('completed'))
    pending_forms = len(get_all_pending_forms())
    admins_list = get_admins()
    admin_limit = get_admin_limit(user_id) if user_id != OWNER_ID else MAX_DEAL_LIMIT
    
    msg = f"""
{to_stylish('ADMIN PANEL')}
{to_stylish('KALYUG ESCROW SERVICE')}

{to_stylish('Total Deals')}: {total_deals}
{to_stylish('Pending')}: {pending_deals}
{to_stylish('Completed')}: {completed_deals}
{to_stylish('Pending Forms')}: {pending_forms}
{to_stylish('Admins')}: {len(admins_list)}
{to_stylish('Your Limit')}: ₹{admin_limit}

@KALYUGESCROWSERVICE
"""
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(msg, reply_markup=get_admin_panel_buttons())
    else:
        await update.message.reply_text(msg, reply_markup=get_admin_panel_buttons())

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if not is_admin(user_id) and user_id != OWNER_ID:
        await query.edit_message_text(f"{to_stylish('Admin only!')}")
        return
    
    data = query.data
    
    if data == "admin_back":
        await admin_panel_cmd(update, context)
        return
    
    if data == "admin_deals":
        deals = get_all_deals()
        if not deals:
            msg = f"{to_stylish('No deals found.')}"
        else:
            msg = f"{to_stylish('ALL DEALS')}\n\n"
            for d in deals[:10]:
                msg += f"{d['deal_id']} - ₹{d['amount']} - {d['status'].upper()}\n"
                msg += f"   {d['buyer']} -> {d['seller']}\n\n"
            if len(deals) > 10:
                msg += f"\n... {to_stylish('and')} {len(deals)-10} {to_stylish('more')}"
        await query.edit_message_text(msg, reply_markup=get_back_button())
        return
    
    if data == "admin_pending":
        deals = get_deals_by_status('pending')
        if not deals:
            msg = f"{to_stylish('No pending deals.')}"
        else:
            msg = f"{to_stylish('PENDING DEALS')}\n\n"
            for d in deals[:10]:
                msg += f"{d['deal_id']} - ₹{d['amount']}\n"
                msg += f"   {d['buyer']} -> {d['seller']}\n\n"
            if len(deals) > 10:
                msg += f"\n... {to_stylish('and')} {len(deals)-10} {to_stylish('more')}"
        await query.edit_message_text(msg, reply_markup=get_back_button())
        return
    
    if data == "admin_list":
        admins = get_all_admins_with_limits()
        if not admins:
            msg = f"{to_stylish('No admins found.')}"
        else:
            msg = f"{to_stylish('ADMIN LIST')}\n\n"
            for a in admins:
                is_owner_tag = f"{to_stylish('OWNER')} " if a[0] == OWNER_ID else ""
                msg += f"{is_owner_tag}{to_stylish('ID')}: {a[0]}\n"
                msg += f"   {to_stylish('Limit')}: ₹{a[2]}\n\n"
        await query.edit_message_text(msg, reply_markup=get_back_button())
        return
    
    if data == "admin_status":
        total = len(get_all_deals())
        pending = len(get_deals_by_status('pending'))
        completed = len(get_deals_by_status('completed'))
        cancelled = len(get_deals_by_status('cancelled'))
        on_hold = len(get_deals_by_status('on_hold'))
        payment_received = len(get_deals_by_status('payment_received'))
        msg = f"""
{to_stylish('DEAL STATUS')}

{to_stylish('Total')}: {total}
{to_stylish('Pending')}: {pending}
{to_stylish('Completed')}: {completed}
{to_stylish('Cancelled')}: {cancelled}
{to_stylish('On Hold')}: {on_hold}
{to_stylish('Payment Received')}: {payment_received}

@KALYUGESCROWSERVICE
"""
        await query.edit_message_text(msg, reply_markup=get_back_button())
        return
    
    if data == "admin_forms":
        forms = get_all_pending_forms()
        if not forms:
            msg = f"{to_stylish('No pending forms.')}"
        else:
            msg = f"{to_stylish('PENDING FORMS')}\n\n"
            for f in forms[:10]:
                form_data = json.loads(f['form_data'])
                msg += f"{to_stylish('ID')}: {f['id']}\n"
                msg += f"{to_stylish('User')}: @{f['username'] or f['user_id']}\n"
                msg += f"{to_stylish('Amount')}: ₹{form_data.get('amount', 'N/A')}\n"
                msg += f"{to_stylish('Buyer')}: {form_data.get('buyer', 'N/A')}\n"
                msg += f"{to_stylish('Seller')}: {form_data.get('seller', 'N/A')}\n\n"
            if len(forms) > 10:
                msg += f"\n... {to_stylish('and')} {len(forms)-10} {to_stylish('more')}"
        await query.edit_message_text(msg, reply_markup=get_back_button())
        return