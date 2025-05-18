import os
import threading
from flask import Flask, jsonify
from flask_cors import CORS
import discord
from discord.ext import tasks

app = Flask(__name__)
CORS(app, origins=['http://127.0.0.1:5500', 'https://spotify-backend-zaoy.onrender.com'])

# Load environment variable secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_USER_ID = int(os.environ.get("TARGET_USER_ID"))

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

# Dict for latest presence data
presence_data = {
    "status": "offline",
    "activities": [],
    'user' : {}
}

@app.route('/presence')
def get_presence():
    return jsonify(presence_data)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    update_presence.start()

@tasks.loop(seconds=10)
async def update_presence():
    for guild in client.guilds:
        member = guild.get_member(TARGET_USER_ID)
        if member:
            presence_data["status"] = member.status.name
            presence_data["activities"] = [{
                "name": a.name,
                "type": a.type.name,
                "details": getattr(a, "details", None),
                "state": getattr(a, "state", None)
            } for a in member.activities]
            presence_data['user'] = {
                'id': str(member.id),
                'avatar': member.avatar.key if member.avatar else None
            }
            return

# Run bot in a thread
def run_discord():
    client.run(BOT_TOKEN)

threading.Thread(target=run_discord).start()

# Flask server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
