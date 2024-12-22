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


async def is_user_joined_channel(client, user_id, channel):
    """
    Check if the user is a member of the specified Telegram channel.
    """
    try:
        user_status = await client.get_chat_member(chat_id=channel, user_id=user_id)
        return user_status.status in ["member", "administrator", "creator"]
    except:
        # If the bot cannot fetch user status (e.g., user blocked the bot or channel is private)
        return False


@Client.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Check if user is new and add to DB
    if not await db.is_user_exist(user_id):
        referrer = None
        # Check if user started from a referral link
        if len(message.command) > 1:
            referrer = message.command[1]
            await db.add_user(user_id, first_name, referrer)
            try:
                await client.send_message(
                    referrer,
                    f"🎉 Great news! {first_name} has joined the bot using your referral link. Keep inviting to earn more rewards!"
                )
            except:
                pass
        else:
            await db.add_user(user_id, first_name)

    # Check if user joined channels
    required_channels = [channel for channel in REFERRAL_CHANNELS if channel]
    for channel in required_channels:
        if not await is_user_joined_channel(client, user_id, channel):
            join_button = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{channel}")],
                [InlineKeyboardButton("✅ Check Membership", callback_data="check_membership")]
            ])
            await message.reply(
                "💡 To start using this bot and earn rewards, please join the required channels below.\n"
                "After joining, click **Check Membership** to proceed.",
                reply_markup=join_button
            )
            return

    # Welcome message with buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Your Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📤 Withdrawal", callback_data="withdraw")],
        [InlineKeyboardButton("🎯 Earn Money", callback_data="earn")],
        [InlineKeyboardButton("👥 Referral Program", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")]
    ])
    welcome_message = (
        f"🎉 Welcome, {first_name}!\n\n"
        f"💵 This bot helps you earn money without any investment. Start earning today and explore the features below:\n\nn"
        f"• Manage your wallet\n"
        f"• Withdraw your earnings\n"
        f"• Earn through our exciting programs\n"
        f"• Invite friends to earn more rewards\n"
        f"• Collect daily bonuses\n\n"
        f"Let’s get started!"
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
        [InlineKeyboardButton("💰 Your Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📤 Withdrawal", callback_data="withdraw")],
        [InlineKeyboardButton("🎯 Earn Money", callback_data="earn")],
        [InlineKeyboardButton("👥 Referral Program", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")]
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
        [InlineKeyboardButton("💰 Your Wallet", callback_data="wallet")],
        [InlineKeyboardButton("📤 Withdrawal", callback_data="withdraw")],
        [InlineKeyboardButton("🎯 Earn Money", callback_data="earn")],
        [InlineKeyboardButton("👥 Referral Program", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")]
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

    # Share text for referral
    share_text = (
        f"🔥 I'm earning daily ₹10-₹20 by completing tasks on this amazing bot! 🤑\n\n"
        f"💵 Earn extra rewards by inviting your friends! Use my referral link to start:\n\n"
        f"👉 {referral_link}\n\n"
        f"Start your earnings today!"
    )

    # Buttons for sharing and navigating
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Share Referral", url=f"https://t.me/share/url?url={referral_link}&text={share_text}")],
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

# Example handler for task button (add logic for each task)
@Client.on_callback_query(filters.regex(r"task_\d+"))
async def handle_task_callback(client, callback_query: CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])
    task_name = TASKS[task_id - 1]  # Adjust for 0-based indexing

    # Respond with task details
    await callback_query.message.edit_text(
        f"📝 **Task {task_id}: {task_name}**\n\n"
        "Complete this task to earn ₹1. Follow the instructions and complete it to start earning!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Tasks", callback_data="earn_1")]
        ])
    )

