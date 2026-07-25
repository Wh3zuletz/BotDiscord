import discord
from discord import app_commands
import random
from flask import Flask, request, jsonify
import threading

# ----------------- CONFIGURARE SERVER WEB (PENTRU ROBLOX) -----------------
app = Flask("")

@app.route("/verifica", methods=["POST"])
def verifica_cod():
    data = request.json
    discord_id = int(data.get("discord_id", 0))
    cod_introdus = str(data.get("cod", ""))

    if discord_id in CODURI_VERIFICARE:
        info = CODURI_VERIFICARE[discord_id]
        if info["cod"] == cod_introdus:
            # Codul este corect! Salvăm jucătorul definitiv
            roblox_name = info["roblox"]
            DATE_JUCATORI[discord_id] = {"roblox": roblox_name, "puncte": 10} # Bonus de început 10 puncte
            del CODURI_VERIFICARE[discord_id] # Ștergem codul folosit
            
            return jsonify({"status": "succes", "mesaj": "Cont verificat cu succes!"})
    
    return jsonify({"status": "eroare", "mesaj": "Cod invalid sau expirat!"})

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# ----------------- CONFIGURARE BOT DISCORD -----------------
class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Comenzile slash (/) au fost sincronizate!")

client = MyBot()

DATE_JUCATORI = {}      
CODURI_VERIFICARE = {}  

@client.event
async def on_ready():
    print(f'Botul Discord a intrat ca {client.user}!')

@client.tree.command(name="robloxuser", description="Îți asociezi contul de Roblox în mod securizat.")
@app_commands.describe(roblox_name="Numele tău exact de pe Roblox")
async def robloxuser(interaction: discord.Interaction, roblox_name: str):
    user_id = interaction.user.id

    for d_id, date in DATE_JUCATORI.items():
        if date["roblox"].lower() == roblox_name.lower() and d_id != user_id:
            await interaction.response.send_message(f"❌ Contul de Roblox **{roblox_name}** este deja revendicat.", ephemeral=True)
            return

    if user_id in DATE_JUCATORI:
        await interaction.response.send_message(f"⚠️ Ai deja un cont asociat (**{DATE_JUCATORI[user_id]['roblox']}**).", ephemeral=True)
        return

    cod_unic = str(random.randint(1000, 9999))
    CODURI_VERIFICARE[user_id] = {"roblox": roblox_name, "cod": cod_unic}

    embed = discord.Embed(
        title="🔐 Verificare Cont Roblox (Secret)",
        description=f"Ai înregistrat numele **{roblox_name}**.\n\nIntră în jocul nostru de pe Roblox și introdu codul tău secret:",
        color=discord.Color.orange()
    )
    embed.add_field(name="⭐ Codul tău unic", value=f"# **{cod_unic}**", inline=False)
    embed.set_footer(text=f"ID-ul tău Discord pentru joc: {user_id}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="puncte", description="Verifică punctele tale.")
async def puncte(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in DATE_JUCATORI:
        info = DATE_JUCATORI[user_id]
        roblox_name = info["roblox"]
        puncte_val = info["puncte"]
    else:
        roblox_name = "Nespecificat (Neconfirmat)"
        puncte_val = 0

    embed = discord.Embed(title="📊 Profil Jucător", color=discord.Color.blue())
    embed.add_field(name="👤 Discord", value=interaction.user.mention, inline=True)
    embed.add_field(name="🎮 Roblox", value=roblox_name, inline=True)
    embed.add_field(name="⭐ Puncte", value=f"**{puncte_val}**", inline=False)
    
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="help", description="Meniul de ajutor.")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Centru de Ajutor", color=discord.Color.green())
    embed.add_field(name="`/robloxuser Nume`", value="Începe verificarea.", inline=False)
    embed.add_field(name="`/puncte`", value="Vezi punctele.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Pornim serverul web în paralel cu botul de Discord
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    client.run('MTUzMDMxNTI3MjIxOTUyNTE4MA.GmE75P.FIrEADyzOtk3LVugFWiLBEGEZIsdCryhugSduc')