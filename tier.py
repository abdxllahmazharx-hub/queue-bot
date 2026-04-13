import discord
from discord.ext import commands
import os

# ---------- CONFIG ----------
GUILD_ID = 1491802017851769065
TESTER_ROLE_NAME = "Testers"
MAX_PLAYERS = 10

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

queue = []
current_mode = None
panel_owner = None
queue_message = {}


# ---------- ROLE CHECK ----------
def is_tester(interaction):
    return any(role.name == TESTER_ROLE_NAME for role in interaction.user.roles)


# ---------- EMBED ----------
def build_embed():
    embed = discord.Embed(
        title=f"⚔ {current_mode} Queue",
        description=f"{current_mode} Tier Testing (Max 10 Players)",
        color=0x4aa3ff
    )

    if len(queue) == 0:
        embed.add_field(name="🎮 Queue (0/10)", value="Empty", inline=False)
    else:
        embed.add_field(
            name=f"🎮 Queue ({len(queue)}/10)",
            value="\n".join(
                f"{i+1}. {u.mention} ({u.display_name})"
                for i, u in enumerate(queue)
            ),
            inline=False
        )

    embed.add_field(
        name="🧪 Tester (Panel Owner)",
        value=panel_owner.mention if panel_owner else "None",
        inline=False
    )

    embed.set_footer(text="Live Queue System")
    return embed


# ---------- BUTTONS ----------
class QueueView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.primary)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in queue:
            return await interaction.response.send_message("Already in queue ⚠", ephemeral=True)

        if len(queue) >= MAX_PLAYERS:
            return await interaction.response.send_message("Queue full (10/10) ❌", ephemeral=True)

        queue.append(user)
        await interaction.response.send_message("Joined queue ✔", ephemeral=True)

        await update_queue()

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.secondary)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user in queue:
            queue.remove(user)
            await interaction.response.send_message("Left queue ✔", ephemeral=True)
        else:
            await interaction.response.send_message("Not in queue ⚠", ephemeral=True)

        await update_queue()


# ---------- MATCH ----------
async def check_match():
    if len(queue) == MAX_PLAYERS:
        players = queue[:]
        queue.clear()

        channel = bot.get_channel(CHANNELS[current_mode])

        await channel.send(
            f"🔥 **{current_mode.upper()} MATCH READY (10/10)** 🔥\n\n" +
            "\n".join(f"{i+1}. {p.mention}" for i, p in enumerate(players))
        )


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
    await check_match()


# ---------- OPEN PANEL ----------
async def open_panel(interaction, mode):
    global current_mode, panel_owner, queue

    current_mode = mode
    panel_owner = interaction.user
    queue = []

    channel = bot.get_channel(CHANNELS[mode])

    msg = await channel.send(
        f"@here 💙 **{mode} Queue Opened**",
        allowed_mentions=discord.AllowedMentions(everyone=True),
        view=QueueView()
    )

    queue_message[mode] = msg.id

    await update_queue()

    await interaction.response.send_message(f"{mode} queue opened ✔", ephemeral=True)


# ---------- SLASH COMMANDS ----------
def tester_only(interaction):
    return is_tester(interaction)


@bot.tree.command(name="opensword", guild=discord.Object(id=GUILD_ID))
async def opensword(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Sword")


@bot.tree.command(name="openaxe", guild=discord.Object(id=GUILD_ID))
async def openaxe(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Axe")


@bot.tree.command(name="opennethpot", guild=discord.Object(id=GUILD_ID))
async def opennethpot(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "NethPot")


@bot.tree.command(name="opendiapot", guild=discord.Object(id=GUILD_ID))
async def opendiapot(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "DiaPot")


@bot.tree.command(name="opencrystal", guild=discord.Object(id=GUILD_ID))
async def opencrystal(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Crystal")


@bot.tree.command(name="opendiasmp", guild=discord.Object(id=GUILD_ID))
async def opendiasmp(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "DiaSMP")


@bot.tree.command(name="opensmp", guild=discord.Object(id=GUILD_ID))
async def opensmp(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "SMP")


@bot.tree.command(name="openmace", guild=discord.Object(id=GUILD_ID))
async def openmace(interaction):
    if not tester_only(interaction):
        return await interaction.response.send_message("❌ Testers only", ephemeral=True)
    await open_panel(interaction, "Mace")


# ---------- READY ----------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Slash commands synced ✔")
    except Exception as e:
        print("Sync failed:", e)


# ---------- RUN (RAILWAY SAFE) ----------
bot.run(os.getenv("TOKEN"))
