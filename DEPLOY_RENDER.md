# Deploy FLICKPICK ML API to Render.com (100% FREE)

## Why Render?
- ✅ 100% FREE forever
- ✅ No credit card required
- ✅ No usage limits
- ⚠️ Services sleep after 15 min idle (10-30s wake up)

## Step-by-Step Deployment

### Step 1: Push to GitHub (5 minutes)

```bash
cd e:\Coding project\flickpick\ml_api

git init
git add .
git commit -m "ML API for FLICKPICK - Render deployment"

# Create GitHub repo
git remote add origin https://github.com/YOUR_USERNAME/flickpick-ml-api.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Render (3 minutes)

1. Go to [Render.com](https://render.com)
2. Sign up with GitHub (free)
3. Click "New" → "Web Service"
4. Connect your `flickpick-ml-api` repo
5. Configure:
   - Name: `flickpick-ml-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - Instance Type: `Free`

6. Click "Create Web Service"

### Step 3: Add Environment Variable (1 minute)

1. In your service dashboard → "Environment" tab
2. Add Environment Variable:
   - Key: `TMDB_API_KEY`
   - Value: `5e338db773fdec4213f2c68748ff8d36`
3. Render automatically redeploys

### Step 4: Get Your URL

Render gives you a URL like:
```
https://flickpick-ml-api.onrender.com
```

Test it:
```
https://flickpick-ml-api.onrender.com/health
```

## 🚨 Important: Render Sleep Mode

**Free tier services sleep after 15 minutes of inactivity**

- First request after sleep: 10-30 seconds delay
- Subsequent requests: Fast
- Solution: Keep a "pinger" to keep it alive (optional)

**Optional: Keep Alive Script**
```javascript
// Add to your Django app to ping ML API every 10 minutes
setInterval(async () => {
  try {
    await fetch('https://your-api.onrender.com/health');
    console.log('Kept ML API alive');
  } catch (e) {
    console.log('Ping failed');
  }
}, 600000); // 10 minutes
```

## 🔗 Connect Django to Render API

Update `flickpick/settings.py`:
```python
# ML API Configuration
ML_API_URL = "https://flickpick-ml-api.onrender.com"
```

Update `api/views.py`:
```python
import requests
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations(request):
    """Get recommendations from ML API"""
    try:
        profile = request.user.profile
        preferences = profile.preferences
        
        # Get user ratings
        user_ratings = Review.objects.filter(user=request.user).values('movie__tmdb_id', 'rating')
        ratings_dict = {str(r['movie__tmdb_id']): r['rating'] for r in user_ratings}
        
        # Call ML API (with timeout for Render wake up)
        response = requests.post(
            f"{settings.ML_API_URL}/recommendations",
            json={
                "user_id": str(request.user.id),
                "preferences": preferences,
                "ratings": ratings_dict,
                "n_recommendations": 24
            },
            timeout=30  # Longer timeout for Render wake up
        )
        
        if response.status_code == 200:
            data = response.json()
            return Response({
                "movies": data.get("recommendations", []),
                "source": "render-ml-api"
            })
        else:
            # Fallback to local recommendations
            return get_local_recommendations(request)
            
    except requests.exceptions.Timeout:
        # Render is waking up, use local recommendations
        return get_local_recommendations(request)
    except Exception as e:
        return get_local_recommendations(request)

def get_local_recommendations(request):
    """Fallback local recommendations"""
    profile = request.user.profile
    preferences = profile.preferences
    preferred_genres = preferences.get('genres', [])
    
    if not preferred_genres:
        popular_movies = Movie.objects.filter(popularity__gte=50).order_by('-popularity')[:20]
    else:
        recommended_movies = Movie.objects.filter(
            genres__contains=[int(g) for g in preferred_genres]
        ).order_by('-popularity', '-rating')[:24]
    
    movie_data = []
    for movie in recommended_movies:
        movie_data.append({
            'id': movie.tmdb_id,
            'title': movie.title,
            'poster': movie.poster_url,
            'rating': movie.rating,
            'year': movie.year
        })
    
    return Response({
        'movies': movie_data,
        'source': 'local-fallback'
    })
```

## 🧪 Test the Render API

```bash
# Health check
curl https://flickpick-ml-api.onrender.com/health

# Get recommendations (first call may take 20s)
curl -X POST https://flickpick-ml-api.onrender.com/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "preferences": {"genres": [28, 35, 18]},
    "ratings": {},
    "n_recommendations": 10
  }'

# Second call should be fast
curl -X POST https://flickpick-ml-api.onrender.com/recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "preferences": {"genres": [28]}, "n_recommendations": 5}'
```

## 📊 Monitoring

- Render dashboard shows logs and metrics
- Free tier includes basic monitoring
- API response times visible in dashboard

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | Service is sleeping, wait 30s and retry |
| 500 Internal Error | Check logs in Render dashboard |
| Slow first request | Normal for Render free tier |
| Connection timeout | Increase timeout to 30s |

## 💡 Pro Tips

1. **Keep API Warm**: Ping every 10 minutes
2. **Fallback Logic**: Always have local recommendations as backup
3. **Error Handling**: Handle timeouts gracefully
4. **Monitor**: Check Render dashboard for issues

## 🎯 Final Setup

Once deployed:
1. Update Django with your Render URL
2. Test the full flow: Register → Survey → Recommendations
3. Monitor for any issues

**Your ML API is now 100% free on Render! 🎉**
