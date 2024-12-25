# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from database.db import db
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import REFERRAL_CHANNELS, RefferalAmount as earnings_range, TASKS
from pyrogram.types import CallbackQuery

from pyrogram import enums
from pyrogram.errors import *

from utils import get_verify_shorted_link
async def is_user_joined_channel(client, user_id, channel):
    """
    Check if the user is a member of the specified Telegram channel.
    """
    try:
        user = await client.get_chat_member(channel, user_id)
        return True
    except UserNotParticipant:
        return False


@Client.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Check if the user is new and add to the database
    if not await db.is_user_exist(user_id):
        referrer = None
        if len(message.command) > 1:  # Check for referral link
            referrer = message.command[1]
            await db.add_user(user_id, first_name, referrer)
            try:
                await client.send_message(
                    referrer,
                    f"🎉 Great news! **{first_name}** has joined the bot using your referral link. Keep inviting to earn more rewards!"
                )
            except Exception as e:
                print(f"Error sending referral notification: {e}")
        else:
            await db.add_user(user_id, first_name)

    # Check if the user joined the required channels
    required_channels = [channel for channel in REFERRAL_CHANNELS if channel]
    for channel in required_channels:
        if not await is_user_joined_channel(client, user_id, channel):
            join_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{channel}")],
                [InlineKeyboardButton("✅ Check Membership", callback_data="check_membership")]
            ])
            await message.reply(
                (
                    "💡 **Action Required!**\n\n"
                    "To start using this bot and earn rewards, please join the required channels below.\n\n"
                    "After joining, click **Check Membership** to proceed."
                ),
                reply_markup=join_button
            )
            return

    # Main menu buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 View Wallet", callback_data="wallet"), InlineKeyboardButton("📤 Withdraw Funds", callback_data="withdraw")],
        [InlineKeyboardButton("🎯 Earn Money", callback_data="earn"), InlineKeyboardButton("👥 Referral Program", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"), InlineKeyboardButton("ℹ️ Help & Support", callback_data="help")],
        [InlineKeyboardButton("🛒 Use Balance (Premium/Recharges)", callback_data="use_balance")]
    ])

    # Welcome message
    welcome_message = (
        f"🎉 **Welcome, {first_name}!**\n\n"
        f"💵 **Start your journey to earning money effortlessly!**\n\n"
        f"Here's what you can do:\n"
        f"• Manage and track your wallet.\n"
        f"• Withdraw your earnings securely.\n"
        f"• Participate in exciting earning programs.\n"
        f"• Invite friends and earn extra rewards.\n"
        f"• Claim daily bonuses for additional income.\n"
        f"• Use your balance for exclusive services like Telegram Premium or mobile recharges.\n\n"
        f"🔔 **Note:** Fake or duplicate accounts are not allowed. If detected, you may be blocked from using this bot."
    )

    await message.reply(welcome_message, reply_markup=buttons)


@Client.on_callback_query(filters.regex("check_membership"))
async def check_membership(client, callback_query):
    user_id = callback_query.from_user.id
    required_channels =  [channel for channel in REFERRAL_CHANNELS if channel]
    
    # Check membership for all channels
    for channel in required_channels:
        if not await is_user_joined_channel(client, user_id, channel):
            await callback_query.answer("🚫 You have not joined all required channels.", show_alert=True)
            return

    # Membership confirmed
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 View Wallet", callback_data="wallet"), InlineKeyboardButton("📤 Withdraw Funds", callback_data="withdraw")],
        [InlineKeyboardButton("🎯 Earn Money", callback_data="earn"), InlineKeyboardButton("👥 Referral Program", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"), InlineKeyboardButton("ℹ️ Help & Support", callback_data="help")],
        [InlineKeyboardButton("🛒 Use Balance (Premium/Recharges)", callback_data="use_balance")]
    ])

    welcome_message = (
        "🎉 Welcome back!\n\n"
        "✅ You have successfully joined all required channels. Start exploring the features below and maximize your earnings:\n"
        "• Manage your wallet\n"
        "• Withdraw your earnings\n"
        "• Earn through our exciting programs\n"
        "• Invite friends to earn more rewards\n"
        "• Collect daily bonuses\n\n"
        "Happy earning!"
    )
    await callback_query.message.edit_text(welcome_message, reply_markup=buttons)

