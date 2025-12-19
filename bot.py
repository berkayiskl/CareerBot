import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import google.generativeai as genai

from sql import get_db, setup


#.env

load_dotenv()

# Tokenler

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# Gemini entegrasyonu

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")


# Database setup

setup()


# Bot setup

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot giriş yaptı: {bot.user}")


# Kayıt komutu

@bot.command()
async def kayit(ctx, age: int, education: str, interests: str, skills: str, goal: str):
    """
    Örnek kullanım:
    !kayit 18 lise "yazılım,oyun" "python,discord" "oyun geliştirici olmak"
    """
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (discord_id, age, education, interests, skills, goal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(ctx.author.id),
            age,
            education,
            interests,
            skills,
            goal
        ))
        conn.commit()
        await ctx.send("✅ Kaydın alındı! Artık `!kariyer` yazabilirsin.")
    except:
        await ctx.send("⚠️ Zaten kayıtlısın.")
    finally:
        conn.close()


# Gemini kariyer komutu

@bot.command()
async def kariyer(ctx):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT age, education, interests, skills, goal FROM users WHERE discord_id = ?",
        (str(ctx.author.id),)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return await ctx.send("❌ Önce kayıt olmalısın. `!kayit`")

    age = user["age"]
    education = user["education"]
    interests = user["interests"]
    skills = user["skills"]
    goal = user["goal"]

    prompt = f"""
Sen profesyonel bir kariyer danışmanısın.

Kullanıcı bilgileri:
- Yaş: {age}
- Eğitim: {education}
- İlgi alanları: {interests}
- Yetkinlikler: {skills}
- Hedef: {goal}

Bu kişiye özel:
1. Uygun kariyer yolları
2. Kısa vadeli plan (0-6 ay)
3. Orta vadeli plan (6-24 ay)
4. Öğrenmesi gereken beceriler
5. Net ve motive edici tavsiyeler

hazırla. Türkçe yaz.
"""

    try:
        response = model.generate_content(prompt)
        await ctx.send(response.text[:2000])  # Discord mesaj limiti
    except Exception as e:
        print(e)
        await ctx.send("🤯 Kariyer motoru şu an yoğun, birazdan tekrar dene.")


# BOT RUN

bot.run(DISCORD_TOKEN)
