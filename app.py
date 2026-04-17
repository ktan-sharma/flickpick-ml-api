"""
FLICKPICK ML Recommendation API
A Flask-based service that provides movie recommendations using ML algorithms
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# TMDB API Configuration
TMDB_API_KEY = "5e338db773fdec4213f2c68748ff8d36"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Cache for movie data
movie_cache = {}

def fetch_movie_features(movie_id):
    """Fetch movie features from TMDB"""
    if movie_id in movie_cache:
        return movie_cache[movie_id]
    
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            features = {
                'id': movie_id,
                'title': data.get('title', ''),
                'genres': [g['name'] for g in data.get('genres', [])],
                'overview': data.get('overview', ''),
                'popularity': data.get('popularity', 0),
                'rating': data.get('vote_average', 0),
                'poster': f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}" if data.get('poster_path') else None,
                'year': data.get('release_date', '')[:4] if data.get('release_date') else ''
            }
            movie_cache[movie_id] = features
            return features
    except Exception as e:
        print(f"Error fetching movie {movie_id}: {e}")
    return None

def fetch_movies_by_genre(genre_id, page=1):
    """Fetch movies by genre from TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc&page={page}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        print(f"Error fetching genre {genre_id}: {e}")
    return []

def fetch_similar_movies(movie_id):
    """Fetch similar movies from TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/movie/{movie_id}/similar?api_key={TMDB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('results', [])
    except Exception as e:
        print(f"Error fetching similar movies for {movie_id}: {e}")
    return []

class ContentBasedRecommender:
    """Content-based filtering using movie features"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def get_recommendations(self, user_preferences, n_recommendations=20):
        """
        Get recommendations based on user genre preferences
        
        user_preferences: dict with 'genres' list of genre IDs
        """
        preferred_genres = user_preferences.get('genres', [])
        
        if not preferred_genres:
            # Return popular movies
            return self._get_popular_movies(n_recommendations)
        
        # Fetch movies from preferred genres
        all_movies = []
        for genre_id in preferred_genres[:3]:  # Limit to top 3 genres
            movies = fetch_movies_by_genre(genre_id, page=1)
            all_movies.extend(movies[:10])  # Get top 10 from each genre
        
        # Remove duplicates and sort by popularity and rating
        seen_ids = set()
        unique_movies = []
        for movie in all_movies:
            if movie['id'] not in seen_ids:
                seen_ids.add(movie['id'])
                unique_movies.append(movie)
        
        # Sort by weighted score (popularity * rating)
        unique_movies.sort(
            key=lambda x: (x.get('popularity', 0) * x.get('vote_average', 1)), 
            reverse=True
        )
        
        return unique_movies[:n_recommendations]
    
    def _get_popular_movies(self, n=20):
        """Get popular movies when no preferences set"""
        try:
            url = f"{TMDB_BASE_URL}/movie/popular?api_key={TMDB_API_KEY}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get('results', [])[:n]
        except Exception as e:
            print(f"Error fetching popular movies: {e}")
        return []
    
    def get_similar_movies(self, movie_id, n_recommendations=10):
        """Get movies similar to a given movie"""
        similar = fetch_similar_movies(movie_id)
        return similar[:n_recommendations]

class CollaborativeRecommender:
    """Simple collaborative filtering based on user behavior"""
    
    def __init__(self):
        self.user_ratings = {}  # In production, this comes from database
    
    def add_rating(self, user_id, movie_id, rating):
        """Store user rating"""
        if user_id not in self.user_ratings:
            self.user_ratings[user_id] = {}
        self.user_ratings[user_id][movie_id] = rating
    
    def get_recommendations(self, user_id, n_recommendations=10):
        """Get recommendations based on similar users"""
        # Simplified collaborative filtering
        # In production, you'd use matrix factorization (SVD, ALS, etc.)
        
        if user_id not in self.user_ratings:
            return []
        
        user_movies = set(self.user_ratings[user_id].keys())
        
        # Find similar users (users who rated same movies similarly)
        similar_users = []
        for other_id, ratings in self.user_ratings.items():
            if other_id == user_id:
                continue
            
            # Calculate similarity
            common_movies = user_movies & set(ratings.keys())
            if len(common_movies) < 2:
                continue
            
            # Simple Pearson correlation
            user_ratings_list = [self.user_ratings[user_id][m] for m in common_movies]
            other_ratings_list = [ratings[m] for m in common_movies]
            
            if np.std(user_ratings_list) == 0 or np.std(other_ratings_list) == 0:
                continue
            
            correlation = np.corrcoef(user_ratings_list, other_ratings_list)[0, 1]
            if not np.isnan(correlation) and correlation > 0.5:
                similar_users.append((other_id, correlation))
        
        # Get recommendations from similar users
        recommendations = []
        similar_users.sort(key=lambda x: x[1], reverse=True)
        
        for similar_user, similarity in similar_users[:5]:
            for movie_id, rating in self.user_ratings[similar_user].items():
                if movie_id not in user_movies and rating >= 4:
                    recommendations.append((movie_id, rating * similarity))
        
        # Sort by weighted rating
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in recommendations[:n_recommendations]]