# Home Callback Handler
# Home Callback Handler
@Client.on_callback_query(filters.regex("home"))
async def home_callback(client, callback_query: CallbackQuery):
    first_name = callback_query.from_user.first_name

    # Re-create the start buttons    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 View Wallet", callback_data="wallet"), InlineKeyboardButton("📤 Withdraw Funds", callback_data="withdraw")],
        [InlineKeyboardButton("🎯 Earn Money", callback_data="earn"), InlineKeyboardButton("👥 Referral Program", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus"), InlineKeyboardButton("ℹ️ Help & Support", callback_data="help")],
        [InlineKeyboardButton("🛒 Use Balance (Premium/Recharges)", callback_data="use_balance")]
    ])

    welcome_message = (
        f"🎉 Welcome back, {first_name}!\n\n"
        f"💵 Explore the features below to manage your wallet and earnings:\n\n"
        f"• Manage your wallet\n"
        f"• Withdraw your earnings\n"
        f"• Earn through our exciting programs\n"
        f"• Invite friends to earn more rewards\n"
        f"• Collect daily bonuses\n\n"
        f"Let’s get started!"
    )

    # Edit the message back to home
    await callback_query.message.edit_text(welcome_message, reply_markup=buttons)


@Client.on_callback_query(filters.regex("use_balance"))
async def use_balance(client, callback_query):
    user_id = callback_query.from_user.id
    balance = await db.get_balance(user_id)

    if balance and balance > 0:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Buy Telegram Premium", callback_data="buy_premium")],
            [InlineKeyboardButton("📱 Recharge Mobile", callback_data="recharge_mobile")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ])
        await callback_query.message.edit_text(
            f"💳 **Your Wallet Balance:** ₹{balance:.2f}\n\n"
            f"🛍️ Use your balance for the following services:\n"
            f"1. Purchase Telegram Premium.\n"
            f"2. Recharge your mobile number.\n\n"
            f"Choose an option below to proceed.",
            reply_markup=buttons
        )
    else:
        await callback_query.answer("❌ You have insufficient balance to use this feature.", show_alert=True)






# Wallet Callback Handler
@Client.on_callback_query(filters.regex("wallet"))
async def wallet_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    # Fetch user's wallet balance from the database
    balance = await db.get_balance(user_id)
    balance = balance if balance is not None else 0.0  # Default to 0.0 if no balance found

    # Wallet information
    wallet_message = (
        f"💳 **Your Wallet**\n\n"
        f"💰 Current Balance: ₹{balance:.2f}\n\n"
        f"Use the buttons below to navigate."
    )

    # Buttons for navigation
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Home", callback_data="home")]
    ])

    # Edit the message with wallet info
    await callback_query.message.edit_text(wallet_message, reply_markup=buttons)





@Client.on_callback_query(filters.regex("referral"))
async def referral_program_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name

    # Generate the referral link
    bot_username = (await client.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    rflink = f"https://t.me/{bot_username}?start={user_id}"

    # Referral message with notice
    referral_message = (
        f"👥 **Referral Program**\n\n"
        f"Earn {earnings_range} for every user who joins using your referral link and completes the tasks.\n\n"
        f"🔗 **Your Referral Link:**\n"
        f"[{referral_link}]({referral_link})\n\n"
        f"💡 Share this link with your friends and start earning now!\n"
        f"🚀 The more you invite, the more you earn!\n\n"
        f"⚠️ **Notice:**\n"
        f"Please don't use fake accounts to invite yourself. If we detect fraudulent activity, you will be permanently banned from using the bot."
    )
    share_url =f"https://t.me/share/url?url=%F0%9F%94%A5%20I%27m%20earning%20daily%20%E2%82%B910-%E2%82%B920%20by%20completing%20tasks%20on%20this%20amazing%20bot%21%20%F0%9F%A4%91%20%20%0A%0A%F0%9F%92%B5%20Earn%20extra%20rewards%20by%20inviting%20your%20friends%21%20Use%20my%20referral%20link%20to%20start%3A%20%20%0A%0A%F0%9F%91%89%20{rflink}%20%20%0A%0AStart%20your%20earnings%20today%21"
    # Buttons for sharing and navigating
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Share Referral", url=share_url)],
        [InlineKeyboardButton("🔙 Back to Home", callback_data="home")]
    ])

    # Edit the message with referral info
    await callback_query.message.edit_text(referral_message, reply_markup=buttons, disable_web_page_preview=True)




from math import ceil

