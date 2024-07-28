function acceptCookies(e) {
  e.preventDefault();
  const cookieBox = document.getElementById("cookie_box");
  let date = new Date();
  let cookiesExpiry = date.setDate(date.getDate() + 14);
  document.cookie = "cookie_accepted=T; expires=" + cookiesExpiry + "; path=/";
  cookieBox.remove();
}

function declineCookies(e) {
  e.preventDefault();
  const cookieBox = document.getElementById("cookie_box");
  cookieBox.remove();
}

document.addEventListener("DOMContentLoaded", function () {
  const cookie_accepted = document.getElementById("cookies_accept");
  const cookie_declined = document.getElementById("cookies_decline");
  cookie_accepted.addEventListener("click", acceptCookies);
  cookie_declined.addEventListener("click", declineCookies);
});
