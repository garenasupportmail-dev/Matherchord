import json
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import OWNER_ID, MAX_DEAL_LIMIT
from database import *
from utils import *
from keyboards import *

(FORM_AMOUNT, FORM_BUYER, FORM_SELLER, FORM_DEAL_DETAIL, 
 FORM_RLS_UPI, FORM_CONDITION, FORM_ESCROW_TILL) = range(7)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    is_admin_user = is_admin(user_id) or user_id == OWNER_ID
    
    msg = f"""
{to_stylish('KALYUG ESCROW SERVICE')}

{to_stylish('Welcome')} {user.first_name}!

{to_stylish('Safe and secure escrow deals')}

{to_stylish('/newdeal')} - {to_stylish('Create new deal')}
{to_stylish('/status DEAL_ID')} - {to_stylish('Check deal status')}
{to_stylish('/admin')} - {to_stylish('Admin panel')}
{to_stylish('/help')} - {to_stylish('Help menu')}

{to_stylish('MANUAL COMMANDS')}:
{to_stylish('/recived DEAL_ID')} - {to_stylish('Payment received')}
{to_stylish('/hold DEAL_ID')} - {to_stylish('Hold deal')}
{to_stylish('/cancel DEAL_ID')} - {to_stylish('Cancel deal')}

@KALYUGESCROWSERVICE
"""
    await update.message.reply_text(msg, reply_markup=get_main_menu(is_admin_user))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"""
{to_stylish('HELP MENU')}

{to_stylish('COMMANDS')}:
{to_stylish('/newdeal')} - {to_stylish('Submit new deal form')}
{to_stylish('/status DEAL_ID')} - {to_stylish('Check deal status')}
{to_stylish('/admin')} - {to_stylish('Open admin panel')}

{to_stylish('MANUAL DEAL ACTIONS')}:
{to_stylish('/recived DEAL_ID')} - {to_stylish('Mark as payment received')}
{to_stylish('/hold DEAL_ID')} - {to_stylish('Put deal on hold')}
{to_stylish('/cancel DEAL_ID')} - {to_stylish('Cancel deal')}

{to_stylish('OWNER COMMANDS')}:
{to_stylish('/approve USER_ID')} - {to_stylish('Add admin')}
{to_stylish('/removeadmin USER_ID')} - {to_stylish('Remove admin')}
{to_stylish('/setlimit AMOUNT USER_ID')} - {to_stylish('Set admin limit')}

{to_stylish('HOW TO USE')}:
1. {to_stylish('User submits deal form')}
2. {to_stylish('Admin approves with Both Agree')}
3. {to_stylish('Deal is created with ID')}
4. {to_stylish('Admin manages deal with buttons or commands')}

@KALYUGESCROWSERVICE
"""
    await update.message.reply_text(msg)

# ============ MANUAL COMMANDS ============

async def recived_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual payment received command"""
    user_id = update.effective_user.id
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(f"{to_stylish('Admin only!')}")
        return
    
    if not context.args:
        await update.message.reply_text(f"{to_stylish('Usage')}: /recived {to_stylish('DEAL_ID')}")
        return
    
    deal_id = context.args[0].upper()
    await deal_action_manual(update, context, deal_id, 'pay')

async def hold_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual hold command"""
    user_id = update.effective_user.id
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(f"{to_stylish('Admin only!')}")
        return
    
    if not context.args:
        await update.message.reply_text(f"{to_stylish('Usage')}: /hold {to_stylish('DEAL_ID')}")
        return
    
    deal_id = context.args[0].upper()
    await deal_action_manual(update, context, deal_id, 'hold')

async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual cancel command"""
    user_id = update.effective_user.id
    if not is_admin(user_id) and user_id != OWNER_ID:
        await update.message.reply_text(f"{to_stylish('Admin only!')}")
        return
    
    if not context.args:
        await update.message.reply_text(f"{to_stylish('Usage')}: /cancel {to_stylish('DEAL_ID')}")
        return
    
    deal_id = context.args[0].upper()
    await deal_action_manual(update, context, deal_id, 'cancel')

async def deal_action_manual(update: Update, context: ContextTypes.DEFAULT_TYPE, deal_id, action):
    """Common function for manual deal actions"""
    deal = get_deal(deal_id)
    if not deal:
        await update.message.reply_text(f"{to_stylish('Deal not found!')}")
        return
    
    if deal['status'] != 'pending' and action != 'complete':
        await update.message.reply_text(f"{to_stylish('Deal is already')} {deal['status'].upper()}!")
        return
    
    user_id = update.effective_user.id
    
    if deal['handled_by'] and deal['handled_by'] != user_id and deal['status'] != 'pending':
        await update.message.reply_text(f"{to_stylish('Another admin is handling this!')}")
        return
    
    if action == 'pay':
        update_deal_status(deal_id, 'payment_received', user_id)
        add_log(deal_id, 'payment_received', user_id)
        msg = format_deal_message(deal, 'payment')
        await update.message.reply_text(msg)
    
    elif action == 'hold':
        update_deal_status(deal_id, 'on_hold', user_id)
        add_log(deal_id, 'hold', user_id)
        msg = format_deal_message(deal, 'hold')
        await update.message.reply_text(msg)
    
    elif action == 'cancel':
        update_deal_status(deal_id, 'cancelled', user_id)
        add_log(deal_id, 'cancelled', user_id)
        msg = format_deal_message(deal, 'cancel')
        await update.message.reply_text(msg)

# ============ DEAL STATUS ============

async def deal_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(f"{to_stylish('Usage')}: /status {to_stylish('DEAL_ID')}")
        return
    
    deal_id = context.args[0].upper()
    deal = get_deal(deal_id)
    
    if not deal:
        await update.message.reply_text(f"{to_stylish('Deal not found!')}")
        return
    
    form_data = json.loads(deal['form_data'])
    status_text = {'pending':'PENDING','payment_received':'PAYMENT RECEIVED','on_hold':'ON HOLD','completed':'COMPLETED','cancelled':'CANCELLED'}.get(deal['status'],'PENDING')
    
    msg = f"""
{to_stylish('DEAL STATUS')}