@Client.on_callback_query(filters.regex("earn"))
async def earn_money_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    # Pagination setup
    tasks_per_page = 4
    page = int(callback_query.data.split("_")[-1]) if "_" in callback_query.data else 1
    total_tasks = len(TASKS)
    total_pages = ceil(total_tasks / tasks_per_page)
    start_index = (page - 1) * tasks_per_page
    end_index = start_index + tasks_per_page

    # Generate task buttons
    task_buttons = [
        InlineKeyboardButton(
            f"💼 Task {i+1}",
            callback_data=f"task_{i+1}"
        )
        for i in range(start_index, min(end_index, total_tasks))
    ]

    # Arrange buttons in 2x2 format
    task_rows = [task_buttons[i:i+2] for i in range(0, len(task_buttons), 2)]

    # Navigation buttons
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"earn_{page - 1}"))
    if page < total_pages:
        navigation_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"earn_{page + 1}"))

    # Combine all buttons
    buttons = InlineKeyboardMarkup(task_rows + [navigation_buttons] if navigation_buttons else task_rows)

    # Message about earning
    earn_message = (
        "💰 **Earn Money**\n\n"
        "📋 Here are the tasks you can complete to earn money:\n\n"
        "✅ Per task, you will earn up to ₹1.\n"
        f"💼 Total available tasks: {total_tasks}\n\n"
        "Click on a task to start earning!"
    )

    await callback_query.message.edit_text(earn_message, reply_markup=buttons)


@Client.on_callback_query(filters.regex(r"task_\d+"))
async def handle_task_callback(client, callback_query: CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])  # Extract task ID from callback data
    task_data = TASKS[task_id - 1]  # Adjust for 0-based indexing
    task_name = task_data["name"]
    site_link = task_data["link"]
    site_api = task_data["api"]
    verify_link = f"t.me/botxhub"
    task_link = await get_verify_shorted_link(verify_link, site_link, site_api)

    # Respond with task details
    await callback_query.message.edit_text(
        f"📝 **Task {task_id}: {task_name}**\n\n"
        "Complete this task to earn ₹1. Follow the instructions below:\n\n"
        "1️⃣ Click **Complete Task** to perform the task.\n"
        "2️⃣ If you're unsure, click **How to Complete** for detailed instructions.\n\n"
        "⚡ Once done, your earnings will be credited!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Complete Task", url=task_link)],  # Button to perform the task
            [InlineKeyboardButton("❓ How to Complete", url=task_api)],  # Button for task instructions
            [InlineKeyboardButton("🔙 Back to Tasks", callback_data="earn_1")]  # Button to go back to tasks
        ])
    )





from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from datetime import datetime

@Client.on_callback_query(filters.regex(r"withdraw"))
async def withdraw_callback(client, callback_query):
    user_id = callback_query.from_user.id

    # Fetch the user's balance
    balance = await db.get_balance(user_id)
    if balance < 5:
        # Inform the user if balance is insufficient
        await callback_query.message.edit_text(
            "💸 **Insufficient Balance!**\n\n"
            "You need at least ₹5 in your wallet to make a withdrawal.\n"
            "👉 Complete tasks to increase your balance and qualify for withdrawals.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 Earn Money", callback_data="earn")]
            ])
        )
        return

    # Check if UPI is saved
    user_data = await db.users_col.find_one({"id": user_id})
    user_upi = user_data.get("upi") if user_data else None

    if not user_upi:
        # If no UPI is saved, prompt to add one
        await callback_query.message.edit_text(
            "🏦 **No UPI ID Found!**\n\n"
            "Please add your UPI ID to proceed with the withdrawal.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add UPI ID", callback_data="add_upi")]
            ])
        )
        return

    # If UPI is saved, show options
    await callback_query.message.edit_text(
        f"🏦 **Withdraw to UPI ID:**\n\n"
        f"📌 **Current UPI:** `{user_upi}`\n\n"
        "Select your UPI ID to send the withdrawal request.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(user_upi, callback_data="confirm_withdraw")],
            [InlineKeyboardButton("✏️ Change UPI ID", callback_data="change_upi")]
        ])
    )


# Handler for Adding a New UPI ID
@Client.on_callback_query(filters.regex(r"add_upi"))
async def add_upi_callback(client, callback_query):
    user_id = callback_query.from_user.id

    # Ask user for UPI ID
    await client.ask(
        callback_query.message.chat.id,
        "🏦 **Add UPI ID**\n\n"
        "Please send your UPI ID in the format `mobilenumber@upi` or `mobilenumber@ybl`.\n\n"
        "❗️ Ensure the UPI ID is valid and linked to your account.",
        filters=filters.text,
        reply_to_message_id=callback_query.message.message_id
    )

    async def validate_upi(user, text):
        if "@" not in text or not text.split("@")[0].isdigit() or len(text.split("@")[0]) != 10:
            await client.send_message(user, "❌ Invalid UPI ID! Please try again.")
            return False

        # Check if UPI ID is already in DB
        upi_exists = await db.users_col.find_one({"upi": text})
        if upi_exists:
            await client.send_message(
                user,
                "❌ This UPI ID is already linked to another account.\n\n"
                "Each UPI ID can only be linked to one account."
            )
            return False
        return text

    upi_id = await validate_upi(callback_query.message.chat.id, callback_query.data)
    if upi_id:
        await db.users_col.update_one({"id": user_id}, {"$set": {"upi": upi_id}})
        await callback_query.message.edit_text(
            "✅ **UPI ID Added Successfully!**\n\n"
            "You can now request withdrawals."
        )


