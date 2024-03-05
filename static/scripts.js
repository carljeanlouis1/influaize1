document.getElementById('auth-btn').addEventListener('click', function() {
    window.location.href = '/auth';
});

document.getElementById('logout-btn').addEventListener('click', function() {
    window.location.href = '/logout';
});

document.getElementById('new-post-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const tweetContent = document.getElementById('tweet-content').value;
    const mediaFile = document.getElementById('media-input').files[0];

    const formData = new FormData();
    formData.append('tweet-content', tweetContent);
    formData.append('media-input', mediaFile);

    fetch('/new-post', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        window.location.href = '/profile';
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// Character count for tweet content
const tweetContent = document.getElementById('tweet-content');
const charCount = document.getElementById('char-count');

tweetContent.addEventListener('input', function() {
    const remainingChars = 280 - tweetContent.value.length;
    charCount.textContent = remainingChars;
});