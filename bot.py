import os

import discord
from discord.ext import commands
from discord.ui import View, Button

TOKEN = os.getenv("DISCORD_TOKEN"

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

kanal_owner = {}

class KanalMaxView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for i in range(2, 11):
            self.add_item(Button(label=f"Stwórz max {i}", style=discord.ButtonStyle.green, custom_id=f"max_{i}"))

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"].startswith("max_"):
            max_osob = int(interaction.data["custom_id"].split("_")[1])
            guild = interaction.guild
            user = interaction.user
            channel = await guild.create_voice_channel(
                name=f"{user.display_name}'s kanał ({max_osob})",
                user_limit=max_osob
            )
            kanal_owner[channel.id] = user.id
            await interaction.response.send_message(
                f"✅ Stworzyłem kanał `{channel.name}` z limitem **{max_osob} osób**.\n"
                f"👑 Właściciel: {user.mention}",
                ephemeral=True
            )

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and before.channel.id in kanal_owner:
        if len(before.channel.members) == 0:
            await before.channel.delete()
            del kanal_owner[before.channel.id]

@bot.command()
async def panel(ctx):
    embed = discord.Embed(
        title="Stwórz kanał max",
        description="Kliknij przycisk, aby stworzyć kanał z limitem osób.\n"
                    "📌 Kanały są **automatycznie usuwane**, jeśli zostaną puste.",
        color=discord.Color.green()
    )
    view = KanalMaxView()
    await ctx.send(embed=embed, view=view)

@bot.group(invoke_without_command=True)
async def max(ctx):
    await ctx.send("Użyj: `!max wyrzuc @użytkownik`")

@max.command()
async def wyrzuc(ctx, member: discord.Member):
    voice_state = member.voice
    if not voice_state or not voice_state.channel:
        await ctx.send("❌ Ten użytkownik nie jest na kanale głosowym.")
        return

    channel = voice_state.channel
    owner_id = kanal_owner.get(channel.id)

    if owner_id != ctx.author.id:
        await ctx.send("❌ Nie jesteś właścicielem tego kanału.")
        return

    await member.move_to(None)
    await ctx.send(f"✅ {member.mention} został wyrzucony z `{channel.name}`.")

bot.run(TOKEN)