# Handler for Changing UPI ID
@Client.on_callback_query(filters.regex(r"change_upi"))
async def change_upi_callback(client, callback_query):
    user_id = callback_query.from_user.id

    await callback_query.message.edit_text(
        "⚠️ **Change UPI ID Confirmation**\n\n"
        "If you change your UPI ID, your wallet balance will be reset to ₹0.\n\n"
        "Do you want to proceed?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm_change_upi")],
            [InlineKeyboardButton("❌ Cancel", callback_data="withdraw")]
        ])
    )


@Client.on_callback_query(filters.regex(r"confirm_change_upi"))
async def confirm_change_upi(client, callback_query):
    user_id = callback_query.from_user.id

    # Reset wallet balance and ask for a new UPI ID
    await db.wallet_col.update_one({"id": user_id}, {"$set": {"balance": 0}})
    await client.ask(
        callback_query.message.chat.id,
        "🏦 **Change UPI ID**\n\n"
        "Please send your new UPI ID in the format `mobilenumber@upi` or `mobilenumber@ybl`.",
        filters=filters.text,
        reply_to_message_id=callback_query.message.message_id
    )


# Handler for Confirming Withdrawal
@Client.on_callback_query(filters.regex(r"confirm_withdraw"))
async def confirm_withdraw_callback(client, callback_query):
    user_id = callback_query.from_user.id
    balance = await db.get_balance(user_id)

    await client.ask(
        callback_query.message.chat.id,
        f"💸 **Withdrawal Request**\n\n"
        f"Your current balance: ₹{balance}\n\n"
        "Enter the amount you want to withdraw.",
        filters=filters.text,
        reply_to_message_id=callback_query.message.message_id
    )

    async def process_withdraw_request(user, text):
        try:
            amount = float(text)
        except ValueError:
            await client.send_message(user, "❌ Invalid amount! Please try again.")
            return False

        if amount > balance:
            await client.send_message(
                user,
                f"❌ Insufficient Balance! You only have ₹{balance}."
            )
            return False

        if amount < 5:
            await client.send_message(
                user,
                "❌ Minimum withdrawal amount is ₹5. Please try again."
            )
            return False

        # Send withdrawal request to log channel
        log_channel_id = -1001234567890  # Replace with your channel ID
        upi = await db.users_col.find_one({"id": user_id}, {"upi": 1})["upi"]
        await client.send_message(
            log_channel_id,
            f"💸 **New Withdrawal Request**\n\n"
            f"👤 User ID: {user_id}\n"
            f"📱 UPI ID: {upi}\n"
            f"💰 Amount: ₹{amount}\n"
            f"🕒 Requested at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Deduct balance
        await db.withdraw_coin(amount, user_id)
        await client.send_message(
            user,
            "✅ **Withdrawal Request Submitted!**\n\n"
            "Your request has been submitted and will be processed shortly."
        )


@Client.on_callback_query(filters.regex(r"daily_bonus"))
async def daily_bonus_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    
    # Example check if the user has completed daily tasks (you may replace this with actual DB check)
    tasks_completed_today = 10 #await db.get_completed_tasks(user_id)  # Function to get tasks completed today (to be implemented)
    required_tasks = 50  # Define how many tasks are required to get the bonus

    # Check if user has completed enough tasks
    if tasks_completed_today < required_tasks:
        # If the user hasn't completed enough tasks, inform them
        message = (
            "😞 **Sorry! You didn't get any bonus.**\n\n"
            "Your task status is too low. Complete your daily tasks on time to earn ₹3-5 in daily bonuses.\n\n"
            "✅ Complete all daily tasks to unlock your bonus!"
        )
        await callback_query.message.edit_text(message)
    else:
        # If the user has completed enough tasks, reward them
        bonus_amount = 3  # You can adjust this based on the completed tasks
        # Add bonus amount to the user's wallet (You can implement this with your DB logic)
      #  await db.add_wallet_balance(user_id, bonus_amount)

     #   message = (
      #      f"🎉 **Congrats! You have received a ₹{bonus_amount} bonus!**\n\n"
     #       "Well done for completing the daily tasks. Keep it up to earn more bonuses every day!"
      #  )
     #   await callback_query.message.edit_text(message)

