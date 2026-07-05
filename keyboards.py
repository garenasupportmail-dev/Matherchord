from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import to_stylish

def get_deal_buttons(deal_id):
    """3 buttons: Payment Received, Hold Deal, Cancel Deal"""
    keyboard = [
        [
            InlineKeyboardButton(f"{to_stylish('Payment Received')}", callback_data=f"pay_{deal_id}"),
        ],
        [
            InlineKeyboardButton(f"{to_stylish('Hold Deal')}", callback_data=f"hold_{deal_id}"),
            InlineKeyboardButton(f"{to_stylish('Cancel Deal')}", callback_data=f"cancel_{deal_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_panel_buttons():
    keyboard = [
        [InlineKeyboardButton(f"{to_stylish('All Deals')}", callback_data="admin_deals")],
        [InlineKeyboardButton(f"{to_stylish('Pending Deals')}", callback_data="admin_pending")],
        [InlineKeyboardButton(f"{to_stylish('Admins List')}", callback_data="admin_list")],
        [InlineKeyboardButton(f"{to_stylish('Deal Status')}", callback_data="admin_status")],
        [InlineKeyboardButton(f"{to_stylish('Pending Forms')}", callback_data="admin_forms")],
        [InlineKeyboardButton(f"{to_stylish('Back')}", callback_data="admin_back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{to_stylish('Back')}", callback_data="admin_back")]
    ])

def get_main_menu(is_admin_user=False):
    keyboard = []
    if is_admin_user:
        keyboard.append([InlineKeyboardButton(f"{to_stylish('New Deal Form')}", callback_data="new_deal")])
    keyboard.append([InlineKeyboardButton(f"{to_stylish('Admin Panel')}", callback_data="admin_panel")])
    keyboard.append([InlineKeyboardButton(f"{to_stylish('Help')}", callback_data="help")])
    return InlineKeyboardMarkup(keyboard)

def get_approve_buttons(form_id):
    keyboard = [
        [
            InlineKeyboardButton(f"{to_stylish('BOTH AGREE - CREATE DEAL')}", callback_data=f"approve_{form_id}"),
            InlineKeyboardButton(f"{to_stylish('REJECT FORM')}", callback_data=f"reject_{form_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)