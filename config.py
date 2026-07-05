import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set!")

OWNER_ID = int(os.environ.get('OWNER_ID', 8986441675))
CHANNEL_USERNAME = os.environ.get('CHANNEL_USERNAME', "@KALYUGESCROWSERVICE")
MAX_DEAL_LIMIT = 12000
DB_PATH = "data/escrow.db"