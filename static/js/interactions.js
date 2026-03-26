document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = getCookie("csrftoken");

    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function () {
            const haikuId = this.dataset.haikuId;
            const btn = this;
            const likeIcon = this.getElementsByTagName('i')[0]

            fetch(`/haiku/${haikuId}/like/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Request failed");
                }
                return response.json();
            })
            .then(data => {
                document.getElementById(`like-count-${haikuId}`).textContent = data.like_count;
                
                if (data.liked) {
                    likeIcon.classList.remove("fa-regular");
                    likeIcon.classList.add("fa-solid");
                }else{
                    likeIcon.classList.remove("fa-solid");
                    likeIcon.classList.add("fa-regular");
                }
                
            })
            .catch(error => console.error("Like toggle error:", error));
        });
    });

    document.querySelectorAll(".follow-btn").forEach(button => {
        button.addEventListener("click", function () {
            const followUser = this.dataset.profileUsername;
            const btn = this;

            fetch(`/profile/${followUser}/follow/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                }
            })
            .then(response => response.json())
            .then(data => {
                btn.textContent = data.is_following ? "Unfollow" : "Follow";
                document.getElementById("follower-count").textContent = data.follower_count;
                document.getElementById("follower-label").textContent =
                    data.follower_count === 1 ? "Follower" : "Followers";
            })
            .catch(error => console.error("Follow toggle error:", error));
        });
    });
        const commentForm = document.getElementById("comment-form");

    if (commentForm) {
        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const commentInput = document.getElementById("comment-input");
            const commentSubmit = document.getElementById("comment-submit");
            const commentsList = document.getElementById("comments-list");
            const noCommentsMessage = document.getElementById("no-comments-message");
            const commentText = commentInput.value.trim();

            if (!commentText) return;

            commentSubmit.disabled = true;
            commentSubmit.textContent = "Posting...";

            fetch(commentForm.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    comment_text: commentText
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (noCommentsMessage) {
                        noCommentsMessage.remove();
                    }

                    const newComment = document.createElement("div");
                    newComment.classList.add("comment-card", "fade-in");

                    newComment.innerHTML = `
                        <div class="usernameCont">
                            ${data.profile_picture ? `<img class="profileImg" src="${data.profile_picture}" alt="${data.username} profile picture">` : ""}
                            <strong>${data.username}</strong>
                        </div>
                        <p>${data.comment_text}</p>
                        <small>${data.created_at}</small>
                    `;

                    commentsList.prepend(newComment);

                    commentInput.value = "";

                    const commentCountArea = document.getElementById("comment-count");
                    if (commentCountArea) {
                        commentCountArea.innerHTML = `<i class="fa-regular fa-comment"></i>${data.comment_count}`;
                    }
                }
            })
            .catch(error => console.error("Comment AJAX error:", error))
            .finally(() => {
                commentSubmit.disabled = false;
                commentSubmit.textContent = "Post Comment";
            });
        });
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}