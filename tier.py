import discord
from discord.ext import commands
import os

# ---------- CONFIG ----------
GUILD_ID = 1491802017851769065
TESTER_ROLE_NAME = "Testers"
MAX_PLAYERS = 10

RESULT_CHANNEL = 1491828092946350191

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
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
current_mode = None
panel_owner = None
queue_message = {}


# ---------- TESTER CHECK ----------
def is_tester(interaction):
    return any(role.name == TESTER_ROLE_NAME for role in interaction.user.roles)


# ---------- QUEUE EMBED ----------
def build_embed():
    embed = discord.Embed(
        title=f"⚔ {current_mode} Queue",
        description=f"{current_mode} Tier Testing (Max {MAX_PLAYERS})",
        color=0x4aa3ff
    )

    if len(queue) == 0:
        embed.add_field(name="Queue (0/10)", value="Empty", inline=False)
    else:
        embed.add_field(
            name=f"Queue ({len(queue)}/10)",
            value="\n".join(f"{i+1}. {u.mention} ({u.display_name})"
                            for i, u in enumerate(queue)),
            inline=False
        )

    embed.add_field(
        name="Tester",
        value=panel_owner.mention if panel_owner else "None",
        inline=False
    )

    return embed


# ---------- QUEUE BUTTONS ----------
class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in queue:
            return await interaction.response.send_message("Already in queue", ephemeral=True)

        if len(queue) >= MAX_PLAYERS:
            return await interaction.response.send_message("Queue full", ephemeral=True)

        queue.append(interaction.user)
        await interaction.response.send_message("Joined ✔", ephemeral=True)
        await update_queue()

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.secondary)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in queue:
            queue.remove(interaction.user)
            await interaction.response.send_message("Left ✔", ephemeral=True)
        else:
            await interaction.response.send_message("Not in queue", ephemeral=True)

        await update_queue()


# ---------- UPDATE ----------
async def _update_queue():
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


async def update_queue():
    await _update_queue()

    if len(queue) == MAX_PLAYERS:
        channel = bot.get_channel(CHANNELS[current_mode])
        players = queue[:]
        queue.clear()

        await channel.send(
            f"🔥 **MATCH READY ({current_mode})** 🔥\n\n" +
            "\n".join(p.mention for p in players)
        )


# ---------- OPEN PANEL ----------
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


# ---------- SLASH COMMANDS ----------
def tester(interaction):
    return is_tester(interaction)


@bot.tree.command(name="opensword", guild=discord.Object(id=GUILD_ID))
async def opensword(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Sword")


@bot.tree.command(name="openaxe", guild=discord.Object(id=GUILD_ID))
async def openaxe(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Axe")


@bot.tree.command(name="opennethpot", guild=discord.Object(id=GUILD_ID))
async def opennethpot(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "NethPot")


@bot.tree.command(name="opendiapot", guild=discord.Object(id=GUILD_ID))
async def opendiapot(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "DiaPot")


@bot.tree.command(name="opencrystal", guild=discord.Object(id=GUILD_ID))
async def opencrystal(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Crystal")


@bot.tree.command(name="opendiasmp", guild=discord.Object(id=GUILD_ID))
async def opendiasmp(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "DiaSMP")


@bot.tree.command(name="opensmp", guild=discord.Object(id=GUILD_ID))
async def opensmp(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "SMP")


@bot.tree.command(name="openmace", guild=discord.Object(id=GUILD_ID))
async def openmace(interaction):
    if not tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Mace")


# ---------- RESULT COMMAND ----------
@bot.tree.command(name="result", guild=discord.Object(id=GUILD_ID))
async def result(interaction, member: discord.Member, gamemode: str, tier: str, ign: str, tester: discord.Member):

    if not is_tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)

    tier = tier.upper()

    if tier not in POINTS:
        return await interaction.response.send_message("❌ Invalid tier", ephemeral=True)

    points = POINTS[tier]

    embed = discord.Embed(title="⚔ Match Result", color=0x4aa3ff)

    embed.description = (
        f"{member.mention} Result:\n\n"
        f"**IGN:** {ign}\n"
        f"**Tier:** {tier}\n"
        f"**Ranked:** {points} Points\n"
        f"**GameMode:** {gamemode}\n\n"
        f"**Tester:** {tester.mention}\n\n"
        f"McPvP-Tierlist: https://www.mcpvptiers.xyz/"
    )

    channel = bot.get_channel(RESULT_CHANNEL)
    await channel.send(embed=embed)

    await interaction.response.send_message("Result posted ✔", ephemeral=True)


# ---------- TICKET SYSTEM ----------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary)
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.send(f"{interaction.user.mention} Support ticket opened 🎫")

    @discord.ui.button(label="Partnership", style=discord.ButtonStyle.success)
    async def partner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.send(f"{interaction.user.mention} Partnership ticket opened 🤝")

    @discord.ui.button(label="Rank Purchase", style=discord.ButtonStyle.danger)
    async def rank(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.send(f"{interaction.user.mention} Rank purchase ticket opened 💰")


@bot.tree.command(name="ticket_add_tick", guild=discord.Object(id=GUILD_ID))
async def ticket_add_tick(interaction):

    if not is_tester(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)

    embed = discord.Embed(
        title="🎫 Ticket Panel",
        description="Select an option below:",
        color=0x4aa3ff
    )

    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Ticket panel created ✔", ephemeral=True)


# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Slash commands synced ✔")
    except Exception as e:
        print("Sync error:", e)


# ---------- RUN ----------
bot.run(os.getenv("TOKEN"))
