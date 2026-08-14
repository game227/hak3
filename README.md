# 🌿 QuietSpace Tashkent — Tinch Ishlash Joylari Ekotizimi

[![Django Version](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Python Version](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![Telegram Bot](https://img.shields.io/badge/Telegram_Bot-@QuietSpace_Tashkent_bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/QuietSpace_Tashkent_bot)

> **QuietSpace Tashkent** — Toshkent shahridagi frilanserlar, dasturchilar, talabalar va masofaviy ishlovchilar uchun tinch kovorkinglar, sokin qahvaxonalar va kutubxonalarni topish, real vaqtdagi shovqin (dB) hamda Wi-Fi tezligini (Mbps) baholash, 3D stollarni oldindan band qilish va yagona **QuietPass** obunasidan foydalanish ekotizimi.

---

## ✨ Asosiy Imkoniyatlar

1. **🌿 Peaceful Cyber-Nature Dizayn Tizimi:**
   - 60 FPS HTML5 Canvas zarrachalar foni (momaqaymoq parchalari, olovqo‘ng‘izlar, kiber-kapalaklar).
   - Tashqi MP3siz ishlovchi **Web Audio API** orqali 9 xil protsedural tabiat tovushlari sintezatori (Zen Soundboard).
   - High-contrast tipografiya va engil glassmorphism.

2. **🪑 3D Zen Micro-Booking:**
   - Zallarning 3D Izometrik xaritasidan aniq stolni (rozetka bor/yo‘q, Zoom kabina) tanlab, bir bosishda bron qilish.

3. **🤖 Jasur — AI Jonli Maslahatchi (Google Gemini AI):**
   - Foydalanuvchining erkin so‘rovlarini inson kabi samimiy tahlil qilib, Toshkentdagi eng mos joylarni solishtirib tavsiya qiladi.

4. **⚡️ Crowdsourced O‘lchovlar & Gamifikatsiya:**
   - Wi-Fi Speedtest (+10 ball) va shovqin darajasi (dB) tahlili.
   - Status darajalari: 🌱 *Explorer* → 🌿 *Quiet Master* → 🌳 *Space Guru*.

5. **💳 QuietPass Obunasi & To‘lovlar:**
   - Yagona obuna orqali 10-25% chegirma va bepul qahvalar.
   - Administrator uchun tezkor to‘lovlarni tasdiqlash / rad etish paneli.

6. **🤖 Telegram Bot Integratsiyasi:**
   - Yagona PostgreSQL ma’lumotlar bazasi orqali sayt bilan 100% sinxron ishlash.

---

## 🛠 Texnologiyalar Steki

- **Backend:** Django 5.1 / Python 3.13, Django ORM, Asgiref
- **Database:** PostgreSQL (Production) / SQLite (Local)
- **Frontend:** HTML5 Canvas, Web Audio API, Vanilla JavaScript, CSS3 Glassmorphism, Bootstrap 5 Icons
- **AI & NLP:** Google Gemini 1.5 Flash API + Neural Knowledge Graph
- **Telegram Bot:** Aiogram 3.x
- **Production Server:** Gunicorn, WhiteNoise, Render Cloud

---

## 🚀 O‘rnatish va Ishga Tushirish (Lokal)

```bash
# 1. Repositoriyani klonlash
git clone https://github.com/game227/hak3.git
cd hak3

# 2. Virtual muhitni yaratish va faollashtirish
python3 -m venv .venv
source .venv/bin/activate

# 3. Kutubxonalarni o‘rnatish
pip install -r requirements.txt

# 4. Migratsiyalarni bajarish
python manage.py makemigrations
python manage.py migrate

# 5. Serverni ishga tushirish
python manage.py runserver
```

---

## 🌐 Render.com Deployment

Loyiha to‘liq `render.yaml`, `build.sh` va `Procfile` bilan jihozlangan.
Render Dashboard orqali **Blueprint** sifatida ulanganda avtomatik tarzda Web Service va PostgreSQL bazasini ishga tushiradi.

---

## 📄 Litsenziya
MIT License © 2026 QuietSpace Tashkent Team.
