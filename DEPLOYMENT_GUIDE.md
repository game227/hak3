# 🚀 QuietSpace Tashkent — Render Deployment Qo‘llanmasi

Ushbu qo‘llanma orqali **QuietSpace Tashkent** veb-ilovasini [Render.com](https://render.com) platformasiga bepul va avtomatik ravishda joylashtirishingiz (deploy) mumkin.

---

## 📁 1. Loyihada tayyorlangan deployment fayllari:
- **`render.yaml`** — Render Blueprint fayli (Veb-servis va PostgreSQL ma’lumotlar bazasini 1 ta bosishda sozlaydi).
- **`build.sh`** — Paketlarni o‘rnatish, static fayllarni yig‘ish (`collectstatic`) va migratsiyalarni bajaruvchi skript.
- **`Procfile`** — Gunicorn production serverini ishga tushirish konfiguratsiyasi (`gunicorn config.wsgi:application`).
- **`requirements.txt`** — Production uchun zarur kutubxonalar (`Django`, `gunicorn`, `whitenoise`, `psycopg2-binary`, `dj-database-url`).

---

## 🛠 2. Qadam-baqadam Renderga joylash:

### 1-Qadam: Kodni GitHub repositoriyga yuklang
Terminalda loyiha papkasida (`/home/neo/Desktop/hak3`) quyidagi buyruqlarni bajaring:
```bash
git init
git add .
git commit -m "QuietSpace Tashkent Production Ready"
git branch -M main
git remote add origin https://github.com/SIZNING_USERNAME/quietspace-tashkent.git
git push -u origin main
```

---

### 2-Qadam: Render.com saytida Blueprints orqali ochish (Eng osoni)
1. **[https://dashboard.render.com/](https://dashboard.render.com/)** ga kiring va GitHub orqali kiring.
2. **New +** tugmasini bosib, **`Blueprint`** tanlang.
3. GitHub-dagi `quietspace-tashkent` repositoriyangizni tanlang.
4. Render avtomatik `render.yaml` faylini o‘qib oladi va:
   - 🟢 **`quietspace-tashkent`** nomli Python Veb-servisni
   - 🐘 **`quietspace-db`** nomli PostgreSQL ma’lumotlar bazasini avtomatik yaratadi.
5. **`Apply`** tugmasini bosing.

---

### 3-Qadam (Muqobil): Qo‘lda Web Service yaratish
Agar Blueprint ishlatmasangiz:
1. Renderda **New +** -> **Web Service** tanlang.
2. Repositoriyangizni ulang.
3. Quyidagi parametrlarni kiriting:
   - **Name:** `quietspace-tashkent`
   - **Environment:** `Python`
   - **Region:** `Frankfurt (EU Central)`
   - **Branch:** `main`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
   - **Plan:** `Free`
4. **Environment Variables (Muhit o‘zgaruvchilari)** bo‘limiga quyidagilarni qo‘shing:
   - `SECRET_KEY` = `ixtiyoriy-uzun-maxfiy-kalit`
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = `.onrender.com,localhost,127.0.0.1`
   - `DATABASE_URL` = `(Renderda ochilgan PostgreSQL bazangizning Internal Database URL manzili)`
   - `GEMINI_API_KEY` = `(Google Gemini API kalitingiz - ixtiyoriy)`
5. **Create Web Service** tugmasini bosing.

---

### 4-Qadam: Saytda Admin (Superuser) yaratish
Deploy muvaffaqiyatli yakunlangach:
1. Render Dashboard-da veb-servisingiz sahifasiga o‘ting.
2. Chap menyudan **`Shell`** tugmasini bosing.
3. Terminal ochilgach, quyidagi buyruqni kiriting:
```bash
python manage.py createsuperuser
```
Username, email va parolni kiriting.

---

### 5-Qadam: Dastlabki namunaviy joylarni yuklash (Seed Data)
Render Shell terminalida boshlang‘ich test joylari va ma’lumotlarni kiritish uchun:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🌐 Muvaffaqiyatli Deployment!
Sizning saytingiz Render taqdim etgan bepul SSL (HTTPS) domenida ishga tushadi:
👉 **`https://quietspace-tashkent.onrender.com/`**

Admin panel:
👉 **`https://quietspace-tashkent.onrender.com/admin/`**
