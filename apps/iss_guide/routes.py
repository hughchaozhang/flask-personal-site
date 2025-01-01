from flask import Blueprint, render_template, request
from datetime import datetime
import os
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

iss_bp = Blueprint('iss_guide', __name__, url_prefix='/iss-guide')

# Configuration
N2YO_API_KEY = os.getenv("N2YO_API_KEY")
SATELLITE_ID = 25544  # ISS NORAD ID

# Default LA coordinates
DEFAULT_CITY = "Los Angeles"
DEFAULT_COORDS = {
    "latitude": 34.052235,
    "longitude": -118.243683
}

def get_city_coordinates(location=None):
    """Get coordinates for a given location string, default to LA if None or error"""
    if not location:
        print(f"\nUsing default location: {DEFAULT_CITY}")
        return DEFAULT_COORDS["latitude"], DEFAULT_COORDS["longitude"], DEFAULT_CITY

    try:
        geolocator = Nominatim(user_agent="iss_tracker")
        location_data = geolocator.geocode(location)

        if location_data:
            return location_data.latitude, location_data.longitude, location_data.address
        else:
            return DEFAULT_COORDS["latitude"], DEFAULT_COORDS["longitude"], DEFAULT_CITY
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        return DEFAULT_COORDS["latitude"], DEFAULT_COORDS["longitude"], DEFAULT_CITY

def get_timezone_from_coordinates(latitude, longitude):
    """Get timezone string from coordinates"""
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    return timezone_str or 'America/Los_Angeles'

def get_iss_position():
    """Get current ISS position using N2YO API"""
    try:
        url = f"https://api.n2yo.com/rest/v1/satellite/positions/{SATELLITE_ID}/0/0/0/1/?apiKey={N2YO_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            return None, None, None

        if 'positions' not in data or not data['positions']:
            return None, None, None

        positions = data['positions'][0]
        return float(positions['satlatitude']), float(positions['satlongitude']), float(positions['sataltitude'])

    except (requests.exceptions.RequestException, KeyError, IndexError, ValueError) as e:
        return None, None, None

def get_location_from_coordinates(latitude, longitude):
    """Get location name from coordinates using reverse geocoding"""
    try:
        geolocator = Nominatim(user_agent="iss_tracker")
        location = geolocator.reverse((latitude, longitude), language='en')

        if location:
            address_parts = []
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village')
            state = address.get('state') or address.get('region')
            country = address.get('country')

            if city: address_parts.append(city)
            if state: address_parts.append(state)
            if country: address_parts.append(country)

            return f"Currently above: {', '.join(address_parts)}" if address_parts else "Currently above water"
        else:
            return "Currently above water"
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        return f"Location lookup failed: {str(e)}"

def get_next_passes(lat, lng, alt=0, days=10):
    """Get next visible passes using N2YO API"""
    try:
        url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/{SATELLITE_ID}/{lat}/{lng}/{alt}/{days}/300/&apiKey={N2YO_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('passes', [])
    except requests.exceptions.RequestException as e:
        return None

def get_cardinal_direction(azimuth):
    """Convert azimuth in degrees to cardinal direction"""
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(azimuth / 22.5) % 16
    return directions[index]

def format_pass_info(pass_data, timezone_str):
    """Format pass information for display"""
    try:
        utc_start = datetime.fromtimestamp(pass_data['startUTC'], tz=pytz.UTC)
        utc_end = datetime.fromtimestamp(pass_data['endUTC'], tz=pytz.UTC)

        local_timezone = pytz.timezone(timezone_str)
        local_start = utc_start.astimezone(local_timezone)
        local_end = utc_end.astimezone(local_timezone)

        return (
            f"UTC Times:\n"
            f"  Start: {utc_start.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"  End: {utc_end.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"\nLocal Times ({timezone_str}):\n"
            f"  Start: {local_start.strftime('%Y-%m-%d %I:%M:%S %p %Z')}\n"
            f"  End: {local_end.strftime('%Y-%m-%d %I:%M:%S %p %Z')}\n"
            f"\nViewing Details:\n"
            f"  Starting direction: {pass_data['startAz']}° ({get_cardinal_direction(pass_data['startAz'])})\n"
            f"  Maximum Elevation: {pass_data['maxEl']}°\n"
            f"  Ending direction: {pass_data['endAz']}° ({get_cardinal_direction(pass_data['endAz'])})\n"
            f"  Duration: {pass_data['duration']} seconds\n"
            f"\nViewing guide: Look {get_cardinal_direction(pass_data['startAz'])} at {local_start.strftime('%I:%M %p')}, "
            f"the ISS will rise to {pass_data['maxEl']}° above horizon "
            f"and set {get_cardinal_direction(pass_data['endAz'])}"
        )
    except Exception as e:
        return f"Error formatting pass information: {str(e)}"

@iss_bp.route('/', methods=['GET', 'POST'])
def index():
    error = None
    current_location = None
    latitude = None
    longitude = None
    timezone = None
    iss_position = None
    passes = None

    if request.method == 'POST':
        try:
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            country = request.form.get('country', 'USA').strip()

            location = city
            if state:
                location += f", {state}"
            if country:
                location += f", {country}"

            latitude, longitude, address = get_city_coordinates(location if city else None)
            timezone = get_timezone_from_coordinates(latitude, longitude)
            current_location = address

            lat, lng, alt = get_iss_position()
            if all(v is not None for v in (lat, lng, alt)):
                iss_position = {
                    'latitude': f"{lat:.4f}",
                    'longitude': f"{lng:.4f}",
                    'altitude': f"{alt:.2f}",
                    'location_info': get_location_from_coordinates(lat, lng)
                }

            pass_data = get_next_passes(latitude, longitude)
            if pass_data:
                passes = []
                for pass_info in pass_data:
                    formatted_info = format_pass_info(pass_info, timezone)
                    passes.append({'formatted_info': formatted_info})

        except Exception as e:
            error = f"An error occurred: {str(e)}"

    return render_template('iss_guide/index.html',
                         error=error,
                         current_location=current_location,
                         latitude=latitude,
                         longitude=longitude,
                         timezone=timezone,
                         iss_position=iss_position,
                         passes=passes)