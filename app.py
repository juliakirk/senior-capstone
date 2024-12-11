#!/usr/bin/env node

from flask import Flask, request, render_template, jsonify
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import ast

# Ensure the bullets column is parsed correctly


def cityReccomender(user_preferences):
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler

    data = pd.read_csv('dataset.csv')

    scaler = MinMaxScaler()
    columns_to_normalize = [ 'crime_rate', 'parks_pp', 'pop_density', 
        'nonwhite_percent', 'foreign_born_percent', 'restaurants', 
        'nightlife', 'transit', 'car_percent', 'activities', 
        'republican', 'democrat', 'max_avg_high', 'mean_diff',
        'natural-resources_percent', 'construction_percent', 'manufacturing_percent', 
        'sales_percent', 'transportation_percent', 'information_percent', 
        'finance_percent', 'scientific_percent', 'education_percent', 
        'arts_percent', 'other_percent', 'public-administration_percent'
    ]
    data[columns_to_normalize] = scaler.fit_transform(data[columns_to_normalize])
    data['bullets'] = data['bullets'].apply(lambda x: x.replace('\xa0', ' ') if isinstance(x, str) else x)

# Convert the string representation of lists into actual Python lists
    data['bullets'] = data['bullets'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    data['score'] = 0

    data['job_match'] = data[f"{user_preferences['job-industry']}_percent"]

    data = data[data['medianRent'] <= user_preferences['COL'] + 400]

    weather = 0
    if user_preferences['climate'] in [1, 2]:
        weather = (1 - data['max_avg_low']) * (6 - user_preferences['climate'])
    elif user_preferences['climate'] in [4, 5]:
        weather = data['max_avg_high'] * user_preferences['climate']

    density = 0
    if user_preferences['urban'] in [1, 2]:
        density = (1 - data['pop_density']) * (6 - user_preferences['urban'])  # Prefer lower density
    elif user_preferences['urban'] in [4, 5]:
        density = data['pop_density'] * user_preferences['urban']  # Prefer higher density

    politics = 0
    if user_preferences['politics'] in [1, 2]:
        politics = data['democrat'] * (6 - user_preferences['politics'])  # Prefer lower density
    elif user_preferences['politics'] in [4, 5]:
        politics = data['republican'] * user_preferences['politics']  # Prefer higher density

    data['score'] = (
        (1 - data['crime_rate']) * (6 - user_preferences['crime']) +  # Lower crime rate preferred
        data['parks_pp'] * user_preferences['nature'] +        # Nature preference
        density +                                              # Urban/rural preference
        (data['nonwhite_percent'] + data['foreign_born_percent']) * user_preferences['diverse'] +
        data['restaurants'] * user_preferences['dining'] +
        data['nightlife'] * user_preferences['nightlife'] +
        data['transit'] * user_preferences['airports'] +
        data['car_percent'] * user_preferences['transportation'] +
        data['activities'] * user_preferences['activities'] +
        politics * user_preferences['alignment'] +
        weather +
        data['mean_diff'] * user_preferences['seasonal'] +
        data['job_match'] * 5  # Job match is always maximally weighted
    )

    recommendations = data.sort_values(by='score', ascending=False).head(5)
    # Output recommendations
    return recommendations[['City_State', 'score', 'Latitude', 'Longitude', 'blurb', 'image', 'bullets']]

app = Flask(__name__, static_folder="static")


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

@app.route('/map')
def map_view():
    return render_template('map.html')


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

@app.route('/recommend', methods=['POST'])
def recommend():
    # Extract preferences from POST form data
    user_preferences = extract_user_preferences(request.form)

    # Get recommendations
    recommendations = cityReccomender(user_preferences)

    # Select top 3 matches for the matches page
    top_3_matches = recommendations.head(3).to_dict(orient='records')

    return render_template('matches.html', matches=top_3_matches)

@app.route('/data/cities.json')
def get_cities_data():
    # Provide the correct path to your JSON file
    return app.send_static_file('data/cities.json')


@app.route('/map', methods=['GET'])
def map_view():
    # Extract user preferences or provide defaults
    user_preferences = extract_user_preferences(request.form)

    # Generate recommendations
    recommendations = cityReccomender(user_preferences)

    # Convert recommendations to JSON-serializable format
    if not recommendations.empty:
        points = recommendations.head(5).to_dict(orient='records')
    else:
        # Provide fallback if no recommendations exist
        points = [{"City_State": "No Matches Found", "Latitude": 0, "Longitude": 0, "blurb": "No data available"}]

    # Debugging step: Print points to check the structure
    print("Points passed to the template:", points)

    return render_template('map.html', points=points)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)