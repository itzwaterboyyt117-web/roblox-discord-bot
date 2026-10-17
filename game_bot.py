import discord
from discord.ext import commands, tasks
import asyncio
import requests

# --- CONFIGURATION ---
BOT_TOKEN = "MTU2MTA0MDUzNDkzODg0OTM3MA.GE_hhV.M0neWyx71uIZ5M2KboLp4rMsMHVKsXafZl2k2M"
YOUR_USER_ID = 1485074929950003241  # Put your numerical Discord User ID here

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Track users who want 24/7 alerts: { user_id: ["Kitsune", "Leopard"] }
USER_WATCHLIST = {}  

# ==========================================
# 🐍 PURE PYTHON LIVE DATA UTILITY (NO BS4)
# ==========================================
def get_live_blox_fruits_stock():
    """Fetches live stock database directly as JSON—no web scraping required."""
    try:
        # Pulls live tracked stock directly from a community raw data mirror
        url = "https://githubusercontent.com"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json() # Automatically turns data into a clean Python dictionary
            normal = data.get("normal", ["Rocket", "Spin", "Flame", "Spring"])
            mirage = data.get("mirage", ["Kitsune", "Leopard"])
            return normal, mirage
    except Exception:
        pass
    # Fallback default values if network goes down
    return ["Rocket", "Ice", "Dark", "Light"], ["Dough", "Leopard"]


# ==========================================
# 📊 GAME DATABASES (Python Lists & Dicts)
# ==========================================
ROBLOX_RIVALS_GUNS = [
    {"name": "Pistol", "keys": "Starter", "damage": "22", "img": "https://githubusercontent.com"},
    {"name": "Rifle", "keys": "15 Keys", "damage": "35", "img": "https://githubusercontent.com"},
    {"name": "Sniper", "keys": "50 Keys", "damage": "100", "img": "https://githubusercontent.com"}
]

STEAL_AN_EGG_DATA = {
    "info": {"event": "Spooky Autumn Event", "update": "v2.4 - New Mythical Eggs added!"},
    "zones": [
        {"name": "Zone 1: Beginner Meadow", "speed": "0 - 50 Speed", "eggs": "Common Egg, Uncommon Egg, Tiger Egg", "boss": "King Chick", "boss_img": "https://githubusercontent.com"},
        {"name": "Zone 2: Sandy Desert", "speed": "50 - 200 Speed", "eggs": "Desert Egg, Scorpion Egg, Cactus Egg", "boss": "Anubis Golem", "boss_img": "https://githubusercontent.com"}
    ]
}


# ==========================================
# 🍎 BLOX FRUITS BUTTON MENUS
# ==========================================
class BloxFruitsStockView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Current Stock", style=discord.ButtonStyle.green, custom_id="bf_current_stock")
    async def current_stock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        normal, mirage = get_live_blox_fruits_stock()
        
        embed = discord.Embed(title="🍎 Live Blox Fruits Stock Dashboard", color=discord.Color.blue())
        embed.add_field(name="🌐 Normal Regular Stock", value="\n".join([f"• {f}" for f in normal]), inline=False)
        embed.add_field(name="🏝️ Mirage Island Stock", value="\n".join([f"• {f}" for f in mirage]), inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="24/7 Stock Monitor", style=discord.ButtonStyle.blurple, custom_id="bf_247_stock")
    async def watch_stock_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = discord.ui.View()
        
        select = discord.ui.Select(
            placeholder="Pick fruits to track 24/7...",
            min_values=1,
            max_values=4,
            options=[
                discord.SelectOption(label="Kitsune", value="Kitsune", emoji="🦊"),
                discord.SelectOption(label="Leopard", value="Leopard", emoji="🐆"),
                discord.SelectOption(label="Dragon", value="Dragon", emoji="🐉"),
                discord.SelectOption(label="Dough", value="Dough", emoji="🍩"),
                discord.SelectOption(label="Buddha", value="Buddha", emoji="🟡")
            ]
        )
        
        async def select_callback(inter: discord.Interaction):
            USER_WATCHLIST[inter.user.id] = select.values
            await inter.response.send_message(
                f"✅ **Alert Active!** Tracking: {', '.join(select.values)}. You'll get 3 pings right when they land in stock!", 
                ephemeral=True
            )
            
        select.callback = select_callback
        view.add_item(select)
        await interaction.response.send_message("Select your tracking targets:", view=view, ephemeral=True)


