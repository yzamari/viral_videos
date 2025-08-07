# 📱 Telegram News Scraping - Quick Start Guide

## 🚀 Setup (One-Time)

### 1. Get Telegram API Credentials
```bash
python3 setup_telegram.py
```

This will guide you through:
- Getting API credentials from https://my.telegram.org
- Saving them securely to `.env` file
- Testing the connection

### 2. Alternative: Manual Setup
Add to your `.env` file:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone_number  # optional
```

## 📰 Usage Examples

### Basic Telegram Channel Scraping
```bash
# Single channel
python3 main.py news aggregate-enhanced \
  --telegram-channels @ynet_news \
  --platform tiktok \
  --duration 60

# Multiple channels
python3 main.py news aggregate-enhanced \
  --telegram-channels @ynet_news \
  --telegram-channels @channel13news \
  --telegram-channels @kann_news \
  --style "breaking news" \
  --duration 60
```

### Mix Telegram with Web Sources
```bash
python3 main.py news aggregate-enhanced \
  https://www.ynet.co.il \
  https://rotter.net/forum/scoops1/ \
  --telegram-channels @breaking_news \
  --telegram-channels @news0404 \
  --style "dark humor satire" \
  --platform tiktok \
  --duration 60
```

### Dark Humor News Edition
```bash
python3 main.py news aggregate-enhanced \
  --telegram-channels @srugim_news \
  --telegram-channels @news0404 \
  --style "dark comedy news satire" \
  --tone "sarcastic dark humor" \
  --channel-name "DOOM & GLOOM NEWS" \
  --platform tiktok \
  --duration 30 \
  --max-stories 10
```

## 📺 Popular Israeli News Channels

| Channel | Description |
|---------|-------------|
| @ynet_news | Ynet News |
| @channel13news | Channel 13 News |
| @kann_news | Kann News |
| @N12News | Channel 12 News |
| @glz_news | Galei Tzahal (Army Radio) |
| @srugim_news | Srugim News |
| @news0404 | 0404 News |
| @Heb_News | Hebrew News |
| @NewsIL | Israel News |

## ⚙️ Options

- `--telegram-channels` / `-tc`: Specify Telegram channels (can use multiple times)
- `--hours-back`: How far back to scrape (default: 24)
- `--max-stories`: Maximum stories to include
- `--use-youtube-videos`: Add YouTube video backgrounds
- `--no-ai-discussion`: Skip AI discussions for faster processing

## 🔧 Troubleshooting

### "Telegram API not available"
```bash
# Install telethon
pip3 install telethon

# Setup credentials
python3 setup_telegram.py
```

### "Session file error"
```bash
# Remove old session files
rm *.session
rm news_scraper.session
```

### "Cannot connect to Telegram"
1. Check your API credentials in `.env`
2. Ensure your phone number has access to the channels
3. Try re-authenticating: `python3 setup_telegram.py`

## 📝 Notes

- First run will require phone number authentication
- Session is saved for future runs (no need to re-authenticate)
- Private channels require membership
- Media (images/videos) from Telegram are automatically downloaded
- Supports Hebrew, Arabic, Russian, and English content detection

## 🎬 Complete Example

Create a dark humor news video from Israeli Telegram channels:

```bash
# Setup (once)
python3 setup_telegram.py

# Create video
python3 main.py news aggregate-enhanced \
  --telegram-channels @ynet_news \
  --telegram-channels @channel13news \
  --telegram-channels @news0404 \
  --platform tiktok \
  --style "dark comedy news satire like The Onion" \
  --tone "deadpan sarcastic with gallows humor" \
  --channel-name "DOOM & GLOOM NEWS" \
  --duration 60 \
  --max-stories 15 \
  --languages he \
  --no-ai-discussion

# Output: outputs/session_*/news_he_tiktok_*.mp4
```
EOF < /dev/null