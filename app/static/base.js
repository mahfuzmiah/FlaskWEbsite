document.addEventListener('DOMContentLoaded', function () {
    var textarea = document.getElementById('post_textarea');
    var charCountElement = document.getElementById('char_count');
    var maxLength = 500;

    if (textarea && charCountElement) {
        textarea.addEventListener('input', function () {
            var remainingChars = maxLength - textarea.value.length;
            charCountElement.textContent = remainingChars + '/' + maxLength;
        });
    }

    var allPostsBtn = document.getElementById('all-posts-btn');
    var friendsPostsBtn = document.getElementById('friends-posts-btn');

    if (allPostsBtn && friendsPostsBtn) {
        allPostsBtn.addEventListener('click', function() {
            document.getElementById('all_posts').style.display = 'block';
            document.getElementById('friends_posts').style.display = 'none';
        });

        friendsPostsBtn.addEventListener('click', function() {
            document.getElementById('all_posts').style.display = 'none';
            document.getElementById('friends_posts').style.display = 'block';
        });
    }
});


document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('toggle-replies')) {
            var button = event.target;
            var postId = button.getAttribute('data-post-id');
            var repliesContainer = document.querySelector('.replies-container[data-post-id="' + postId + '"]');

            if (repliesContainer.style.display === 'none' || repliesContainer.style.display === '') {
                $.ajax({
                    url: '/get_replies/' + postId,
                    type: 'get',
                    success: function(response) {
                        console.log('Replies loaded for post ID ' + postId + ':', response); // Additional debugging
                        repliesContainer.innerHTML = response;
                        repliesContainer.style.display = 'block';
                        button.textContent = 'Hide Replies';
                    },
                    error: function(error) {
                        console.log('Error loading replies for post ID ' + postId + ':', error); // Error handling
                    }
                });
            } else {
                repliesContainer.style.display = 'none';
                button.textContent = 'Show Replies';
            }
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('toggle-replies-friend')) {
            var button = event.target;
            var postId = button.getAttribute('data-post-id');
            var repliesContainer = document.querySelector('.friend-replies-container[data-post-id="' + postId + '"]');

            if (repliesContainer.style.display === 'none' || repliesContainer.style.display === '') {
                $.ajax({
                    url: '/get_replies/' + postId.replace('friend-', ''),
                    type: 'get',
                    success: function(response) {
                        repliesContainer.innerHTML = response;
                        repliesContainer.style.display = 'block';
                        button.textContent = 'Hide Replies';
                    },
                    error: function(error) {
                        console.log('Error loading replies for post ID ' + postId + ':', error);
                    }
                });
            } else {
                repliesContainer.style.display = 'none';
                button.textContent = 'Show Replies';
            }
        }
    });
});



$(document).ready(function() {
    $('.heart-icon').click(function() {
        var postId = $(this).data('post-id');
        if (postId) {
            $.ajax({
                url: '/like/' + postId,
                type: 'POST',
                success: function(response) {

                    // Updating the heart icon
                    var heartIcon = $('img.heart-icon[data-post-id="' + postId + '"]');
                    heartIcon.attr('src', response.is_liked ? '/static/RedHeart.png' : '/static/BlackHeart.png');

                    // Corrected selector for likesCountElement
                    var likesCountElement = heartIcon.closest('.card-footer').find('.heart-count');

                    likesCountElement.text(response.likes_count);
                },
                error: function() {
                    alert('Error liking the post.');
                }
            });
        } else {
            console.error('Post ID is undefined.');
        }
    });
});