import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        weather_data = req.get_json()
        if not weather_data:
            return func.HttpResponse(
                "Invalid input data",
                status_code=400
            )

        enhanced_data = enhance_forecast(weather_data)
        return func.HttpResponse(
            json.dumps(enhanced_data),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )

def enhance_forecast(data):
    current = data['current']
    forecast = {
        'temp': current['temp'],
        'weather': current['weather'][0]['description'],
        'humidity': current['humidity'],
        'wind_speed': current['wind_speed'],
        'alerts': data.get('alerts', [])
    }
    return {'city': data.get('timezone', 'Unknown'), 'forecast': forecast}