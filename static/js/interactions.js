document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = getCookie("csrftoken");

    document.querySelectorAll(".like-btn").forEach(button => {
        button.addEventListener("click", function () {
            const haikuId = this.dataset.haikuId;
            const btn = this;

            fetch(`/haiku/${haikuId}/like/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                }
            })
            .then(response => response.json())
            .then(data => {
                btn.textContent = data.liked ? "Unlike" : "Like";
                document.getElementById(`like-count-${haikuId}`).textContent = data.like_count;
            })
            .catch(error => console.error("Like toggle error:", error));
        });
    });

    document.querySelectorAll(".follow-btn").forEach(button => {
        button.addEventListener("click", function () {
            const followUser = this.dataset.profile.username;
            const btn = this;

            fetch(`/profile/${followUser}/follow/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                }
            })
            .then(response => response.json())
            .then(data => {
                btn.textContent = data.followed ? "Unfollow" : "Follow";
                document.getElementById(`like-count-${haikuId}`).textContent = data.follow_count;
            })
            .catch(error => console.error("Follow toggle error:", error));
        });
    });
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