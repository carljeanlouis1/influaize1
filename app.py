from flask import Flask, jsonify, request, redirect, session, render_template
from flask_cors import CORS
import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
CALLBACK_URL = os.getenv('CALLBACK_URL')

if not all([CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL]):
    raise ValueError('One or more of the required Twitter API keys are not set. Please check your .env file.')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'your-random-secret-key'

@app.route('/')
def index():
    user_data = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
    return render_template('index.html', user_data=user_data)

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
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    if not oauth_verifier or not oauth_token:
        return jsonify({'error': 'Missing OAuth verifier or token.'}), 400

    try:
        auth.request_token = {'oauth_token': oauth_token, 'oauth_token_secret': oauth_verifier}
        auth.get_access_token(oauth_verifier)
        session['access_token'] = auth.access_token
        session['access_token_secret'] = auth.access_token_secret
        return redirect('/')
    except tweepy.TweepError as e:
        print(f'An error occurred during Twitter callback: {e}')
        return jsonify({'error': 'Failed to authenticate with Twitter.'}), 500

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    session.pop('access_token_secret', None)
    return redirect('/')

@app.route('/profile')
def profile():
    user_data = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
    return render_template('profile.html', user_data=user_data)

@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    user_data = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
        if request.method == 'POST':
            tweet_content = request.form['tweet-content']
            media_file = request.files['media-input']
            # Process the tweet and media file
            api.update_status(status=tweet_content)
            return redirect('/profile')
    return render_template('new_post.html', user_data=user_data)

@app.route('/analysis')
def analysis():
    user_data = None
    engagement_rate = None
    sentiment_score = None
    topics = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
        # Perform analysis and pass data to the template
        engagement_rate = 2.5  # Example data
        sentiment_score = 0.8  # Example data
        topics = ['AI', 'Web Development', 'Data Science']  # Example data
    return render_template('analysis.html', user_data=user_data, engagement_rate=engagement_rate, sentiment_score=sentiment_score, topics=topics)

if __name__ == '__main__':
    app.run(debug=True)