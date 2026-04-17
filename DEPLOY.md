# Deploy FLICKPICK ML API to Railway.app

## Prerequisites

1. [Railway.app](https://railway.app) account (free tier available)
2. [GitHub](https://github.com) account
3. TMDB API Key ([Get one here](https://www.themoviedb.org/settings/api))

## Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
# Navigate to ml_api folder
cd e:\Coding project\flickpick\ml_api

# Initialize git repo
git init

# Add all files
git add .

# Commit
git commit -m "Initial ML API for FLICKPICK"

# Create GitHub repo (via web or CLI) and push
git remote add origin https://github.com/YOUR_USERNAME/flickpick-ml-api.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `flickpick-ml-api` repo
5. Railway will auto-detect Python and deploy

### Step 3: Set Environment Variables

1. In Railway dashboard, go to your project
2. Click "Variables" tab
3. Add these variables:
   ```
   TMDB_API_KEY=5e338db773fdec4213f2c68748ff8d36
   PORT=5000
   ```

### Step 4: Get Your API URL

1. After deployment, Railway gives you a URL like:
   ```
   https://flickpick-ml-api.up.railway.app
   ```

2. Test it's working:
   ```
   https://flickpick-ml-api.up.railway.app/health
   ```

## Update Django to Use ML API

In `flickpick/settings.py`, add:

```python
# ML API Configuration
ML_API_URL = "https://your-railway-url.up.railway.app"  # Replace with your URL
ML_API_KEY = os.environ.get('ML_API_KEY', '')  # If you add API key protection
```

In `api/views.py`, update the recommendations function:

```python
import requests

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations(request):
    """Get recommendations from ML API"""
    try:
        # Get user preferences
        profile = request.user.profile
        preferences = profile.preferences
        
        # Get user ratings
        user_ratings = Review.objects.filter(user=request.user).values('movie__tmdb_id', 'rating')
        ratings_dict = {str(r['movie__tmdb_id']): r['rating'] for r in user_ratings}
        
        # Call ML API
        ml_api_url = settings.ML_API_URL
        response = requests.post(
            f"{ml_api_url}/recommendations",
            json={
                "user_id": str(request.user.id),
                "preferences": preferences,
                "ratings": ratings_dict,
                "n_recommendations": 24
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return Response({
                "movies": data.get("recommendations", []),
                "source": "ml-api"
            })
        else:
            # Fallback to local recommendations
            return get_local_recommendations(request)
            
    except Exception as e:
        # Fallback to local recommendations on error
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
    
    # ... serialize movies ...
```

## Testing the API

### Test Endpoints:

```bash
# Health check
curl https://your-url.up.railway.app/health

# Get recommendations
curl -X POST https://your-url.up.railway.app/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "preferences": {"genres": [28, 35, 18]},
    "ratings": {},
    "n_recommendations": 10
  }'

# Get similar movies
curl https://your-url.up.railway.app/similar/550

# Get popular movies
curl https://your-url.up.railway.app/popular
```

## Monitoring

- Railway dashboard shows logs, metrics, and deployment status
- Set up alerts for API downtime
- Monitor API response times

## Troubleshooting

### API returns 500 errors:
- Check Railway logs in dashboard
- Verify TMDB_API_KEY is set correctly
- Ensure all dependencies are installed

### CORS errors:
- The Flask-CORS is configured to allow all origins
- Check if requests include proper headers

### Slow response:
- TMDB API might be slow
- Add caching layer (Redis) for production

## Next Steps

1. Add API authentication (API keys)
2. Implement caching with Redis
3. Add rate limiting
4. Set up monitoring/alerting
5. Add A/B testing for recommendation algorithms
