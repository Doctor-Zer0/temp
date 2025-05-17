from flask import Flask, request, redirect, session, jsonify
import requests
import base64
import os

app = Flask(__name__)
app.secret_key = 'something_secret_here'

# Spotify app credentials
CLIENT_ID = 'your_spotify_client_id'
CLIENT_SECRET = 'your_spotify_client_secret'
REDIRECT_URI = 'http://localhost:8888/callback'

# Step 1: Login URL
@app.route('/login')
def login():
    scope = 'user-read-currently-playing'
    return redirect(
        f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}"
    )

# Step 2: Handle callback and get refresh token
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
    session['refresh_token'] = token_json['refresh_token']
    return "Login successful! You can close this window."

# Step 3: Get current track
@app.route('/now-playing')
def now_playing():
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return jsonify({'error': 'Not logged in'}), 401

    # Get a new access token
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
    access_token = token_res.json().get('access_token')

    # Use the token to fetch now playing
    now_res = requests.get(
        'https://api.spotify.com/v1/me/player/currently-playing',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    return jsonify(now_res.json())
