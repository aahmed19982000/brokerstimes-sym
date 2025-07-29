function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='));
  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}

function toggleNotifications() {
  const dropdown = document.getElementById("notificationDropdown");
  if (dropdown) {
    dropdown.classList.toggle("show");
  }
}

function markAsRead(id) {
  fetch(`/notifications/${id}/read/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  }).then(response => response.json())
    .then(data => {
      if (data.success) {
        const el = document.getElementById(`note-${id}`);
        if (el) {
          el.classList.remove("unread");
          const btn = el.querySelector('button[onclick^="markAsRead"]');
          if (btn) btn.remove();
        }
      }
    });
}

function deleteNotification(id) {
  fetch(`/notifications/${id}/delete/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({})
  }).then(response => response.json())
    .then(data => {
      if (data.success) {
        const el = document.getElementById(`note-${id}`);
        if (el) el.remove();
      }
    });
}

// إغلاق القائمة عند الضغط خارجها
document.addEventListener("click", function(event) {
  const dropdown = document.getElementById("notificationDropdown");
  const icon = document.querySelector(".notification-icon");

  if (dropdown && !dropdown.contains(event.target) && !icon.contains(event.target)) {
    dropdown.classList.remove("show");
  }
});
