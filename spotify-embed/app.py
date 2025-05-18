from flask import Flask, request, redirect, session, jsonify
from flask_cors import CORS
import requests
import base64
import os

# ========== Environment Inputs ==========
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://127.0.0.1:5500', 'https://galaxypengin.com'])
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-fallback-key')

# Spotify app credentials
CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')

# ============== Core System =============
# Step 1: login url
@app.route('/login')
def login():
    scope = 'user-read-currently-playing'
    return redirect(
        f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}'
    )

# Step 2: callback and refresh token
@app.route('/callback')
def callback():
    code = request.args.get('code')
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    token_res = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI
        },
        headers={
            'Authorization': f'Basic {b64_auth_str}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    token_json = token_res.json()
    print(token_json)
    return redirect(f"http://127.0.0.1:5500/mason's%20FUCKING%20WEBSAITE/spotify%20embed/index.html?token={token_json['refresh_token']}")

# Step 3: get current track
@app.route('/now-playing', methods=['POST'])
def now_playing():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'Not logged in'}), 401

    # New access token
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    token_res = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        },
        headers={
            'Authorization': f'Basic {b64_auth_str}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    )
    print(token_res.json())
    access_token = token_res.json().get('access_token')

    # Fetch now playing
    now_res = requests.get(
        'https://api.spotify.com/v1/me/player/currently-playing',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    return jsonify(now_res.json())

# Open host and port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
