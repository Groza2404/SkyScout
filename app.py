import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
import requests

app = Flask(__name__)

api_key = 'b9e3a01988effd916a53213a095e0550'
azure_func_url = 'AZFUNCTURL'

def get_user_location():
    try:
        ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
        response = requests.get(f'https://ipinfo.io/{ip_addr}?token=2b5580d0ce75ed')
        data = response.json()
        city = data.get('city')
        coordinates = data.get('loc', '').split(',')
        if len(coordinates) == 2:
            lat, lon = coordinates
            return {'lat': float(lat), 'lon': float(lon)}
        else:
            return None
    except Exception as e:
        print(f"Error getting user's location: {e}")
        return None
    
def fecth_coords(city):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={2}&appid={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if data:
        return data[0]
    return None


def fetch_weather(lat, lon):
    url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['GET'])
def get_weather():
    try:
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
            location = fecth_coords(city)
            if location:
                lat = location['lat']
                lon = location['lon']
            else:
                return jsonify({'error' : 'Latitude and longitude are required.'}), 400
        if not lat or not lon:
            return jsonify({'error': 'Invalid request parameters.'}), 400

        data = fetch_weather(lat, lon)
        return jsonify(data)
    
    except requests.RequestException as e:
        app.logger.error(f"Error fetching weather data: {e}")
        return jsonify({'error': 'Failed to fetch weather data.'}), 500 

    except Exception as e:
        app.logger.error(f"Unexpected error : {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500
    
@app.route('/enhanced_forecast', methods=['POST'])
def enhanced_forecast():
    try:
        data = request.json
        response = requests.post(azure_func_url, json=data)
        response.raise_for_status()
        enhanced_data = response.json()
        return jsonify(enhanced_data)
    
    except requests.RequestException as e:
        app.logger.error(f"Error calling Azure Function: {e}")
        return jsonify({'error': 'Failed to fetch enhanced weather data.'}), 500 

    except Exception as e:
        app.logger.error(f"Unexpected error : {e}")
        return jsonify({'error': 'An unexpected error occurred.'}), 500


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
