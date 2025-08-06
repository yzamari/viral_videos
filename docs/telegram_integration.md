# Telegram Integration for News Aggregator

## Overview
The ViralAI News Aggregator now supports scraping news from Telegram channels using the official Telegram API.

## Setup

### 1. Get Telegram API Credentials
1. Go to https://my.telegram.org
2. Log in with your phone number
3. Navigate to "API development tools"
4. Create an application to get:
   - API ID
   - API Hash

### 2. Configure Credentials
Run the setup script:
```bash
python setup_telegram.py
```

Or manually add to `.env` file:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
```

### 3. Install Dependencies
```bash
pip install telethon
```

## Usage

### Command Line
```bash
# Aggregate news from websites and Telegram channels
python main.py news aggregate-enhanced https://www.ynet.co.il \
  --telegram-channels @ynet_news @channel13news \
  --languages he \
  --platform tiktok \
  --style "modern news" \
  --tone professional
```

### Features
- **Real-time scraping** from Telegram channels
- **Media download** (photos and videos)
- **Language detection** (Hebrew, Arabic, Russian, English)
- **Duplicate detection** across sources
- **Time-based filtering** (--hours-back parameter)

### Test Mode
If no credentials are configured, the system automatically falls back to a test scraper with sample data.

## Supported Telegram Features
- Text messages
- Photos
- Videos
- Message metadata (views, forwards)
- Channel information

## Example Channels
Hebrew News:
- @ynet_news
- @channel13news
- @kann_news

## Troubleshooting

### Authentication Issues
1. Ensure phone number includes country code
2. Be ready to enter verification code sent to your phone
3. Session is saved locally for future use

### Rate Limits
Telegram API has rate limits. The scraper respects these limits automatically.

### Media Download Failures
Downloaded media is saved to `outputs/telegram_media/`
Ensure sufficient disk space and write permissions.