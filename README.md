# FLICKPICK ML Recommendation API

A Flask-based machine learning API that provides personalized movie recommendations using content-based and collaborative filtering algorithms.

## Features

- **Content-Based Filtering**: Recommends movies based on genre preferences
- **Collaborative Filtering**: Recommends based on similar user behavior
- **Hybrid Approach**: Combines both methods for better recommendations
- **TMDB Integration**: Fetches movie data from The Movie Database API

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Get Recommendations
```http
POST /recommendations
Content-Type: application/json

{
    "user_id": "user123",
    "preferences": {
        "genres": [28, 35, 18],  // Action, Comedy, Drama
        "actors": [],
        "directors": []
    },
    "ratings": {
        "550": 5,  // Fight Club
        "13": 4    // Forrest Gump
    },
    "n_recommendations": 20
}
```

### 2. Get Similar Movies
```http
GET /similar/550?n=10
```

### 3. Get Popular Movies
```http
GET /popular?n=20
```

## Deployment Options

### Free Hosting

#### Railway.app (Recommended)
1. Push code to GitHub
2. Connect Railway to your repo
3. Add environment variables
4. Deploy

#### Render.com
1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`

#### Heroku
```bash
heroku create flickpick-ml-api
heroku config:set TMDB_API_KEY=your_key
heroku git:remote -a flickpick-ml-api
heroku push
```

## Environment Variables

- `TMDB_API_KEY`: Your TMDB API key
- `PORT`: Server port (default: 5000)

## How It Works

1. **User Registration**: New users complete genre preference survey
2. **Content-Based**: Recommendations based on preferred genres from TMDB
3. **Collaborative**: Recommendations based on users with similar tastes
4. **Hybrid**: Combines both approaches for optimal results

## Integration with Django

The Django backend calls this API to get recommendations:

```python
import requests

def get_ml_recommendations(user):
    response = requests.post(
        'http://localhost:5000/recommendations',
        json={
            'user_id': user.id,
            'preferences': user.profile.preferences,
            'ratings': get_user_ratings(user)
        }
    )
    return response.json()['recommendations']
```

## Future Improvements

- Matrix factorization (SVD, NMF)
- Deep learning models (neural collaborative filtering)
- Real-time model updates
- A/B testing framework
