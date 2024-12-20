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
from config import REFERRAL_CHANNELS  # List of channels (chnl, chnll, chnlll)

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
    required_channels = [channel for channel in REFERRAL_CHANNELS if channel]

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
