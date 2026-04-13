import discord
from discord.ext import commands
import os

# ---------- CONFIG ----------
GUILD_ID = 1491802017851769065
TESTER_ROLE_NAME = "Testers"
MAX_PLAYERS = 10

RESULT_CHANNEL = 1491828092946350191
TICKET_CATEGORY_ID = 1491835386081837177

CHANNELS = {
    "Sword": 1491827421480222900,
    "DiaPot": 1491833787770863778,
    "NethPot": 1491833200161591527,
    "Axe": 1491833874911854722,
    "Crystal": 1493205644579180594,
    "DiaSMP": 1493237939222876261,
    "SMP": 1493237981480488970,
    "Mace": 1493238029312331899
}

POINTS = {
    "LT5": 1, "HT5": 3,
    "LT4": 5, "HT4": 8,
    "LT3": 12, "HT3": 15,
    "LT2": 20, "HT2": 25,
    "LT1": 30, "HT1": 35
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
current_mode = None
panel_owner = None
queue_message = {}

# ---------- CHECK TESTER ----------
def is_tester(interaction):
    return any(role.name == TESTER_ROLE_NAME for role in interaction.user.roles)


# =========================================================
#                       QUEUE SYSTEM
# =========================================================

def build_embed():
    embed = discord.Embed(
        title=f"⚔ {current_mode} Queue",
        color=0x4aa3ff
    )

    if not queue:
        embed.add_field(name="Queue", value="Empty", inline=False)
    else:
        embed.add_field(
            name=f"Queue ({len(queue)}/10)",
            value="\n".join([u.mention for u in queue]),
            inline=False
        )

    embed.add_field(name="Tester", value=panel_owner.mention if panel_owner else "None", inline=False)
    return embed


class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.primary)
    async def join(self, interaction, button):
        if interaction.user in queue:
            return await interaction.response.send_message("Already in queue", ephemeral=True)

        if len(queue) >= MAX_PLAYERS:
            return await interaction.response.send_message("Queue full", ephemeral=True)

        queue.append(interaction.user)
        await interaction.response.send_message("Joined ✔", ephemeral=True)
        await update_queue()

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.secondary)
    async def leave(self, interaction, button):
        if interaction.user in queue:
            queue.remove(interaction.user)
            await interaction.response.send_message("Left ✔", ephemeral=True)

        await update_queue()


async def update_queue():
    channel = bot.get_channel(CHANNELS[current_mode])
    msg_id = queue_message.get(current_mode)

    if msg_id:
        try:
            msg = await channel.fetch_message(msg_id)
            await msg.edit(embed=build_embed(), view=QueueView())
            return
        except:
            pass

    msg = await channel.send(embed=build_embed(), view=QueueView())
    queue_message[current_mode] = msg.id


async def open_panel(interaction, mode):
    global current_mode, panel_owner, queue

    current_mode = mode
    panel_owner = interaction.user
    queue = []

    channel = bot.get_channel(CHANNELS[mode])

    await channel.send(
        f"@here 💙 **{mode} Queue Opened**",
        allowed_mentions=discord.AllowedMentions(everyone=True),
        view=QueueView()
    )

    await update_queue()
    await interaction.response.send_message("Queue opened ✔", ephemeral=True)


# =========================================================
#                       RESULT SYSTEM
# =========================================================

@bot.tree.command(name="result", guild=discord.Object(id=GUILD_ID))
async def result(interaction, member: discord.Member, gamemode: str, tier: str, ign: str, tester: discord.Member):

    if not is_tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)

    tier = tier.upper()
    if tier not in POINTS:
        return await interaction.response.send_message("Invalid tier", ephemeral=True)

    embed = discord.Embed(title="⚔ Match Result", color=0x4aa3ff)

    embed.description = (
        f"{member.mention}\n\n"
        f"**IGN:** {ign}\n"
        f"**Tier:** {tier}\n"
        f"**Points:** {POINTS[tier]}\n"
        f"**Gamemode:** {gamemode}\n"
        f"**Tester:** {tester.mention}"
    )

    channel = bot.get_channel(RESULT_CHANNEL)
    await channel.send(embed=embed)

    await interaction.response.send_message("Result sent ✔", ephemeral=True)


# =========================================================
#                       TICKET SYSTEM (FIXED)
# =========================================================

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction, ttype):
        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}-{ttype}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket Opened",
            description=f"Type: **{ttype}**\n\nExplain your issue below.",
            color=0x4aa3ff
        )

        await channel.send(content=user.mention, embed=embed)

        await interaction.response.send_message(
            f"Ticket created: {channel.mention}",
            ephemeral=True
        )

    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary)
    async def support(self, interaction, button):
        await self.create_ticket(interaction, "Support")

    @discord.ui.button(label="Partnership", style=discord.ButtonStyle.success)
    async def partner(self, interaction, button):
        await self.create_ticket(interaction, "Partnership")

    @discord.ui.button(label="Rank Purchase", style=discord.ButtonStyle.danger)
    async def rank(self, interaction, button):
        await self.create_ticket(interaction, "Rank Purchase")


@bot.tree.command(name="ticket_add_tick", guild=discord.Object(id=GUILD_ID))
async def ticket_add_tick(interaction):

    if not is_tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)

    embed = discord.Embed(
        title="🎫 Ticket System",
        description="Click below to open a private ticket",
        color=0x4aa3ff
    )

    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Ticket panel sent ✔", ephemeral=True)


# =========================================================
#                       QUEUE COMMANDS
# =========================================================

def tester(interaction):
    return is_tester(interaction)


@bot.tree.command(name="opensword", guild=discord.Object(id=GUILD_ID))
async def opensword(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Sword")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))


bot.run(os.getenv("TOKEN"))
