# Telegram Integration Quick Start

## 1. Setup (One-time)
```bash
# Install Telethon
pip install telethon

# Configure credentials
python setup_telegram.py
```

## 2. Basic Usage
```bash
# Hebrew news from Ynet + Telegram channels
python main.py news aggregate-enhanced https://www.ynet.co.il \
  --telegram-channels @ynet_news @channel13news \
  --languages he \
  --platform tiktok

# Multiple sources with English output
python main.py news aggregate-enhanced \
  https://www.cnn.com https://www.bbc.com \
  --telegram-channels @breaking_news @world_news \
  --languages en \
  --platform youtube
```

## 3. Full Example with All Options
```bash
python main.py news aggregate-enhanced \
  https://www.ynet.co.il https://www.mako.co.il \
  --telegram-channels @ynet_news @channel13news @kann_news \
  --languages he en \
  --platform tiktok \
  --style "breaking news style with urgency" \
  --tone "professional yet engaging" \
  --overlay-style modern \
  --max-stories 10 \
  --hours-back 12 \
  --duration 90 \
  --enable-ai \
  --discussion-log
```

## 4. Platform Options
- `youtube` - 1920x1080 landscape
- `tiktok` - 1080x1920 portrait  
- `instagram` - 1080x1080 square
- `twitter` - 1920x1080 landscape

## 5. Test Mode
Without credentials, the system uses test data automatically.

## 6. Popular Hebrew Telegram Channels
- @ynet_news - Ynet breaking news
- @channel13news - Channel 13 news
- @kann_news - Kan news updates
- @glz_news - Galei Tzahal
- @haaretz - Haaretz news

## 7. Troubleshooting
- No credentials? System uses test data
- Authentication issues? Re-run setup_telegram.py
- Rate limits? Wait 15 minutes
- No media? Check outputs/telegram_media/