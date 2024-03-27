from flask import Flask, jsonify, request, redirect, session, render_template
from flask_cors import CORS
import tweepy
import os
from dotenv import load_dotenv
import openai

load_dotenv()

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
CALLBACK_URL = os.getenv('CALLBACK_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not all([CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL, OPENAI_API_KEY]):
    raise ValueError('One or more of the required API keys are not set. Please check your .env file.')

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
openai.api_key = OPENAI_API_KEY

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


@app.route('/new-post')
def new_post():
    user_data = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
    return render_template('new_post.html', user_data=user_data)


@app.route('/analysis')
def analysis():
    user_data = None
    sentiment_analysis = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
        try:
            tweets = api.user_timeline(count=100)
            tweet_texts = ' '.join([tweet.text for tweet in tweets])
            prompt = f"Perform sentiment analysis on the following tweets:\n{tweet_texts}\n\nSentiment Analysis:"
            response = openai.Completion.create(
                engine='text-davinci-002',
                prompt=prompt,
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.7
            )
            sentiment_analysis = response.choices[0].text.strip()
        except tweepy.TweepyException as e:
            print(f"Error occurred while fetching tweets: {e}")
            sentiment_analysis = "Unable to perform sentiment analysis due to limited API access."
    return render_template('analysis.html', user_data=user_data, sentiment_analysis=sentiment_analysis)


@app.route('/generate-tweet', methods=['GET', 'POST'])
def generate_tweet():
    user_data = None
    tweet_suggestions = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
        if request.method == 'POST':
            topic = request.form['topic']
            tone = request.form['tone']
            length = request.form['length']
            hashtags = request.form['hashtags']
            mentions = request.form['mentions']

            prompt = f"Generate a {length} tweet about {topic} with a {tone} tone. Include the following hashtags: {hashtags}. Mention the following users: {mentions}."
            response = openai.Completion.create(
                engine='text-davinci-002',
                prompt=prompt,
                max_tokens=100,
                n=3,
                stop=None,
                temperature=0.7
            )
            tweet_suggestions = [choice.text.strip() for choice in response.choices]
    return render_template('generate_tweet.html', user_data=user_data, tweet_suggestions=tweet_suggestions)


@app.route('/post-tweet', methods=['POST'])
def post_tweet():
    tweet_text = request.form['tweet_text']

    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)

        try:
            api.update_status(tweet_text)
            return jsonify({'message': 'Tweet posted successfully'})
        except tweepy.TweepError as e:
            print(f"Error occurred while posting tweet: {e}")
            return jsonify({'error': 'Failed to post tweet'}), 500
    else:
        return jsonify({'error': 'User not authenticated'}), 401


if __name__ == '__main__':
    app.run(debug=True)