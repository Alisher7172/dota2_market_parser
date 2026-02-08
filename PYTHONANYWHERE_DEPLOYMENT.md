# 🚀 PythonAnywhere Deployment Guide

Complete step-by-step guide to deploy your Dota 2 Market Parser on PythonAnywhere.

---

## 📋 Prerequisites

- ✅ PythonAnywhere account (free tier works!)
- ✅ Your Dota2.net API key
- ✅ Project files ready
- ✅ 15 minutes

---

## 🎯 Step 1: Create PythonAnywhere Account

1. Go to **https://www.pythonanywhere.com**
2. Click **"Pricing & signup"**
3. Choose **"Create a Beginner account"** (FREE)
4. Verify your email
5. Log in to your dashboard

---

## 📁 Step 2: Upload Your Files

### Option A: Using Git (Recommended)

1. **Create a GitHub repository** (if you haven't):

   ```bash
   cd c:\Users\user\Downloads\clo
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/dota2-parser.git
   git push -u origin main
   ```

2. **On PythonAnywhere**, open a **Bash console** from the dashboard

3. **Clone your repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dota2-parser.git
   cd dota2-parser
   ```

### Option B: Manual Upload (Simple)

1. On PythonAnywhere dashboard, click **"Files"**
2. Navigate to: `/home/YOUR_USERNAME/`
3. Click **"Upload a file"** for each file:
   - `app.py`
   - `requirements.txt`
   - `wsgi.py`
   - `.env.example`
4. Create folder: `templates`
5. Upload `index.html` into `templates/`

---

## 🐍 Step 3: Set Up Python Environment

1. **Open a Bash console** (from PythonAnywhere dashboard)

2. **Create virtual environment**:

   ```bash
   cd ~/dota2-parser
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Create .env file**:

   ```bash
   cp .env.example .env
   nano .env
   ```

5. **Add your API key** in the nano editor:

   ```
   DOTA2_API_KEY=your_actual_api_key_here
   ```

   - Press `Ctrl+X`, then `Y`, then `Enter` to save

6. **Test the app**:

   ```bash
   python app.py
   ```

   - If you see "API Key: LOADED", you're good!
   - Press `Ctrl+C` to stop

---

## 🌐 Step 4: Configure Web App

1. **Go to PythonAnywhere dashboard**
2. Click **"Web"** tab
3. Click **"Add a new web app"**
4. Click **"Next"** (for free domain)
5. Choose **"Manual configuration"**
6. Select **Python 3.11** (or 3.10, NOT 3.12 - see troubleshooting)
7. Click **"Next"**

---

## ⚙️ Step 5: Configure WSGI File

1. On the **Web** tab, scroll to **"Code"** section
2. Click on the **WSGI configuration file** link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. **Delete all the content**
4. **Replace with this**:

```python
import sys
import os
from pathlib import Path

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/dota2-parser'  # CHANGE THIS!
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
env_path = Path(project_home) / '.env'
load_dotenv(dotenv_path=env_path)

# Import Flask app
from app import app as application
```

5. **Important**: Replace `YOUR_USERNAME` with your actual PythonAnywhere username!
6. Click **"Save"** (top right)

---

## 🔧 Step 6: Set Virtual Environment Path

1. Still on the **Web** tab
2. Scroll to **"Virtualenv"** section
3. Click the link: **"Enter path to a virtualenv"**
4. Enter: `/home/YOUR_USERNAME/dota2-parser/venv`
   - Replace `YOUR_USERNAME` with your actual username
5. Click the checkmark ✓

---

## 📝 Step 7: Configure Static Files (Optional but Helpful)

1. Scroll to **"Static files"** section
2. Add these mappings:

| URL        | Directory                                  |
| ---------- | ------------------------------------------ |
| `/static/` | `/home/YOUR_USERNAME/dota2-parser/static/` |

(Not critical for this app, but good practice)

---

## 🚀 Step 8: Launch Your App!

1. Scroll to top of **Web** tab
2. Click the big green **"Reload"** button
3. Wait for reload to complete
4. Click the link: **`https://YOUR_USERNAME.pythonanywhere.com`**

**🎉 Your app should now be live!**

---

## 🧪 Step 9: Test Your Deployment

1. Visit: `https://YOUR_USERNAME.pythonanywhere.com`
2. You should see the beautiful gradient UI
3. Enter an item name like: `Arcana`
4. Click **"Parse Items"**
5. Results should appear in ~1 second

---

## 🐛 Troubleshooting

### ❌ "Something went wrong"

**Check Error Logs:**

1. Go to **Web** tab
2. Scroll to **"Log files"** section
3. Click **"Error log"** link
4. Look for Python errors

**Common issues:**

#### 1. "No module named 'app'"

- **Fix**: Check WSGI file has correct path to project
- Make sure `project_home = '/home/YOUR_USERNAME/dota2-parser'`

#### 2. "No module named 'flask'" or similar

- **Fix**: Virtual environment not set correctly
- Check **Virtualenv** path: `/home/YOUR_USERNAME/dota2-parser/venv`

#### 3. "API Key not loaded"

- **Fix**: `.env` file not created or incorrect
- SSH into bash console:
  ```bash
  cd ~/dota2-parser
  cat .env
  # Should show: DOTA2_API_KEY=your_key
  ```

#### 4. "ModuleNotFoundError: dotenv"

- **Fix**: Reinstall in virtual environment:
  ```bash
  cd ~/dota2-parser
  source venv/bin/activate
  pip install python-dotenv
  ```

#### 5. "ImportError: cannot import name 'app'"

- **Fix**: Check `app.py` is in project directory
- Run: `ls ~/dota2-parser/app.py` (should exist)

#### 6. "Template not found"

- **Fix**: Check templates folder exists with index.html:
  ```bash
  ls ~/dota2-parser/templates/index.html
  ```

#### 7. "Failed building wheel for aiohttp" (Compilation errors)

- **Problem**: Using Python 3.12 which is incompatible with older aiohttp versions
- **Error shows**: `error: 'PyLongObject' has no member named 'ob_digit'`

**Solution A - Use Python 3.11** (Recommended):

```bash
# Delete old virtual environment
cd ~/dota2-parser
rm -rf venv

# Create new one with Python 3.11
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Solution B - Use Python 3.10**:

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then reload your web app from the Web tab.

---

## 🔄 How to Update Your App

### If Using Git:

1. **Update local code**, commit, and push:

   ```bash
   git add .
   git commit -m "Updated features"
   git push
   ```

2. **On PythonAnywhere Bash console**:

   ```bash
   cd ~/dota2-parser
   git pull
   source venv/bin/activate
   pip install -r requirements.txt  # If requirements changed
   ```

3. **Reload web app**:
   - Go to **Web** tab
   - Click **"Reload"** button

### If Manually Uploading:

1. Go to **Files** tab
2. Navigate to your file
3. Click **"Edit"** or upload new version
4. **Reload** web app from **Web** tab

---

## 📊 Monitoring Your App

### Check Logs

**Error Log:**

- Web tab → Log files → Error log
- Shows Python errors and exceptions

**Server Log:**

- Web tab → Log files → Server log
- Shows HTTP requests

**Access Log:**

- Web tab → Log files → Access log
- Shows all visitors

### View in Bash Console

```bash
# View recent errors
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log

# View server log
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.server.log
```

---

## 🔐 Environment Variables (Advanced)

If you need to add more environment variables:

1. **Edit .env file**:

   ```bash
   cd ~/dota2-parser
   nano .env
   ```

2. **Add variables**:

   ```
   DOTA2_API_KEY=your_key
   FLASK_ENV=production
   USD_TO_RUB_RATE=90
   ```

3. **Reload app** from Web tab

---

## ⚡ Performance Tips

### Free Tier Limits

- ✅ 100,000 requests/day
- ✅ Good for personal use
- ✅ Sleeps after inactivity (first request takes ~10s)

### Keep Awake (Optional)

Use a service like UptimeRobot to ping your app every 5 minutes:

- URL to ping: `https://YOUR_USERNAME.pythonanywhere.com`

### Upgrade If Needed

- **Hacker tier ($5/month)**: No sleeping, custom domains
- **Web Dev tier ($12/month)**: More resources, MySQL

---

## 📁 Final File Structure on PythonAnywhere

```
/home/YOUR_USERNAME/dota2-parser/
├── app.py                    # Main Flask app
├── wsgi.py                   # WSGI config (optional)
├── requirements.txt          # Dependencies
├── .env                      # API key (NEVER commit!)
├── .env.example             # Template
├── templates/
│   └── index.html           # Frontend
└── venv/                    # Virtual environment
    └── ...
```

---

## 🎯 Quick Reference Commands

```bash
# Activate virtual environment
cd ~/dota2-parser && source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# View environment variables
cat .env

# Edit environment variables
nano .env

# Test app locally
python app.py

# View error logs
tail -20 /var/log/YOUR_USERNAME.pythonanywhere.com.error.log

# Update from Git
git pull && pip install -r requirements.txt
```

---

## 🌐 Accessing Your App

**Your URL:**

```
https://YOUR_USERNAME.pythonanywhere.com
```

**API Health Check:**

```
https://YOUR_USERNAME.pythonanywhere.com/api/health
```

**Share with friends:**
Just send them your URL! 🎉

---

## 🔄 Migration Checklist

Before going live:

- [ ] All files uploaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file created with API key
- [ ] WSGI file configured
- [ ] Virtualenv path set
- [ ] App reloaded
- [ ] Test with 1-2 items
- [ ] Check error logs (should be empty)
- [ ] Share URL with friends

---

## 💰 Cost Breakdown

**Free Tier:**

- ✅ One web app
- ✅ 512 MB disk space
- ✅ 100,000 requests/day
- ✅ Perfect for personal use

**Paid Tiers** (if you need more):

- **$5/month**: Multiple apps, no sleeping, custom domain
- **$12/month**: More CPU/RAM, MySQL, scheduled tasks

---

## 🆘 Getting Help

**PythonAnywhere Forums:**
https://www.pythonanywhere.com/forums/

**PythonAnywhere Help:**
https://help.pythonanywhere.com/

**Check Logs First:**
Most issues are visible in error logs!

---

## 🎉 Success Checklist

You'll know it's working when:

✅ URL loads without errors
✅ You see the gradient UI
✅ Can type item names
✅ Results appear after clicking "Parse"
✅ No errors in error log
✅ Health endpoint returns `{"status": "ok"}`

---

## 📞 Next Steps

1. **Test thoroughly** with various items
2. **Monitor error logs** for first few days
3. **Share your URL** with friends
4. **Consider custom domain** ($5/month tier)
5. **Set up uptime monitoring** (UptimeRobot)

---

**Congratulations! Your Dota 2 Market Parser is now live on the internet! 🚀**

Need help? Check error logs first, then PythonAnywhere forums!
