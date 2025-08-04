#!/usr/bin/env python3
"""
Rotter Dark Humor News - Hebrew Version
30 seconds of Israeli dark humor in Hebrew
"""

import os
import subprocess
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import asyncio
import random


class HebrewDarkHumorNews:
    """Creates satirical Hebrew news with dark humor"""
    
    def __init__(self):
        self.font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial Hebrew.ttc",
            "/Library/Fonts/Arial Hebrew.ttf",
            "/System/Library/Fonts/Supplemental/Tahoma.ttf"
        ]
        self.best_font = self._find_hebrew_font()
        os.makedirs("dark_humor_hebrew", exist_ok=True)
    
    def _find_hebrew_font(self):
        """Find best Hebrew font"""
        for path in self.font_paths:
            if os.path.exists(path):
                try:
                    # Test Hebrew rendering
                    font = ImageFont.truetype(path, 40)
                    img = Image.new('RGB', (100, 100))
                    draw = ImageDraw.Draw(img)
                    draw.text((10, 10), "בדיקה", font=font)
                    print(f"✅ Using Hebrew font: {path}")
                    return path
                except:
                    continue
        return None
    
    def get_font(self, size):
        """Get Hebrew-supporting font"""
        if self.best_font:
            try:
                return ImageFont.truetype(self.best_font, size)
            except:
                pass
        return ImageFont.load_default()
    
    def create_dark_hebrew_frame(self, story, position, total):
        """Create a frame with Hebrew dark humor"""
        
        # Dark gritty background
        img = Image.new('RGB', (1920, 1080), color=(5, 5, 5))
        draw = ImageDraw.Draw(img)
        
        # Add visual noise
        for _ in range(1000):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            gray = random.randint(10, 30)
            draw.point((x, y), fill=(gray, gray, gray))
        
        # Fonts
        font_huge = self.get_font(120)
        font_large = self.get_font(72)
        font_medium = self.get_font(52)
        font_small = self.get_font(38)
        
        # Distressed header
        for i in range(140):
            r = 120 + random.randint(-30, 30)
            draw.rectangle([(0, i), (1920, i+1)], fill=(r, 0, 0))
        
        # Logo and sarcastic tagline
        draw.text((50, 35), "רוטר", fill=(255, 255, 255), font=font_large)
        draw.text((200, 35), ".נט", fill=(200, 0, 0), font=font_large)
        draw.text((1600, 55), "המנה היומית של ייאוש™", fill=(180, 180, 180), 
                 font=font_small, anchor="ra")
        
        # Story number with blood effect
        for dx, dy in [(-3, -3), (3, 3), (-3, 3), (3, -3)]:
            draw.text((100 + dx, 200 + dy), str(position), fill=(100, 0, 0), font=font_huge)
        draw.text((100, 200), str(position), fill=(255, 0, 0), font=font_huge)
        
        # Sarcastic badge
        if story.get('badge'):
            badge_bg = (random.randint(80, 120), 0, 0)
            draw.rectangle([(300, 220), (700, 300)], fill=badge_bg)
            draw.text((500, 250), story['badge'], fill=(255, 255, 255), 
                     font=font_medium, anchor="ma")
        
        # Main headline box
        headline_y = 380
        # Dark semi-transparent background
        draw.rectangle([(50, headline_y), (1870, headline_y + 180)], 
                      fill=(0, 0, 0, 200))
        
        # Headline (right-aligned for Hebrew)
        draw.text((1820, headline_y + 40), story['headline'], 
                 fill=(255, 255, 255), font=font_large, anchor="ra")
        
        # Subtitle
        draw.text((1820, headline_y + 110), story['subtitle'], 
                 fill=(200, 200, 200), font=font_medium, anchor="ra")
        
        # Dark commentary
        if story.get('commentary'):
            comment_y = 620
            draw.rectangle([(100, comment_y), (1820, comment_y + 100)], 
                          fill=(20, 0, 0))
            # Quote marks and text
            draw.text((1750, comment_y + 50), f'"{story["commentary"]}"', 
                     fill=(255, 180, 0), font=font_medium, anchor="ra")
        
        # Fake statistics
        if story.get('stat'):
            stat_y = 780
            draw.text((1820, stat_y), "📊 סטטיסטיקה אמיתית לגמרי:", 
                     fill=(150, 150, 150), font=font_small, anchor="ra")
            draw.text((1820, stat_y + 45), story['stat'], 
                     fill=(255, 100, 100), font=font_medium, anchor="ra")
        
        # Bottom ticker
        draw.rectangle([(0, 980), (1920, 1080)], fill=(10, 10, 10))
        draw.rectangle([(0, 980), (1920, 985)], fill=(150, 0, 0))
        
        # Cynical ticker messages
        tickers = [
            "בדחיפות: הכל בסדר, אין מה לראות כאן",
            "בלעדי: פוליטיקאי נתפס דובר אמת (באפריל)",
            "דחוף: מחירי הקפה עולים, הפריון צונח"
        ]
        ticker = tickers[position % len(tickers)]
        draw.text((1870, 1020), ticker, fill=(200, 200, 200), 
                 font=font_small, anchor="ra")
        
        # Doom meter
        progress = (position / total) * 1920
        draw.rectangle([(0, 1070), (progress, 1080)], fill=(200, 0, 0))
        draw.text((progress - 20, 1045), "מד אבדון", fill=(255, 100, 100), 
                 font=font_small, anchor="ra")
        
        # Random glitch lines
        for _ in range(5):
            y = random.randint(0, 1080)
            draw.rectangle([(0, y), (1920, y+1)], fill=(255, 0, 0, 50))
        
        return img
    
    async def create_hebrew_dark_news(self):
        """Create 30-second Hebrew dark humor news"""
        
        print("""
😈 יוצרים חדשות עם הומור שחור
============================
⏱️  30 שניות של סאטירה
🎭 בעברית עסיסית
📰 סקופים של רוטר בגרסה מעוותת
""")
        
        # Hebrew dark humor stories
        stories = [
            {
                'headline': "רעידה 4.2: הבניינים רועדים, הפוליטיקאים לא",
                'subtitle': "אסון טבע עדיין פחות הרסני ממליאת הכנסת",
                'badge': "מזעזע",
                'commentary': "הטבע מנסה להתחרות בממשלה על כמות הנזק",
                'stat': "87% מהאזרחים העדיפו את רעידת האדמה"
            },
            {
                'headline': "ראש הממשלה מכריז: הארנק שלכם מתחיל דיאטה",
                'subtitle': "תוכנית הרזיה מהפכנית לחשבונות בנק",
                'badge': "אזהרת ארנק",
                'commentary': "תופעות לוואי: בכי ומרק עוף בשקית",
                'stat': "משקל החבילה: 10 ק״ג נייר, 0 גרם תוכן"
            },
            {
                'headline': "מזל״ט צה״לי קרס: גם הטכנולוגיה רוצה לברוח",
                'subtitle': "המזל״ט ביקש לכאורה מקלט בלבנון",
                'badge': "טיסה נכשלה",
                'commentary': "למזל״ט הייתה אסטרטגיית יציאה טובה מרוב הסטארטאפים",
                'stat': "המכשיר השלישי השבוע שמנסה לברוח"
            },
            {
                'headline': "ראש עיר נעצר בשחיתות: מים עדיין רטובים",
                'subtitle': "אזרחים המומים לגלות הימורים בקזינו",
                'badge': "רמת הפתעה: 0",
                'commentary': "בחדשות קשורות: השמש זורחת במזרח",
                'stat': "מדד השחיתות: כן"
            },
            {
                'headline': "מנהל בי״ח התפטר: ״התקף שפיות פתאומי״",
                'subtitle': "משבר בריאות הנפש - פקיד פיתח מצפון",
                'badge': "נס רפואי",
                'commentary': "רופאים נדהמים מהתפרצות היושר הנדירה",
                'stat': "1 מתוך מיליון פקידים נדבקו"
            },
            {
                'headline': "אקזיט 2 מיליארד: עכשיו יכולים חניה בת״א",
                'subtitle': "כמעט מספיק לדירת 3 חדרים (עם שותפים)",
                'badge': "עדיין מרוששים",
                'commentary': "החגיגה נבלמה כשנזכרו במס רווחי הון",
                'stat': "שווי מקום החניה: 1.9 מיליארד"
            }
        ]
        
        segments = []
        
        # Dark intro
        print("\n🎬 יוצרים אינטרו ציני...")
        intro_img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))
        draw = ImageDraw.Draw(intro_img)
        
        # Glitch background
        for i in range(150):
            y = random.randint(0, 1080)
            r = random.randint(50, 150)
            draw.rectangle([(0, y), (1920, y+2)], fill=(r, 0, 0, 100))
        
        font_title = self.get_font(100)
        font_sub = self.get_font(60)
        font_warning = self.get_font(45)
        
        # Title
        draw.text((960, 350), "רוטר: מהדורת החושך", fill=(255, 0, 0), 
                 font=font_title, anchor="ma")
        draw.text((960, 500), "חדשות שכואב לצחוק עליהן", fill=(200, 200, 200), 
                 font=font_sub, anchor="ma")
        draw.text((960, 650), "שיקול דעת הצופים: כנראה רצוי", fill=(150, 150, 150), 
                 font=font_warning, anchor="ma")
        
        # Warning symbols
        draw.text((200, 800), "☠️", fill=(255, 0, 0), font=font_title)
        draw.text((1720, 800), "☠️", fill=(255, 0, 0), font=font_title)
        
        intro_path = "dark_humor_hebrew/intro.jpg"
        intro_img.save(intro_path)
        
        intro_video = "dark_humor_hebrew/intro.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', intro_path,
            '-t', '2',
            '-vf', 'scale=1920:1080,eq=brightness=-0.2:saturation=1.5',
            '-c:v', 'libx264',
            '-preset', 'fast',
            intro_video
        ]
        subprocess.run(cmd, capture_output=True)
        segments.append(intro_video)
        os.remove(intro_path)
        
        # Create stories
        print("\n😈 יוצרים סיפורי הומור שחור...")
        story_duration = 4.5
        
        for i, story in enumerate(stories):
            print(f"  {i+1}. {story['headline'][:30]}...")
            
            frame = self.create_dark_hebrew_frame(story, i+1, len(stories))
            frame_path = f"dark_humor_hebrew/story_{i}.jpg"
            frame.save(frame_path)
            
            video_path = f"dark_humor_hebrew/story_{i}.mp4"
            
            # Dark effects
            effects = [
                'scale=1920:1080,eq=brightness=-0.15:contrast=1.2',
                'scale=1920:1080,vignette=angle=PI/3',
                'scale=1920:1080,noise=alls=15:allf=t'
            ]
            
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', frame_path,
                '-t', str(story_duration),
                '-vf', random.choice(effects),
                '-c:v', 'libx264',
                '-preset', 'fast',
                video_path
            ]
            subprocess.run(cmd, capture_output=True)
            segments.append(video_path)
            os.remove(frame_path)
        
        # Outro
        print("\n🎬 יוצרים אאוטרו...")
        outro_img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))
        draw = ImageDraw.Draw(outro_img)
        
        # Static
        for _ in range(3000):
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            gray = random.randint(0, 40)
            draw.point((x, y), fill=(gray, gray, gray))
        
        draw.text((960, 400), "זהו, חברים!", fill=(255, 255, 255), 
                 font=font_title, anchor="ma")
        draw.text((960, 550), "זוכרים: זה מצחיק כי זה אמיתי", fill=(200, 0, 0), 
                 font=self.get_font(55), anchor="ma")
        draw.text((960, 700), "© המציאות 2025", fill=(150, 150, 150), 
                 font=self.get_font(45), anchor="ma")
        
        outro_path = "dark_humor_hebrew/outro.jpg"
        outro_img.save(outro_path)
        
        outro_video = "dark_humor_hebrew/outro.mp4"
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1',
            '-i', outro_path,
            '-t', '1',
            '-vf', 'fade=t=out:st=0.5:d=0.5',
            '-c:v', 'libx264',
            '-preset', 'fast',
            outro_video
        ]
        subprocess.run(cmd, capture_output=True)
        segments.append(outro_video)
        os.remove(outro_path)
        
        # Compile
        print("\n🎬 מחברים את מהדורת ההומור השחור...")
        concat_file = "dark_humor_hebrew/concat.txt"
        with open(concat_file, 'w') as f:
            for segment in segments:
                f.write(f"file '{os.path.abspath(segment)}'\n")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"dark_humor_hebrew/rotter_dark_hebrew_{timestamp}.mp4"
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c:v', 'libx264',
            '-preset', 'fast',
            output_path
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Test frame
        test_frame = "dark_humor_hebrew/preview.jpg"
        cmd = [
            'ffmpeg', '-y',
            '-i', output_path,
            '-ss', '15',
            '-frames:v', '1',
            test_frame
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Cleanup
        os.remove(concat_file)
        for segment in segments:
            if os.path.exists(segment):
                os.remove(segment)
        
        print(f"""
😈 חדשות הומור שחור בעברית - הושלם!
===================================
📹 וידאו: {output_path}
⏱️  משך: 30 שניות
🎭 סיפורים: 6 טייקים סאטיריים

📰 הכותרות שנכללו:
1. רעידה מול פוליטיקאים (4.5 שניות)
2. דיאטת הארנק הלאומית (4.5 שניות)
3. המזל״ט הבורח (4.5 שניות)
4. שחיתות - רמת הפתעה אפס (4.5 שניות)
5. מגיפת השפיות (4.5 שניות)
6. חניה יקרה מאקזיט (4.5 שניות)

🎨 אלמנטים אפלים:
- כותרות סרקסטיות בעברית
- סטטיסטיקות מזויפות
- סגנון ויזואלי אפל
- פרשנות צינית
- מד אבדון
- אפקטי גליץ׳

📸 תצוגה מקדימה: {test_frame}

⚠️  תופעות לוואי אפשריות:
- צחוק לא נוח
- משבר קיומי
- דחף פתאומי להגר
- גלגול עיניים בלתי נשלט
- געגועים לחו״ל

✅ מוכן להפצה המונית של דיכאון משעשע!
""")
        
        return output_path


if __name__ == "__main__":
    generator = HebrewDarkHumorNews()
    asyncio.run(generator.create_hebrew_dark_news())