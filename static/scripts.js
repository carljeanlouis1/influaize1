document.addEventListener('DOMContentLoaded', function() {
    const authButtons = document.querySelectorAll('#auth-btn');
    authButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.location.href = '/auth';
        });
    });

    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            window.location.href = '/logout';
        });
    }

    const newPostForm = document.getElementById('new-post-form');
    if (newPostForm) {
        newPostForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const tweetContent = document.getElementById('tweet-content').value;
            const mediaInput = document.getElementById('media-input');
            const mediaFile = mediaInput.files[0];

            // TODO: Implement the logic to create a new post using the Twitter API
            // You can use the tweetContent and mediaFile variables to get the user input

            // Reset the form after submission
            newPostForm.reset();
        });
    }

    const generateTweetForm = document.getElementById('generate-tweet-form');
    if (generateTweetForm) {
        generateTweetForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData(generateTweetForm);

            fetch('/generate-tweet', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                const enhancedTweet = data.enhanced_tweet;
                document.getElementById('enhanced-tweet').textContent = enhancedTweet;
                document.getElementById('enhanced-tweet-section').style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });

        const postTweetBtn = document.getElementById('post-tweet-btn');
        postTweetBtn.addEventListener('click', function() {
            const tweetText = document.getElementById('enhanced-tweet').textContent;

            fetch('/post-tweet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tweet_text: tweetText }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert('Tweet posted successfully!');
                } else if (data.error) {
                    alert('Failed to post tweet. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        });
    }

    const tweetInput = document.getElementById('tweet-input');
    if (tweetInput) {
        tweetInput.addEventListener('input', function() {
            const tweetLength = this.value.length;
            const remainingChars = 280 - tweetLength;
            document.getElementById('remaining-chars').textContent = remainingChars;
        });
    }

    const aiImageForm = document.getElementById('ai-image-form');
    if (aiImageForm) {
        aiImageForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const tweetInput = document.getElementById('tweet-input').value;
            const imageSize = document.getElementById('image-size').value;

            fetch('/ai-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tweet_input: tweetInput, image_size: imageSize }),
            })
            .then(response => response.json())
            .then(data => {
                const imageUrl = data.image_url;
                document.getElementById('generated-image').src = imageUrl;
                document.getElementById('generated-image-section').style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });

        const downloadImageBtn = document.getElementById('download-image-btn');
        downloadImageBtn.addEventListener('click', function() {
            const imageUrl = document.getElementById('generated-image').src;
            const link = document.createElement('a');
            link.href = imageUrl;
            link.download = 'generated_image.jpg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    const chatbotInput = document.getElementById('chatbot-input');
    const chatbotSendBtn = document.getElementById('chatbot-send-btn');
    const chatbotMessages = document.getElementById('chatbot-messages');

    if (chatbotSendBtn) {
        chatbotSendBtn.addEventListener('click', function() {
            const message = chatbotInput.value;
            if (message.trim() !== '') {
                // Display user message in the chatbot messages container
                const userMessage = document.createElement('div');
                userMessage.className = 'user-message';
                userMessage.textContent = message;
                chatbotMessages.appendChild(userMessage);

                // Clear the input field
                chatbotInput.value = '';

                // Send message to the server for processing
                fetch('/chatbot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                })
                .then(response => response.json())
                .then(data => {
                    const botResponse = data.response;
                    // Display bot response in the chatbot messages container
                    const botMessage = document.createElement('div');
                    botMessage.className = 'bot-message';
                    botMessage.textContent = botResponse;
                    chatbotMessages.appendChild(botMessage);
                    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });

        // Add event listener for Enter key press in the chatbot input
        chatbotInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                chatbotSendBtn.click();
            }
        });
    }
});