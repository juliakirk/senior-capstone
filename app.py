from flask import Flask, request, render_template
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import ast

app = Flask(__name__, static_folder="static")

# Load and preprocess the dataset once during app initialization
data = pd.read_csv('dataset.csv')

# Parse the 'bullets' column
data['bullets'] = data['bullets'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# Normalize the required columns
scaler = MinMaxScaler()
columns_to_normalize = [
    'crime_rate', 'parks_pp', 'pop_density', 'nonwhite_percent', 'foreign_born_percent',
    'restaurants', 'nightlife', 'transit', 'car_percent', 'activities', 'republican',
    'democrat', 'max_avg_high', 'mean_diff', 'natural-resources_percent', 'construction_percent',
    'manufacturing_percent', 'sales_percent', 'transportation_percent', 'information_percent',
    'finance_percent', 'scientific_percent', 'education_percent', 'arts_percent',
    'other_percent', 'public-administration_percent'
]
data[columns_to_normalize] = scaler.fit_transform(data[columns_to_normalize])


def get_user_preferences(form):
    """Extract user preferences from request form."""
    return {
        'COL': int(form.get('COL', 2000)),
        'crime': int(form.get('crime', 3)),
        'nature': int(form.get('nature', 3)),
        'urban': int(form.get('urban', 3)),
        'diverse': int(form.get('diverse', 3)),
        'dining': int(form.get('dining', 3)),
        'nightlife': int(form.get('nightlife', 3)),
        'airports': int(form.get('airports', 3)),
        'transportation': int(form.get('transportation', 3)),
        'activities': int(form.get('activities', 3)),
        'politics': int(form.get('politics', 3)),
        'alignment': int(form.get('alignment', 3)),
        'climate': int(form.get('climate', 3)),
        'seasonal': int(form.get('seasonal', 3)),
        'job-industry': form.get('job-industry', '')
    }


def cityReccomender(user_preferences):
    """Generate city recommendations based on user preferences."""
    global data  # Use the preloaded dataset

    # Filter and calculate scores
    filtered_data = data[data['medianRent'] <= user_preferences['COL'] + 400]
    filtered_data['job_match'] = filtered_data[f"{user_preferences['job-industry']}_percent"]

    weather = 0
    if user_preferences['climate'] in [1, 2]:
        weather = (1 - filtered_data['max_avg_low']) * (6 - user_preferences['climate'])
    elif user_preferences['climate'] in [4, 5]:
        weather = filtered_data['max_avg_high'] * user_preferences['climate']

    density = 0
    if user_preferences['urban'] in [1, 2]:
        density = (1 - filtered_data['pop_density']) * (6 - user_preferences['urban'])
    elif user_preferences['urban'] in [4, 5]:
        density = filtered_data['pop_density'] * user_preferences['urban']

    politics = 0
    if user_preferences['politics'] in [1, 2]:
        politics = filtered_data['democrat'] * (6 - user_preferences['politics'])
    elif user_preferences['politics'] in [4, 5]:
        politics = filtered_data['republican'] * user_preferences['politics']

    filtered_data['score'] = (
        (1 - filtered_data['crime_rate']) * (6 - user_preferences['crime']) +
        filtered_data['parks_pp'] * user_preferences['nature'] +
        density +
        (filtered_data['nonwhite_percent'] + filtered_data['foreign_born_percent']) * user_preferences['diverse'] +
        filtered_data['restaurants'] * user_preferences['dining'] +
        filtered_data['nightlife'] * user_preferences['nightlife'] +
        filtered_data['transit'] * user_preferences['airports'] +
        filtered_data['car_percent'] * user_preferences['transportation'] +
        filtered_data['activities'] * user_preferences['activities'] +
        politics * user_preferences['alignment'] +
        weather +
        filtered_data['mean_diff'] * user_preferences['seasonal'] +
        filtered_data['job_match'] * 5
    )

    # Return the sorted recommendations
    return filtered_data.sort_values(by='score', ascending=False)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/survey')
def survey():
    return render_template('survey.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    user_preferences = get_user_preferences(request.form)
    recommendations = cityReccomender(user_preferences).head(3).to_dict(orient='records')
    return render_template('matches.html', matches=recommendations)


@app.route('/map')
def map_view():
    user_preferences = get_user_preferences(request.args)
    recommendations = cityReccomender(user_preferences).head(5).to_dict(orient='records')
    return render_template('map.html', locations=recommendations)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
