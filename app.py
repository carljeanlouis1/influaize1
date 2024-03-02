from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS
import tweepy
import os
from dotenv import load_dotenv
from flask import render_template


# Load environment variables from .env file
load_dotenv()

# Twitter API credentials from the .env file
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
CALLBACK_URL = os.getenv('CALLBACK_URL')  # The callback URL you set in your Twitter app settings

# Debug print statements (remove these in production)
print(f'Consumer Key: {CONSUMER_KEY}')
print(f'Consumer Secret: {CONSUMER_SECRET}')
print(f'Callback URL: {CALLBACK_URL}')

# Check if the keys are loaded properly
if not all([CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL]):
    raise ValueError('One or more of the required Twitter API keys are not set. Please check your .env file.')

# Tweepy OAuth handler setup
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)

# Flask app setup
app = Flask(__name__)
CORS(app)

# Secret key for session
app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'your-random-secret-key'

# Routes
@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML file you created


@app.route('/auth')
def twitter_auth():
    try:
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token['oauth_token']
        return redirect(redirect_url)
    except tweepy.TweepError as e:
        print(f'An error occurred during Twitter auth: {e}')
        return jsonify({'error': 'Error! Failed to get request token.'}), 500

@app.route('/callback')
def twitter_callback():
    request_token = session.get('request_token')
    verifier = request.args.get('oauth_verifier')

    if not verifier or not request_token:
        return jsonify({'error': 'Missing OAuth verifier or token.'}), 400

    try:
        auth.request_token = {'oauth_token': request_token, 'oauth_token_secret': verifier}
        auth.get_access_token(verifier)
        session['access_token'] = auth.access_token
        session['access_token_secret'] = auth.access_token_secret
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
        return jsonify({'name': user_data.name, 'followers_count': user_data.followers_count})
    except tweepy.TweepError as e:
        print(f'An error occurred during Twitter callback: {e}')
        return jsonify({'error': 'Failed to authenticate with Twitter.'}), 500


@app.route('/tweets')
def get_tweets():
    access_token = session.get('access_token')
    access_token_secret = session.get('access_token_secret')

    if not all([access_token, access_token_secret]):
        return jsonify({'error': 'Authentication is required.'}), 401

    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    try:
        tweets = api.user_timeline()  # This gets the user's timeline; adjust the parameters as needed
        average_retweets = sum(tweet.retweet_count for tweet in tweets) / len(tweets)

        return jsonify({'average_retweets': average_retweets})
    except tweepy.TweepyException as e:
        print(f'An error occurred during tweets fetching: {e}')
        return jsonify({'error': 'Failed to fetch tweets.'}), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
