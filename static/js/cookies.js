function acceptCookies(e) {
  e.preventDefault();
  const cookieConsent = document.getElementById("cookie_consent");
  let date = new Date();
  let cookiesExpiry = date.setDate(date.getDate() + 14);
  document.cookie = "cookie_accepted=T; expires=" + cookiesExpiry + "; path=/";
  cookieConsent.remove();
}

function declineCookies(e) {
  e.preventDefault();
  const cookieConsent = document.getElementById("cookie_consent");
  cookieConsent.remove();
}

document.addEventListener("DOMContentLoaded", function () {
  const cookie_accepted = document.getElementById("cookies_accept");
  const cookie_declined = document.getElementById("cookies_decline");
  cookie_accepted.addEventListener("click", acceptCookies);
  cookie_declined.addEventListener("click", declineCookies);
});