{to_stylish('Deal ID')}: {deal['deal_id']}
{to_stylish('Status')}: {status_text}

{to_stylish('Amount')}: ₹{deal['amount']}
{to_stylish('Buyer')}: {form_data.get('buyer', 'N/A')}
{to_stylish('Seller')}: {form_data.get('seller', 'N/A')}
{to_stylish('Created')}: {deal['created_at']}
{to_stylish('Detail')}: {form_data.get('deal_detail', 'N/A')[:50]}...

@KALYUGESCROWSERVICE
"""
    await update.message.reply_text(msg)

# ============ NEW DEAL FORM ============

async def new_deal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{to_stylish('KALYUG ESCROW DEAL FORM')}\n\n{to_stylish('Enter DEAL AMOUNT (max 12000)')}:")
    return FORM_AMOUNT

async def form_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.strip())
        if amount <= 0 or amount > MAX_DEAL_LIMIT:
            await update.message.reply_text(f"{to_stylish('Amount must be between 1 and')} {MAX_DEAL_LIMIT}!")
            return FORM_AMOUNT
        context.user_data['deal_data'] = {'amount': amount}
        await update.message.reply_text(f"{to_stylish('Enter BUYER username (with @)')}:")
        return FORM_BUYER
    except ValueError:
        await update.message.reply_text(f"{to_stylish('Please enter a valid number!')}")
        return FORM_AMOUNT

async def form_buyer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buyer = update.message.text.strip()
    if not buyer.startswith('@'):
        buyer = '@' + buyer
    context.user_data['deal_data']['buyer'] = buyer
    await update.message.reply_text(f"{to_stylish('Enter SELLER username (with @)')}:")
    return FORM_SELLER

async def form_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seller = update.message.text.strip()
    if not seller.startswith('@'):
        seller = '@' + seller
    context.user_data['deal_data']['seller'] = seller
    await update.message.reply_text(f"{to_stylish('Enter DEAL DETAILS')}:")
    return FORM_DEAL_DETAIL

async def form_deal_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['deal_detail'] = update.message.text.strip()
    await update.message.reply_text(f"{to_stylish('Enter RLS UPI')}:")
    return FORM_RLS_UPI

async def form_rls_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['rls_upi'] = update.message.text.strip()
    await update.message.reply_text(f"{to_stylish('Enter CONDITION')}:")
    return FORM_CONDITION

async def form_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['condition'] = update.message.text.strip()
    await update.message.reply_text(f"{to_stylish('Enter ESCROW TILL')}:")
    return FORM_ESCROW_TILL

async def form_escrow_till(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['deal_data']['escrow_till'] = update.message.text.strip()
    
    form_data = context.user_data['deal_data']
    formatted = format_deal_form(form_data)
    
    user = update.effective_user
    msg = await update.message.reply_text(f"{formatted}\n\n---\n{to_stylish('Waiting for admin approval...')}\n@admins {to_stylish('please approve!')}")
    
    form_id = save_pending_form(form_data, user.id, user.username or "", update.effective_chat.id, msg.message_id)
    
    admins = get_admins()
    for admin in admins:
        try:
            await context.bot.send_message(
                admin['user_id'],
                f"{to_stylish('NEW PENDING FORM!')}\n\n{formatted}\n\n{to_stylish('Form ID')}: {form_id}\n{to_stylish('User')}: @{user.username or user.first_name}\n\n{to_stylish('Use /admin to see pending forms!')}"
            )
        except:
            pass
    
    try:
        await context.bot.send_message(OWNER_ID, f"{to_stylish('NEW PENDING FORM!')}\n\n{formatted}\n\n{to_stylish('Form ID')}: {form_id}\n{to_stylish('User')}: @{user.username or user.first_name}")
    except:
        pass
    
    await update.message.reply_text(f"{to_stylish('Form submitted successfully!')}\n{to_stylish('Form ID')}: {form_id}\n\n{to_stylish('Waiting for admin approval...')}")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{to_stylish('Form cancelled.')}")
    context.user_data.clear()
    return ConversationHandler.END