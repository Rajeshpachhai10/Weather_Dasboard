# from django.shortcuts import render
# import requests

# # Create your views here.

# def index(request):
#     if 'city' in request.POST:
#         city=request.POST['city']
#     else:
#         city='kathmandu'
        
#     url=f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=bf22686cf11682e29d657b984d138978'
#     param={'units':'metric'}
#     data=requests.get(url,param).json()
#     temp=data['main']['temp']
#     pressure=data['main']['pressure']
#     humidity=data['main']['humidity']

#     context = {
#     'temp':temp ,
#     'city':city ,
#     'pressure': pressure ,
#     'humidity': humidity ,
#     }
#     return render(request ,'index.html' ,context)


import requests
from datetime import datetime, timezone, timedelta
from django.shortcuts import render
from django.conf import settings 



API_KEY = settings.WEATHER_API_KEY
BASE_URL = 'https://api.openweathermap.org/data/2.5/'

# ── Weather image mapping (Unsplash, free) ────────────────────────
WEATHER_IMAGES = {
    '01d': 'https://images.unsplash.com/photo-1601297183305-6df142704ea2?w=800&q=80',
    '01n': 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&q=80',
    '02d': 'https://images.unsplash.com/photo-1501630834273-4b5604d2ee31?w=800&q=80',
    '02n': 'https://images.unsplash.com/photo-1532978379173-523e16f371f4?w=800&q=80',
    '03d': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=800&q=80',
    '03n': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=800&q=80',
    '04d': 'https://images.unsplash.com/photo-1499956827185-0d63ee78a910?w=800&q=80',
    '04n': 'https://images.unsplash.com/photo-1499956827185-0d63ee78a910?w=800&q=80',
    '09d': 'https://images.unsplash.com/photo-1428592953211-077101b2021b?w=800&q=80',
    '09n': 'https://images.unsplash.com/photo-1428592953211-077101b2021b?w=800&q=80',
    '10d': 'https://images.unsplash.com/photo-1519692933481-e162a57d6721?w=800&q=80',
    '10n': 'https://images.unsplash.com/photo-1501999635878-71cb5379c2d8?w=800&q=80',
    '11d': 'https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?w=800&q=80',
    '11n': 'https://images.unsplash.com/photo-1605727216801-e27ce1d0cc28?w=800&q=80',
    '13d': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=800&q=80',
    '13n': 'https://images.unsplash.com/photo-1491002052546-bf38f186af56?w=800&q=80',
    '50d': 'https://images.unsplash.com/photo-1485236715568-ddc5ee6ca227?w=800&q=80',
    '50n': 'https://images.unsplash.com/photo-1485236715568-ddc5ee6ca227?w=800&q=80',
}

# ── Page background gradients ─────────────────────────────────────
BG_GRADIENTS = {
    '01d': 'linear-gradient(145deg, #1a6bc4, #f7b733)',
    '01n': 'linear-gradient(145deg, #0f0c29, #302b63)',
    '02d': 'linear-gradient(145deg, #2c3e50, #4ca1af)',
    '02n': 'linear-gradient(145deg, #1c2a3a, #2c3e50)',
    '03d': 'linear-gradient(145deg, #3a4a5a, #5a7a8a)',
    '03n': 'linear-gradient(145deg, #1a2a3a, #2a3a4a)',
    '04d': 'linear-gradient(145deg, #2c3e50, #3a5a6a)',
    '04n': 'linear-gradient(145deg, #1a2030, #2a3040)',
    '09d': 'linear-gradient(145deg, #1f4037, #3a6a7a)',
    '09n': 'linear-gradient(145deg, #0f2027, #203a43)',
    '10d': 'linear-gradient(145deg, #1a2a4a, #243b6e)',
    '10n': 'linear-gradient(145deg, #0f1a2a, #1a2a3e)',
    '11d': 'linear-gradient(145deg, #0f0c29, #4a0080)',
    '11n': 'linear-gradient(145deg, #09090f, #2a0050)',
    '13d': 'linear-gradient(145deg, #c9d6e3, #e0eafc)',
    '13n': 'linear-gradient(145deg, #1a2a4a, #2a3a6a)',
    '50d': 'linear-gradient(145deg, #606c88, #3f4c6b)',
    '50n': 'linear-gradient(145deg, #303540, #404550)',
}

DEFAULT_IMAGE    = 'https://images.unsplash.com/photo-1504608524841-42584120d693?w=800&q=80'
DEFAULT_GRADIENT = 'linear-gradient(145deg, #1a2a4a, #243b6e)'


# ── Helper: UV label ──────────────────────────────────────────────
def get_uv_label(uv):
    if uv <= 2:   return 'Low — minimal protection needed'
    elif uv <= 5: return 'Moderate — wear sunscreen'
    elif uv <= 7: return 'High — seek shade midday'
    else:         return 'Very high — extra protection required'


# ── Helper: Unix timestamp → local time string ────────────────────
def fmt_time(unix_ts, offset_sec):
    dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc) + timedelta(seconds=offset_sec)
    return dt.strftime('%H:%M')


