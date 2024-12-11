from flask import Flask, request, render_template, jsonify
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import ast
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask app
app = Flask(__name__, static_folder="static")

# Load and preprocess data at startup
def load_and_preprocess_data():
    data = pd.read_csv('dataset.csv')

    # Normalize columns
    scaler = MinMaxScaler()
    columns_to_normalize = [
        'crime_rate', 'parks_pp', 'pop_density', 'nonwhite_percent', 'foreign_born_percent', 'restaurants',
        'nightlife', 'transit', 'car_percent', 'activities', 'republican', 'democrat', 'max_avg_high', 'mean_diff',
        'natural-resources_percent', 'construction_percent', 'manufacturing_percent', 'sales_percent',
        'transportation_percent', 'information_percent', 'finance_percent', 'scientific_percent', 'education_percent',
        'arts_percent', 'other_percent', 'public-administration_percent'
    ]
    data[columns_to_normalize] = scaler.fit_transform(data[columns_to_normalize])

    # Parse and clean bullets column
    data['bullets'] = data['bullets'].apply(lambda x: x.replace('\xa0', ' ') if isinstance(x, str) else x)
    data['bullets'] = data['bullets'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    return data

data = load_and_preprocess_data()

def city_recommender(user_preferences):
    """
    Recommends cities based on user preferences.

    Args:
        user_preferences (dict): Dictionary containing user inputs.

    Returns:
        DataFrame: Top 5 recommended cities with relevant details.
    """
    recommendations = data.copy()
    recommendations['score'] = 0

    # Filter by cost of living
    recommendations = recommendations[recommendations['medianRent'] <= user_preferences['COL'] + 400]

    # Calculate scores
    recommendations['job_match'] = recommendations[f"{user_preferences['job-industry']}_percent"]

    weather = 0
    if user_preferences['climate'] in [1, 2]:
        weather = (1 - recommendations['max_avg_low']) * (6 - user_preferences['climate'])
    elif user_preferences['climate'] in [4, 5]:
        weather = recommendations['max_avg_high'] * user_preferences['climate']

    density = 0
    if user_preferences['urban'] in [1, 2]:
        density = (1 - recommendations['pop_density']) * (6 - user_preferences['urban'])
    elif user_preferences['urban'] in [4, 5]:
        density = recommendations['pop_density'] * user_preferences['urban']

    politics = 0
    if user_preferences['politics'] in [1, 2]:
        politics = recommendations['democrat'] * (6 - user_preferences['politics'])
    elif user_preferences['politics'] in [4, 5]:
        politics = recommendations['republican'] * user_preferences['politics']

    recommendations['score'] = (
        (1 - recommendations['crime_rate']) * (6 - user_preferences['crime']) +
        recommendations['parks_pp'] * user_preferences['nature'] +
        density +
        (recommendations['nonwhite_percent'] + recommendations['foreign_born_percent']) * user_preferences['diverse'] +
        recommendations['restaurants'] * user_preferences['dining'] +
        recommendations['nightlife'] * user_preferences['nightlife'] +
        recommendations['transit'] * user_preferences['airports'] +
        recommendations['car_percent'] * user_preferences['transportation'] +
        recommendations['activities'] * user_preferences['activities'] +
        politics * user_preferences['alignment'] +
        weather +
        recommendations['mean_diff'] * user_preferences['seasonal'] +
        recommendations['job_match'] * 5
    )

    return recommendations.sort_values(by='score', ascending=False).head(5)

def extract_user_preferences(source):
    """Extract user preferences from request form or query parameters."""
    return {
        'COL': int(source.get('COL', 2000)),
        'crime': int(source.get('crime', 3)),
        'nature': int(source.get('nature', 3)),
        'urban': int(source.get('urban', 3)),
        'diverse': int(source.get('diverse', 3)),
        'dining': int(source.get('dining', 3)),
        'nightlife': int(source.get('nightlife', 3)),
        'airports': int(source.get('airports', 3)),
        'transportation': int(source.get('transportation', 3)),
        'activities': int(source.get('activities', 3)),
        'politics': int(source.get('politics', 3)),
        'alignment': int(source.get('alignment', 3)),
        'climate': int(source.get('climate', 3)),
        'seasonal': int(source.get('seasonal', 3)),
        'job-industry': source.get('job-industry', 'other')
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/matches')
def matches():
    return render_template('matches.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_preferences = extract_user_preferences(request.form)
    recommendations = city_recommender(user_preferences)
    top_3_matches = recommendations.head(3).to_dict(orient='records')
    return render_template('matches.html', matches=top_3_matches)

@app.route('/map', methods=['GET'])
def map_view():
    user_preferences = extract_user_preferences(request.args)
    recommendations = city_recommender(user_preferences)
    points = recommendations.head(5).to_dict(orient='records') if not recommendations.empty else []
    return render_template('map.html', points=points)

@app.route('/data/cities.json')
def get_cities_data():
    return app.send_static_file('data/cities.json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
