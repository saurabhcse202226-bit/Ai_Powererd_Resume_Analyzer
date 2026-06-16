# ResumeAI — Deployment Guide

This guide covers deploying the app on Render (free), Railway, and basic VPS/Docker.

---

## Option 1: Render (Recommended for beginners — Free tier)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/yourusername/AI_Resume_Analyzer.git
git push -u origin main
```

### Step 2: Create Render account

Go to [render.com](https://render.com) and sign up with GitHub.

### Step 3: New Web Service

1. Click **New → Web Service**
2. Connect your GitHub repo
3. Fill in:
   - **Name:** `resumeai`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Free

### Step 4: Add Environment Variables

In the Render dashboard → Environment tab, add:

```
SECRET_KEY=your-random-secret-key-here
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx  (optional)
```

### Step 5: Deploy

Click **Create Web Service**. First deploy takes ~3 minutes.

> **Note:** Render's free tier spins down after 15 minutes of inactivity. First request after that takes ~30 seconds to wake up.

---

## Option 2: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

Add env vars in the Railway dashboard.

---

## Option 3: Docker

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads database

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Build and run

```bash
docker build -t resumeai .

docker run -d \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret \
  -e ANTHROPIC_API_KEY=your-key \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/database:/app/database \
  resumeai
```

---

## Option 4: Ubuntu VPS (DigitalOcean / AWS EC2)

### 1. Server setup

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx -y
```

### 2. Clone and setup

```bash
cd /var/www
git clone https://github.com/yourusername/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create systemd service

```bash
sudo nano /etc/systemd/system/resumeai.service
```

Paste:
```ini
[Unit]
Description=ResumeAI Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/AI_Resume_Analyzer
Environment="SECRET_KEY=your-secret"
Environment="ANTHROPIC_API_KEY=your-key"
ExecStart=/var/www/AI_Resume_Analyzer/venv/bin/gunicorn --workers 3 --bind unix:resumeai.sock app:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start resumeai
sudo systemctl enable resumeai
```

### 4. Nginx config

```bash
sudo nano /etc/nginx/sites-available/resumeai
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/AI_Resume_Analyzer/resumeai.sock;
    }

    location /static/ {
        alias /var/www/AI_Resume_Analyzer/static/;
    }

    client_max_body_size 10M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/resumeai /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL with Certbot (free HTTPS)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

---

## Production Checklist

- [ ] `SECRET_KEY` is a long random string (not the default)
- [ ] `SESSION_COOKIE_SECURE = True` in config (needs HTTPS)
- [ ] `DEBUG = False`
- [ ] SQLite is fine for small scale; switch to PostgreSQL for production
- [ ] Set up daily database backups
- [ ] Configure upload folder with proper permissions
- [ ] Add ANTHROPIC_API_KEY or the fallback feedback will be used
- [ ] Test file upload works on server (permissions on `/uploads` folder)

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | dev-secret-key | Flask session secret |
| `ANTHROPIC_API_KEY` | No | '' | Claude API key for AI feedback |
| `PORT` | No | 5000 | Port to run on |
