import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7382522475:AAFjdLm1MxCTUFgHKYC3O4zgzw0e9MQmEzw")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "5461760"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "396b10bcf5e1ed5fcc71f1603800b7cf")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "6521935712"))

# Your Mongodb Database Url
DB_URI = os.environ.get("DB_URI", "mongodb+srv://sidbotz:s8dnBTTboTdkLIHz@cluster0.ygk8a.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "EarningBot")

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

REFERRAL_CHANNELS = "botxhub"
RefferalAmount = os.environ.get("RefferalAmount", "Upto 5 ₹")

# Configuration for tasks (update as per your bot setup)
TASKS = [
    "Complete Survey on XYZ",
    "Watch a Video on ABC",
    "Sign Up on DEF",
    "Play Game on GHI",
    "Install App from JKL",
    "Follow Channel MNO",
]
