import json

STYLISH = {
    'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅',
    'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉', 'K': '𝐊', 'L': '𝐋',
    'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑',
    'S': '𝐒', 'T': '𝐓', 'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗',
    'Y': '𝐘', 'Z': '𝐙',
    'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟',
    'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣', 'k': '𝐤', 'l': '𝐥',
    'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫',
    's': '𝐬', 't': '𝐭', 'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱',
    'y': '𝐲', 'z': '𝐳',
    '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
    '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
}

def to_stylish(text):
    result = ""
    for char in text:
        if char in STYLISH:
            result += STYLISH[char]
        else:
            result += char
    return result

def format_deal_form(form_data):
    return f"""
{to_stylish('KALYUG ESCROW DEAL FORM')}

{to_stylish('DEAL AMOUNT')} :- {form_data.get('amount', 'N/A')}

{to_stylish('BUYERS')} :- {form_data.get('buyer', 'N/A')}

{to_stylish('SELLER')} :- {form_data.get('seller', 'N/A')}

{to_stylish('DEAL DETAIL')} :- {form_data.get('deal_detail', 'N/A')}

{to_stylish('RLS UPI')} :- {form_data.get('rls_upi', 'N/A')}

{to_stylish('CONDITION')} :- {form_data.get('condition', 'N/A')}

{to_stylish('ESCROW TILL')} :- {form_data.get('escrow_till', 'N/A')}

{to_stylish('ESCROW FEES IS NON - REFUNDABLE NO MATTER IF THE DEAL GETS CANCELLED.')}
{to_stylish('RG')} : @KALYUGESCROWSERVICE
"""

def format_deal_message(deal, action):
    form_data = json.loads(deal['form_data'])
    buyer = form_data.get('buyer', '').replace('@', '')
    seller = form_data.get('seller', '').replace('@', '')
    
    if action == 'payment':
        return f"""
{to_stylish('PAYMENT RECEIVED')}

@{buyer}
@{seller}

{to_stylish('Deal Amount')}: {deal['amount']}

{to_stylish('Continue your deal!')}

@KALYUGESCROWSERVICE
"""
    elif action == 'cancel':
        return f"""
{to_stylish('DEAL CANCELLED')}

@{buyer}
@{seller}

{to_stylish('Deal has been cancelled!')}

@KALYUGESCROWSERVICE
"""
    elif action == 'hold':
        return f"""
{to_stylish('DEAL ON HOLD')}

{to_stylish('Deal ID')}: {deal['deal_id']}

@{buyer}
@{seller}

@KALYUGESCROWSERVICE
"""
    return ""