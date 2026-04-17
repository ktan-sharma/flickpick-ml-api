# 🚀 Quick Start - Deploy ML API to Railway

## Files Created

```
ml_api/
├── app.py              # Flask ML API with recommendation algorithms
├── requirements.txt    # Python dependencies
├── Procfile           # Railway process configuration
├── runtime.txt        # Python version
├── railway.json       # Railway deployment config
├── .gitignore         # Git ignore rules
├── README.md          # Full documentation
├── DEPLOY.md          # Deployment guide
└── QUICKSTART.md      # This file
```

## 🎯 Quick Deploy Steps

### 1. Push to GitHub (5 minutes)

```bash
cd e:\Coding project\flickpick\ml_api

git init
git add .
git commit -m "Initial ML API deployment"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/flickpick-ml-api.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Railway (3 minutes)

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select `flickpick-ml-api`
4. Done! Railway auto-deploys

### 3. Add Environment Variable (1 minute)

1. In Railway dashboard → "Variables" tab
2. Add: `TMDB_API_KEY=5e338db773fdec4213f2c68748ff8d36`
3. Railway redeploys automatically

### 4. Get Your URL

Railway gives you a URL like:
```
https://flickpick-ml-api.up.railway.app
```

Test it:
```
https://flickpick-ml-api.up.railway.app/health
```

## 🔗 Connect to Django

Update `api/views.py`:

```python
import requests
from django.conf import settings

ML_API_URL = "https://your-railway-url.up.railway.app"

# In recommendations() function:
response = requests.post(
    f"{ML_API_URL}/recommendations",
    json={
        "user_id": str(request.user.id),
        "preferences": profile.preferences,
        "n_recommendations": 24
    },
    timeout=10
)
```

## ✅ API Endpoints Available

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/recommendations` | POST | Get personalized movies |
| `/similar/<id>` | GET | Get similar movies |
| `/popular` | GET | Get popular movies |
| `/feedback` | POST | Submit feedback |

## 🧪 Test the API

```bash
# Health check
curl https://your-url.up.railway.app/health

# Get recommendations
curl -X POST https://your-url.up.railway.app/recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": "123", "preferences": {"genres": [28, 35]}, "n_recommendations": 10}'
```

## 🎬 How It Works

1. **User Registers** → Django creates account
2. **Survey Page** → User selects favorite genres
3. **Save Preferences** → Django stores in UserProfile
4. **Home Page** → Frontend calls `/api/recommendations/`
5. **Django → ML API** → Fetches personalized movies from TMDB
6. **Display** → Shows "Recommended for You" section

## 📊 ML Algorithm

- **Content-Based**: Matches movies to preferred genres
- **Collaborative**: Finds similar users (future feature)
- **Hybrid**: Combines both approaches
- **TMDB Integration**: Real-time movie data

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| 500 errors | Check TMDB_API_KEY is set |
| Slow responses | Normal - TMDB API can be slow |
| CORS errors | Flask-CORS allows all origins |
| No recommendations | User hasn't completed survey |

## 💡 Next Features

- [ ] Matrix factorization (SVD)
- [ ] Neural collaborative filtering
- [ ] Redis caching
- [ ] Real-time model updates
- [ ] A/B testing

## 📞 Support

Check `DEPLOY.md` for detailed deployment guide.
Check `README.md` for full API documentation.

---

**Your ML API is ready to deploy! 🎉**
