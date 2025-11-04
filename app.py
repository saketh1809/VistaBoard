from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
from datetime import datetime
import pytz
import feedparser
import yfinance as yf
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/weather')
def weather_page():
    return render_template('weather.html')

@app.route('/get-weather')
def get_weather():
    city = "Pune"  # or dynamically fetch if needed
    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        current = data['current_condition'][0]
        astro = data['weather'][0]['astronomy'][0]

        weather_data = {
            "city": city,
            "description": current['weatherDesc'][0]['value'],
            "temperature_c": current['temp_C'],
            "temperature_f": current['temp_F'],
            "pressure": current['pressure'],
            "humidity": current['humidity'],
            "precip": current['precipMM'],
            "wind_kph": current['windspeedKmph'],
            "moon_phase": astro['moon_phase'],
            "moon_illumination": astro['moon_illumination'],
            "moonrise": astro['moonrise'],
            "moonset": astro['moonset'],
            "sunrise": astro['sunrise'],
            "sunset": astro['sunset'],
        }
        return jsonify(weather_data)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/get-quote')
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        data = response.json()[0]
        quote_data = {"content": data["q"], "author": data["a"]}
        return jsonify(quote_data)
    except Exception as e:
        return jsonify({"content": "Error fetching quote.", "author": str(e)})

@app.route('/news')
def news():
    import feedparser
    from bs4 import BeautifulSoup
    from datetime import datetime

    url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    news_items = []

    for entry in feed.entries[:50]:
        # Try to get image from <media:content> or <enclosure>
        image_url = None
        if "media_content" in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0].get("url")
        elif "links" in entry:
            for link in entry.links:
                if link.get("type", "").startswith("image/"):
                    image_url = link.get("href")
                    break

        # Fallback to scraping from summary HTML
        if not image_url:
            soup = BeautifulSoup(entry.get("summary", ""), "html.parser")
            img_tag = soup.find("img")
            image_url = img_tag["src"] if img_tag else "/static/default-img.png"

        # Extract text content
        soup = BeautifulSoup(entry.get("summary", ""), "html.parser")
        text = soup.get_text().strip()

        news_items.append({
            'title': entry.get("title"),
            'link': entry.get("link"),
            'description': text[:300] + "..." if len(text) > 300 else text,
            'publishedAt': entry.get("published", ""),
            'source': entry.get("source", {}).get("title", "Google News"),
            'image_url': image_url
        })

    now = datetime.now()
    return render_template("news.html", news=news_items, now=now)

@app.route("/stocks")
def stocks_page():
    return render_template("stocks.html", now=datetime.now())

@app.route('/api/data')
def api_data():
    symbol = request.args.get('symbol', 'TCS.NS')
    period = request.args.get('period', '1mo')  # default 1 month
    tk = yf.Ticker(symbol)
    hist = tk.history(period=period, interval='1h' if period in ['1d', '5d'] else '1d')
    prices = hist['Close'].tolist()
    timestamps = [ts.strftime('%Y-%m-%d %H:%M' if period in ['1d', '5d'] else '%Y-%m-%d') for ts in hist.index]
    high = max(prices) if prices else None
    low = min(prices) if prices else None
    info = tk.info
    about = info.get('longBusinessSummary', '')
    return jsonify({
        'symbol': symbol,
        'name': info.get('shortName', symbol),
        'price': prices[-1] if prices else 'N/A',
        'prices': prices,
        'timestamps': timestamps,
        'high': high,
        'low': low,
        'about': about[:225] + '...' if len(about) > 225 else about,
        'sector': info.get('sector', ''),
        'industry': info.get('industry', ''),
        'website': info.get('website', ''),
        'logo_url': info.get('logo_url', ''),
    })

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
