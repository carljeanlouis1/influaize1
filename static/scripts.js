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
            const topic = document.getElementById('topic').value;
            const tone = document.getElementById('tone').value;
            const length = document.getElementById('length').value;
            const hashtags = document.getElementById('hashtags').value;
            const mentions = document.getElementById('mentions').value;

            // Send the form data to the server
            fetch('/generate-tweet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    topic: topic,
                    tone: tone,
                    length: length,
                    hashtags: hashtags,
                    mentions: mentions,
                }),
            })
            .then(response => response.text())
            .then(data => {
                // Update the page with the generated tweet suggestions
                const tweetSuggestionsContainer = document.getElementById('tweet-suggestions');
                tweetSuggestionsContainer.innerHTML = data;

                // Attach event listeners to the "Post Tweet" buttons
                const postTweetButtons = document.querySelectorAll('.post-tweet-btn');
                postTweetButtons.forEach(function(button) {
                    button.addEventListener('click', function() {
                        const tweetText = this.getAttribute('data-tweet');

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
                });
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});