# 🚀 Deployment Guide

Deploy your Dota 2 Market Parser to production!

## 📋 Pre-deployment Checklist

- [ ] Code tested locally
- [ ] .env created with API key
- [ ] requirements.txt updated
- [ ] No debug=True in app.py
- [ ] All files ready
- [ ] Git repository initialized (optional)

## 🏠 Option 1: Local Server (Easiest)

### Run on your machine

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit .env and add API key

# Run server
python app.py
```

**Access:** http://localhost:5000

**Pros:** Simple, local access
**Cons:** Only available locally

---

## 🐳 Option 2: Docker

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Create docker-compose.yml

```yaml
version: "3"
services:
  dota2-parser:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DOTA2_API_KEY=${DOTA2_API_KEY}
      - FLASK_ENV=production
    restart: always
```

### Build and run

```bash
# Add gunicorn to requirements.txt first
echo "gunicorn==21.2.0" >> requirements.txt

# Build Docker image
docker build -t dota2-parser .

# Run container
docker run -e DOTA2_API_KEY=your_key -p 5000:5000 dota2-parser

# Or with docker-compose
docker-compose up -d
```

**Access:** http://localhost:5000

**Pros:** Portable, consistent environment
**Cons:** Requires Docker installed

---

## ☁️ Option 3: Heroku (Free-ish)

### Prerequisites

- Heroku account (free tier available)
- Heroku CLI installed
- Git initialized

### Setup

1. **Initialize Git**

```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Create Procfile**

```bash
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT app:app" > Procfile
```

3. **Update requirements.txt**

```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

4. **Create Heroku app**

```bash
heroku create your-app-name
```

5. **Set environment variables**

```bash
heroku config:set DOTA2_API_KEY=your_api_key
heroku config:set FLASK_ENV=production
```

6. **Deploy**

```bash
git push heroku main
# (or 'master' if that's your branch)
```

7. **Check logs**

```bash
heroku logs --tail
```

**Access:** https://your-app-name.herokuapp.com

**Pros:** Free, easy deployment, live on internet
**Cons:** Heroku free tier is limited

---

## 🚀 Option 4: AWS (Advanced)

### Using EC2

1. **Launch EC2 instance**
   - Ubuntu 20.04 LTS
   - t2.micro (free tier)
   - Security group: allow port 80, 443, 5000

2. **SSH into instance**

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install dependencies**

```bash
sudo apt update
sudo apt install python3-pip python3-venv git nginx

# Clone your repo
git clone your-repo-url
cd dota2-parser
```

4. **Setup Python environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

5. **Create systemd service**

```bash
sudo nano /etc/systemd/system/dota2-parser.service
```

```ini
[Unit]
Description=Dota2 Market Parser
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/dota2-parser
Environment="DOTA2_API_KEY=your_key"
ExecStart=/home/ubuntu/dota2-parser/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

6. **Start service**

```bash
sudo systemctl start dota2-parser
sudo systemctl enable dota2-parser
```

7. **Configure Nginx (reverse proxy)**

```bash
sudo nano /etc/nginx/sites-available/default
```

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

8. **Restart Nginx**

```bash
sudo systemctl restart nginx
```

**Access:** http://your-instance-ip

**Pros:** Full control, scalable
**Cons:** More complex setup

---

## ☁️ Option 5: Google Cloud (Similar to AWS)

### Using Cloud Run (simplest for GCP)

1. **Install Cloud SDK**

```bash
curl https://sdk.cloud.google.com | bash
```

2. **Authenticate**

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. **Create Dockerfile** (same as Docker section)

4. **Deploy**

```bash
gcloud run deploy dota2-parser \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars DOTA2_API_KEY=your_key
```

**Access:** Provided URL from GCP

**Pros:** Serverless, scales automatically
**Cons:** Paid service (free tier included)

---

## 📦 Option 6: PythonAnywhere (FREE! ⭐)

### Perfect for beginners - completely free hosting!

**See the complete guide:** [PYTHONANYWHERE_DEPLOYMENT.md](PYTHONANYWHERE_DEPLOYMENT.md)

**Quick Steps:**

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com) (FREE)

2. **Upload files** via Git or manual upload

3. **Create virtual environment**:

```bash
cd ~/dota2-parser
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure Web App** (from Web tab)
   - Add new web app → Manual config → Python 3.10
   - Set virtualenv: ``
   - Edit WSGI file (provided in `wsgi.py`)

5. **Add .env file** with your API key

6. **Reload** and visit: `https://YOUR_USERNAME.pythonanywhere.com`

**Access:** `https://YOUR_USERNAME.pythonanywhere.com`

**Pros:**

