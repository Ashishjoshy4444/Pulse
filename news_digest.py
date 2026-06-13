# News Digest Bot
# Scrapes top headlines from 3 news sites, builds an HTML email,
# and sends it every morning at 7 AM.

import requests
import os
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup


def get_bbc_headlines():
    """Scrape top headlines from BBC News."""
    url = "https://www.bbc.com/news"
    headlines = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all("h2")[:5]:
            text = tag.get_text(strip=True)
            if text:
                headlines.append({"title": text, "source": "BBC News", "url": url})
    except Exception as e:
        headlines.append({"title": f"BBC headlines unavailable ({e})", "source": "BBC News", "url": url})

    return headlines[:3]


def get_reuters_headlines():
    """Scrape top headlines from Reuters."""
    url = "https://www.reuters.com/world/"
    headlines = []
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all("h3")[:5]:
            text = tag.get_text(strip=True)
            if text:
                headlines.append({"title": text, "source": "Reuters", "url": url})
    except Exception as e:
        headlines.append({"title": f"Reuters headlines unavailable ({e})", "source": "Reuters", "url": url})

    return headlines[:3]


def get_aljazeera_headlines():
    """Scrape top headlines from Al Jazeera."""
    url = "https://www.aljazeera.com/"
    headlines = []
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all("h3")[:5]:
            text = tag.get_text(strip=True)
            if text:
                headlines.append({"title": text, "source": "Al Jazeera", "url": url})
    except Exception as e:
        headlines.append({"title": f"Al Jazeera headlines unavailable ({e})", "source": "Al Jazeera", "url": url})

    return headlines[:3]


def build_html_email(bbc, reuters, aljazeera):
    """Combine all headlines into a formatted HTML email."""
    today = date.today().strftime("%A, %d %B %Y")
    fetched_time = "7:00 AM IST"

    html = f"<h2>Morning News Digest - {today}</h2>"

    for source_name, headlines in [("BBC News", bbc), ("Reuters", reuters), ("Al Jazeera", aljazeera)]:
        html += f"<h3>{source_name}</h3><ul>"
        for item in headlines:
            html += (
                f"<li>{item['title']}<br>"
                f"<small>Source: <a href='{item['url']}'>{item['source']}</a> "
                f"| Fetched: {fetched_time}</small></li>"
            )
        html += "</ul>"

    return html


def send_email(html_content):
    """Send the digest as an HTML email."""
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Morning News Digest"
    msg["From"] = sender
    msg["To"] = receiver

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

    print("News digest email sent.")


def run():
    """Main entry point. Called by GitHub Actions."""
    bbc = get_bbc_headlines()
    reuters = get_reuters_headlines()
    aljazeera = get_aljazeera_headlines()

    html = build_html_email(bbc, reuters, aljazeera)
    print(html)

    send_email(html)


if __name__ == "__main__":
    run()
