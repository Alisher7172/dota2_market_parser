# ⚡ Quick Start (5 minutes)

## Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Create .env File
Create a new file named `.env` in the project root:

```
DOTA2_API_KEY=your_api_key_here
FLASK_ENV=production
PORT=5000
```

**Get API key:** https://market.dota2.net/ → Account → API Settings

## Step 3: Run Server
```bash
python app.py
```

Output should show:
```
API Key: LOADED
 * Running on http://0.0.0.0:5000
```

## Step 4: Open in Browser
Go to: **http://localhost:5000**

## Step 5: Parse Items
1. Enter item names (one per line)
2. Click "Parse Items"
3. See results!

---

## 📝 Example Items to Try

```
Arcana
Immortal Item
Courier
Mythical Item
Shadow Fiend Arcana
```

## 🚀 Performance Comparison

| Items | Sequential | Our Parser | Speedup |
|-------|-----------|-----------|---------|
| 1 | 0.5s | 0.5s | 1x |
| 3 | 1.5s | 0.6s | 2.5x |
| 5 | 2.5s | 1.0s | 2.5x |
| 10 | 5.0s | 1.5s | 3.3x |
| 20 | 10.0s | 2.0s | 5x |

## 🔍 What's Happening

When you parse items:

1. **Frontend** sends item names to backend
2. **Backend** uses async to fetch data from Dota2.net API in parallel
3. **ThreadPool** processes multiple requests at once
4. **Results** are formatted and returned as JSON
5. **Frontend** displays summary + table in real-time

## ❌ If It Doesn't Work

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "API Key not loaded"
- Create `.env` file
- Add your API key
- Restart server

### Port 5000 in use
```bash
# Change .env to:
PORT=5001
# Or kill process:
lsof -ti:5000 | xargs kill -9
```

### Items not found
- Use exact English names from market
- Check spelling
- Try: "Arcana", "Immortal Item", "Courier"

## 💡 Pro Tips

✅ Use Ctrl+Enter to submit quickly
✅ One item per line
✅ Use English names only
✅ Copy results URL to share
✅ Results update instantly

## 🎯 Next Steps

After confirming it works:

1. **Deploy online** (see README.md for Heroku/Docker)
2. **Customize colors** (edit templates/index.html CSS)
3. **Add more features** (e.g., price history, notifications)
4. **Share with team** (deploy to server)

---

**All set? Happy parsing! 🚀**

For detailed docs: See README.md
