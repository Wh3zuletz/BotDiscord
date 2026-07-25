import os
from flask import Flask, request, jsonify
import discord
from discord.ext import commands

# Configurarea Flask pentru Roblox
app = Flask(__name__)

# Configurarea Botului de Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@app.route('/verifica', methods=['POST'])
def verifica():
    data = request.json
    cod = data.get("cod")
    
    # Aici pui logica ta existentă de verificare a codului
    if cod == "12345":  # Exemplu simplu
        return jsonify({"mesaj": "Cont verificat cu succes!", "status": "succes"})
    else:
        return jsonify({"mesaj": "Cod invalid sau expirat!", "status": "eroare"})

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")

# Pornirea automată a Flask-ului și a botului de Discord
if __name__ == "__main__":
    import threading
    # Rulează Flask pe fundal
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    
    # Rulează botul de Discord folosind tokenul securizat din Render
    bot.run(os.environ.get("DISCORD_TOKEN"))