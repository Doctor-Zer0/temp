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
            activities_list = []
            for a in member.activities:
                activity_data = {
                    'name': a.name,
                    'type': a.type.name,
                    'details': getattr(a, 'details', None),
                    'state': getattr(a, 'state', None),
                    'application_id': str(a.application_id) if getattr(a, 'application_id', None) else None
                }
                # Add emoji info if custom status and has emoji
                if a.type == discord.ActivityType.custom:
                    emoji = getattr(a, 'emoji', None)
                    if emoji:
                        activity_data['emoji'] = {
                            'name': emoji.name,
                            'id': str(emoji.id) if emoji.id else None,
                            'animated': emoji.animated if emoji.id else False
                        }
                if hasattr(a, 'assets') and a.assets is not None:
                    activity_data['assets'] = {
                        'large_image': getattr(a.assets, 'large_image', None),
                        'large_text': getattr(a.assets, 'large_text', None),
                        'small_image': getattr(a.assets, 'small_image', None),
                        'small_text': getattr(a.assets, 'small_text', None)
                    }
                activities_list.append(activity_data)
            presence_data['activities'] = activities_list
            presence_data['user'] = {
                'id': str(member.id),
                'avatar': member.avatar.key if member.avatar else None
            }

# Run bot in a thread
def run_discord():
    client.run(BOT_TOKEN)

threading.Thread(target=run_discord).start()

# Flask server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