# ── Main view ─────────────────────────────────────────────────────
def index(request):
    context = {}

    # GET → show Kathmandu by default
    # POST → show whatever city the user searched
    if request.method == 'POST':
        city_input = request.POST.get('city', '').strip()
    else:
        city_input = 'Kathmandu'

    if city_input:

        # ── 1. Current Weather ────────────────────────────────────
        try:
            url  = f"{BASE_URL}weather?q={city_input}&appid={API_KEY}&units=metric"
            resp = requests.get(url, timeout=5)
            data = resp.json()

            if data.get('cod') != 200:
                context['error'] = data.get('message', 'City not found.')
                return render(request, 'weather_index.html', context)

            tz_offset   = data['timezone']
            sunrise_ts  = data['sys']['sunrise']
            sunset_ts   = data['sys']['sunset']
            sunrise_str = fmt_time(sunrise_ts, tz_offset)
            sunset_str  = fmt_time(sunset_ts,  tz_offset)

            daylight_secs  = sunset_ts - sunrise_ts
            daylight_hours = daylight_secs // 3600
            daylight_mins  = (daylight_secs % 3600) // 60
            daylight_str   = f"{daylight_hours}h {daylight_mins}m"
            daylight_pct   = min(int((daylight_secs / 57600) * 100), 100)

            icon_code = data['weather'][0]['icon']

            context.update({
                'city':         data['name'],
                'country':      data['sys']['country'],
                'temp':         round(data['main']['temp']),
                'feels_like':   round(data['main']['feels_like']),
                'temp_max':     round(data['main']['temp_max']),
                'temp_min':     round(data['main']['temp_min']),
                'humidity':     data['main']['humidity'],
                'pressure':     data['main']['pressure'],
                'wind_speed':   data['wind']['speed'],
                'wind_deg':     data['wind'].get('deg', 0),
                'visibility':   round(data.get('visibility', 0) / 1000, 1),
                'description':  data['weather'][0]['description'],
                'icon':         icon_code,
                'cloud_cover':  data['clouds']['all'],
                'sunrise':      sunrise_str,
                'sunset':       sunset_str,
                'daylight':     daylight_str,
                'daylight_pct': daylight_pct,
                # ── NEW: image + gradient ──
                'weather_image': WEATHER_IMAGES.get(icon_code, DEFAULT_IMAGE),
                'bg_gradient':   BG_GRADIENTS.get(icon_code, DEFAULT_GRADIENT),
            })

        except requests.exceptions.RequestException:
            context['error'] = 'Could not connect to weather service.'
            return render(request, 'weather_index.html', context)

        # ── 2. 5-Day / Hourly Forecast ────────────────────────────
        try:
            url5  = f"{BASE_URL}forecast?q={city_input}&appid={API_KEY}&units=metric"
            resp5 = requests.get(url5, timeout=5)
            data5 = resp5.json()

            # Hourly — next 8 entries (24 hours)
            hourly = []
            for item in data5['list'][:8]:
                dt_obj = (datetime.fromtimestamp(item['dt'], tz=timezone.utc)
                          + timedelta(seconds=tz_offset))
                hourly.append({
                    'time': dt_obj.strftime('%I %p').lstrip('0'),
                    'icon': item['weather'][0]['icon'],
                    'temp': round(item['main']['temp']),
                    'rain': round(item.get('pop', 0) * 100),
                })
            context['hourly'] = hourly

            # 5-day — one entry per day
            seen_days = {}
            for item in data5['list']:
                dt_obj  = (datetime.fromtimestamp(item['dt'], tz=timezone.utc)
                           + timedelta(seconds=tz_offset))
                day_key = dt_obj.strftime('%Y-%m-%d')
                if day_key not in seen_days:
                    seen_days[day_key] = {
                        'name':     dt_obj.strftime('%a'),
                        'icon':     item['weather'][0]['icon'],
                        'temp_max': round(item['main']['temp_max']),
                        'temp_min': round(item['main']['temp_min']),
                        'rain':     round(item.get('pop', 0) * 100),
                    }
            context['forecast'] = list(seen_days.values())[:5]

            # Rain chance today
            today_pops = [round(i.get('pop', 0) * 100) for i in data5['list'][:8]]
            context['rain_chance'] = max(today_pops) if today_pops else 0

        except Exception:
            context['hourly']   = []
            context['forecast'] = []

        # ── 3. UV Index ───────────────────────────────────────────
        try:
            lat    = data['coord']['lat']
            lon    = data['coord']['lon']
            uv_url = f"{BASE_URL}uvi?lat={lat}&lon={lon}&appid={API_KEY}"
            uv_resp = requests.get(uv_url, timeout=5)
            uv_data = uv_resp.json()
            uv_index = round(uv_data.get('value', 0))
            context['uv_index'] = uv_index
            context['uv_pct']   = min(int(uv_index / 12 * 100), 100)
            context['uv_label'] = get_uv_label(uv_index)
        except Exception:
            context['uv_index'] = '--'
            context['uv_pct']   = 0
            context['uv_label'] = ''

        # ── 4. Air Quality ────────────────────────────────────────
        try:
            lat     = data['coord']['lat']
            lon     = data['coord']['lon']
            aqi_url = f"{BASE_URL}air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
            aqi_resp = requests.get(aqi_url, timeout=5)
            aqi_data = aqi_resp.json()
            aqi_index = aqi_data['list'][0]['main']['aqi']
            aqi_map = {
                1: (25,  'Good',      'good'),
                2: (60,  'Fair',      'moderate'),
                3: (100, 'Moderate',  'moderate'),
                4: (150, 'Poor',      'bad'),
                5: (200, 'Very Poor', 'bad'),
            }
            aqi_val, aqi_label, aqi_class = aqi_map.get(aqi_index, (50, 'Good', 'good'))
            context['aqi_val']   = aqi_val
            context['aqi_label'] = aqi_label
            context['aqi_class'] = aqi_class
        except Exception:
            context['aqi_val']   = '--'
            context['aqi_label'] = 'N/A'
            context['aqi_class'] = 'good'

        # ── 5. Dew Point (formula, no API needed) ─────────────────
        try:
            T = context['temp']
            H = context['humidity']
            context['dew_point'] = round(T - ((100 - H) / 5))
        except Exception:
            context['dew_point'] = '--'

    return render(request, 'weather_index.html', context)