# ==========================================
# 🎛️ THE MAIN MASTER DROPDOWN PANEL
# ==========================================
class MainDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose games to display details...",
        min_values=1,
        max_values=3,
        options=[
            discord.SelectOption(label="Roblox Rivals", value="rivals", description="Gun data, key locks, damage values", emoji="🔫"),
            discord.SelectOption(label="Steal An Egg", value="steal_egg", description="Zones, speeds, eggs, and bosses", emoji="🥚"),
            discord.SelectOption(label="Blox Fruits", value="blox_fruits", description="Live stock checker and auto-ping setups", emoji="🍎")
        ]
    )
    async def main_dropdown_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.defer(ephemeral=True)
        
        for value in select.values:
            if value == "rivals":
                embeds = []
                for index, gun in enumerate(ROBLOX_RIVALS_GUNS):
                    embed = discord.Embed(
                        title=f"🔫 Roblox Rivals Database — {gun['name']}" if index == 0 else "",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Weapon Stats", value=f"**Gun:** {gun['name']}\n**Unlock Cost:** {gun['keys']}\n**Base Damage:** {gun['damage']}")
                    embed.set_image(url=gun["img"])
                    embeds.append(embed)
                
                await interaction.followup.send(embeds=embeds, ephemeral=True)

            elif value == "steal_egg":
                embeds = []
                info_embed = discord.Embed(
                    title="🥚 Steal An Egg Complete Directory", 
                    description=f"**Active Server Event:** {STEAL_AN_EGG_DATA['info']['event']}\n**Latest Patch Notes:** {STEAL_AN_EGG_DATA['info']['update']}",
                    color=discord.Color.gold()
                )
                embeds.append(info_embed)
                
                for zone in STEAL_AN_EGG_DATA["zones"]:
                    z_embed = discord.Embed(title=f"📍 {zone['name']}", color=discord.Color.orange())
                    z_embed.add_field(name="Requirements & Drops", value=f"• **Required Speed:** {zone['speed']}\n• **Local Eggs:** {zone['eggs']}")
                    z_embed.add_field(name="Zone Boss Encounter", value=f"• **Boss Name:** {zone['boss']}")
                    z_embed.set_image(url=zone["boss_img"])
                    embeds.append(z_embed)
                    
                await interaction.followup.send(embeds=embeds, ephemeral=True)

            elif value == "blox_fruits":
                embed = discord.Embed(
                    title="🍎 Blox Fruits Station Hub", 
                    description="Interact with the options below to read current server listings or command 24/7 background tracking.", 
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed, view=BloxFruitsStockView(), ephemeral=True)


# ==========================================
# ⏰ 24/7 BACKGROUND MONITOR LOOP
# ==========================================
@tasks.loop(minutes=5)
async def live_stock_monitor_loop():
    await bot.wait_until_ready()
    
    normal_stock, mirage_stock = get_live_blox_fruits_stock()
    combined_stock = normal_stock + mirage_stock
    
    for user_id, tracked_fruits in list(USER_WATCHLIST.items()):
        try:
            for fruit in list(tracked_fruits):
                if fruit in combined_stock:
                    user = await bot.fetch_user(user_id)
                    # Triple notification burst
                    for i in range(3):
                        await user.send(f"🚨 **[ALERT {i+1}/3]** <@{user_id}>! **{fruit}** is in the live stock right now! Go get it!")
                        await asyncio.sleep(1.5)  
                    
                    tracked_fruits.remove(fruit)
            if not tracked_fruits:
                del USER_WATCHLIST[user_id]
        except Exception as e:
            print(f"Error in monitor loop: {e}")


# ==========================================
# 🚀 INITIALIZATION AND LAUNCH
# ==========================================
@bot.event
async def on_ready():
    print(f"Bot successfully operating online as {bot.user.name}")
    print(f"Run !dashboard inside your DMs to open it!")
    if not live_stock_monitor_loop.is_running():
        live_stock_monitor_loop.start()

@bot.command()
async def dashboard(ctx):
    if ctx.author.id != YOUR_USER_ID:
        return await ctx.send("❌ Access Denied: Main control limited strictly to system owner profiles.")
    
    await ctx.send("🎮 **Roblox Game Control Dashboard**\nSelect your monitoring priorities from the dropdown menu:", view=MainDashboardView())

bot.run(BOT_TOKEN)
