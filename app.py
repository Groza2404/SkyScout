import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
import requests

app = Flask(__name__)

api_key = 'THE_KEY'

def get_user_location():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        coordinates = data.get('loc', '').split(',')
        if len(coordinates) == 2:
            lat, lon = coordinates
            return {'lat': float(lat), 'lon': float(lon)}
        else:
            return None
    except Exception as e:
        print(f"Error getting user's location: {e}")
        return None
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not city and (not lat or not lon):
        # Attempt to get user's location based on IP address or browser geolocation
        user_location = get_user_location()
        if user_location:
            lat, lon = user_location['lat'], user_location['lon']
        else:
            return jsonify({'error': 'Unable to determine user location.'}), 400

    if city:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    elif lat and lon:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
    else:
        return jsonify({'error': 'Invalid request parameters.'}), 400

    try:
        response = requests.get(url)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