# Initialize recommenders
content_recommender = ContentBasedRecommender()
collaborative_recommender = CollaborativeRecommender()

@app.route('/')
def index():
    return jsonify({
        "message": "FLICKPICK ML Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "/recommendations": "POST - Get recommendations for a user",
            "/similar/<movie_id>": "GET - Get similar movies",
            "/popular": "GET - Get popular movies",
            "/health": "GET - Health check"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    """
    Get personalized movie recommendations
    
    Request body:
    {
        "user_id": "user123",
        "preferences": {
            "genres": [28, 35, 18],  // TMDB genre IDs
            "actors": [],
            "directors": []
        },
        "ratings": {
            "movie_id1": 5,
            "movie_id2": 4
        },
        "n_recommendations": 20
    }
    """
    try:
        data = request.json
        
        user_id = data.get('user_id', 'anonymous')
        preferences = data.get('preferences', {})
        ratings = data.get('ratings', {})
        n = data.get('n_recommendations', 20)
        
        # Add user ratings to collaborative model
        for movie_id, rating in ratings.items():
            collaborative_recommender.add_rating(user_id, movie_id, rating)
        
        # Get content-based recommendations
        content_recs = content_recommender.get_recommendations(preferences, n)
        
        # Get collaborative recommendations if user has ratings
        collaborative_recs = []
        if ratings:
            collaborative_recs = collaborative_recommender.get_recommendations(user_id, n // 2)
            # Fetch details for collaborative recommendations
            for movie_id in collaborative_recs:
                movie = fetch_movie_features(movie_id)
                if movie:
                    content_recs.append(movie)
        
        # Remove duplicates
        seen_ids = set()
        unique_recs = []
        for movie in content_recs:
            movie_id = movie.get('id')
            if movie_id and movie_id not in seen_ids:
                seen_ids.add(movie_id)
                unique_recs.append({
                    'id': movie_id,
                    'title': movie.get('title', ''),
                    'poster': movie.get('poster_path') or movie.get('poster'),
                    'rating': movie.get('vote_average', 0) / 2,  # Convert to 5-star scale
                    'year': movie.get('release_date', '')[:4] if movie.get('release_date') else ''
                })
        
        return jsonify({
            "success": True,
            "recommendations": unique_recs[:n],
            "source": "hybrid" if ratings else "content-based",
            "user_id": user_id
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/similar/<int:movie_id>', methods=['GET'])
def get_similar(movie_id):
    """Get movies similar to the given movie"""
    try:
        n = request.args.get('n', 10, type=int)
        similar_movies = content_recommender.get_similar_movies(movie_id, n)
        
        return jsonify({
            "success": True,
            "movie_id": movie_id,
            "similar_movies": similar_movies
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/popular', methods=['GET'])
def get_popular():
    """Get popular movies"""
    try:
        n = request.args.get('n', 20, type=int)
        popular = content_recommender._get_popular_movies(n)
        
        movies = []
        for movie in popular:
            movies.append({
                'id': movie.get('id'),
                'title': movie.get('title', ''),
                'poster': movie.get('poster_path'),
                'rating': movie.get('vote_average', 0) / 2,
                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else ''
            })
        
        return jsonify({
            "success": True,
            "movies": movies
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """Receive feedback on recommendations to improve model"""
    try:
        data = request.json
        user_id = data.get('user_id')
        movie_id = data.get('movie_id')
        liked = data.get('liked')  # True/False
        
        # In production, store this feedback in database
        # and use it to retrain the model periodically
        
        return jsonify({
            "success": True,
            "message": "Feedback recorded"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
