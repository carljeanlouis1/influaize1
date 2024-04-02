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
            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant that performs sentiment analysis on tweets.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.7
            )
            sentiment_analysis = response['choices'][0]['message']['content'].strip()
        except tweepy.TweepyException as e:
            print(f"Error occurred while fetching tweets: {e}")
            sentiment_analysis = "Unable to perform sentiment analysis due to limited API access."
    return render_template('analysis.html', user_data=user_data, sentiment_analysis=sentiment_analysis)

@app.route('/generate-tweet', methods=['GET', 'POST'])
def generate_tweet():
    user_data = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
        if request.method == 'POST':
            tweet_input = request.form['tweet_input']
            tone = request.form['tone']
            hashtags = request.form['hashtags']
            mentions = request.form['mentions']
            include_emoji = 'emoji' in request.form

            prompt = f"Enhance the following tweet with a {tone} tone, include hashtags ({hashtags}) and mentions ({mentions}):\n\n{tweet_input}\n\nEnhanced tweet:"
            if include_emoji:
                prompt += " Include relevant emojis in the enhanced tweet."

            response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant that enhances tweets.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=280,
                n=1,
                stop=None,
                temperature=0.7
            )
            enhanced_tweet = response['choices'][0]['message']['content'].strip()

            return jsonify({'enhanced_tweet': enhanced_tweet})

    return render_template('generate_tweet.html', user_data=user_data)

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

@app.route('/ai-image', methods=['GET', 'POST'])
def ai_image():
    user_data = None
    if 'access_token' in session:
        auth.set_access_token(session['access_token'], session['access_token_secret'])
        api = tweepy.API(auth)
        user_data = api.verify_credentials()
        if request.method == 'POST':
            tweet_input = request.json['tweet_input']
            image_size = request.json['image_size']

            # Generate AI image based on tweet using DALL-E 3 API
            image_url = generate_ai_image(tweet_input, image_size)

            return jsonify({'image_url': image_url})

    return render_template('ai_image.html', user_data=user_data)

def generate_ai_image(tweet, image_size):
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=tweet,
            n=1,
            size=image_size,
        )
        image_url = response['data'][0]['url']
        return image_url
    except openai.error.OpenAIError as e:
        print(f"Error occurred while generating AI image: {e}")
        return None

@app.route('/chatbot', methods=['POST'])
def chatbot():
    message = request.json['message']

    # Generate chatbot response using OpenAI Chat Completion API
    response = generate_chatbot_response(message)

    return jsonify({'response': response})

def generate_chatbot_response(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": message}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        chatbot_response = response.choices[0].message['content'].strip()
        return chatbot_response
    except openai.error.OpenAIError as e:
        print(f"Error occurred while generating chatbot response: {e}")
        return "Sorry, I couldn't generate a response. Please try again."

if __name__ == '__main__':
    app.run(debug=True)