- ✅ **FREE tier available**
- ✅ Easy setup (~15 minutes)
- ✅ Great for personal projects
- ✅ Built-in file editor and console
- ✅ No credit card required

**Cons:**

- App sleeps after inactivity (first request ~10s)
- Limited to 100k requests/day (free tier)

---

## 📦 Option 7: DigitalOcean App Platform

### Simple deployment

1. **Push to GitHub**

```bash
git push origin main
```

2. **Connect DigitalOcean**
   - Create account
   - Connect GitHub repo
   - Select repo and branch

3. **Configure**
   - Framework: Python
   - Build command: `pip install -r requirements.txt`
   - Run command: `gunicorn -w 4 -b 0.0.0.0:8080 app:app`

4. **Set environment**
   - Add `DOTA2_API_KEY` env var
   - Set `FLASK_ENV=production`

5. **Deploy**
   - Click Deploy
   - Wait for build
   - Get URL

**Access:** Provided DigitalOcean URL

**Pros:** Very easy, great pricing
**Cons:** Not free

---

## 🔐 Production Security Checklist

### Environment

- [ ] FLASK_ENV=production
- [ ] DEBUG=False (removed)
- [ ] Use strong API key
- [ ] Rotate API key regularly
- [ ] Use HTTPS/SSL

### Code

- [ ] Input validation
- [ ] Error messages don't leak info
- [ ] No credentials in code
- [ ] Dependencies up to date
- [ ] Error logging enabled

### Monitoring

- [ ] Monitor API usage
- [ ] Log errors to external service
- [ ] Set up uptime monitoring
- [ ] Get alerts on failure

### Example Error Logging (with Sentry)

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

---

## 📊 Performance Tips for Production

### Gunicorn Configuration

```bash
gunicorn -w 4 \
         -b 0.0.0.0:5000 \
         --timeout 60 \
         --access-logfile - \
         --error-logfile - \
         app:app
```

- `-w 4`: 4 worker processes
- `--timeout 60`: 60 second timeout
- Adjust workers based on CPU cores

### Nginx Optimization

```nginx
upstream dota2 {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    location / {
        proxy_pass http://dota2;

        # Caching
        proxy_cache_valid 200 1m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
    }
}
```

---

## 🔄 Continuous Deployment

### GitHub Actions Example

```yaml
name: Deploy to Heroku

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "your-app-name"
          heroku_email: "your-email@example.com"
```

---

## 🐛 Troubleshooting Deployments

### "Module not found" Error

```bash
# Make sure requirements.txt is complete
pip freeze > requirements.txt
# Or manually add missing packages
```

### "API key not set"

```bash
# Check environment variables
echo $DOTA2_API_KEY

# Set in production
export DOTA2_API_KEY=your_key
# Or use platform's env var setting
```

### Port already in use

```bash
# Use a different port
python app.py --port 8080
# Or kill the process
lsof -ti:5000 | xargs kill -9
```

### 502 Bad Gateway (Nginx error)

```bash
# Check if app is running
ps aux | grep gunicorn

# Check app logs
journalctl -u dota2-parser -n 50

# Restart services
sudo systemctl restart dota2-parser
sudo systemctl restart nginx
```

---

## 📈 Scaling for High Traffic

### Horizontal Scaling

- Deploy multiple instances
- Use load balancer (Nginx, HAProxy)
- Each instance handles subset of requests

### Vertical Scaling

- Increase server size
- More CPU/RAM
- Use caching (Redis)

### Caching Layer

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_item_price(item_name):
    # Cache results for repeated items
    pass
```

---

## 🎯 Recommended Setup (Production)

**For personal projects (FREE):**

1. **PythonAnywhere** (FREE!)
   - No credit card required
   - Perfect for learning/personal use
   - Easy web interface
   - See: PYTHONANYWHERE_DEPLOYMENT.md

**Best balance of cost/reliability:**

2. **DigitalOcean App Platform** ($5/month)
   - Auto-deploys from GitHub
   - Automatic SSL
   - Easy scaling

**Or**

3. **Heroku** (Free tier available)
   - One-command deployment
   - Built-in monitoring
   - Simple scaling

**Or for maximum control:**

4. **AWS EC2 + RDS** ($5-20/month)
   - Full control
   - Highly scalable
   - Auto-scaling groups

---

## 📝 Deployment Checklist (Before Going Live)

```
□ Code works locally
□ requirements.txt complete
□ .env.example created
□ No hardcoded secrets
□ Error handling working
□ Logging configured
□ API key is valid
□ Domain/URL decided
□ HTTPS configured
□ Uptime monitoring set
□ Error logging set
□ Backup plan ready
```

---

**Ready to deploy? Pick an option above and follow the steps! 🚀**

Questions? Check the main README.md for more info.
