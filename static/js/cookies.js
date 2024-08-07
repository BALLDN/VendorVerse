function acceptCookies(e) {
  e.preventDefault();
  const cookieConsent = document.getElementById("cookie_consent");
  let date = new Date();
  date.setDate(date.getDate() + 14);
  let cookiesExpiry = date.toUTCString();
  document.cookie = `cookie_accepted=T; 
  expires=${cookiesExpiry};
  path=/; 
  SameSite = None;
  Secure`;
  cookieConsent.remove();
}

function declineCookies(e) {
  e.preventDefault();
  const cookieConsent = document.getElementById("cookie_consent");
  cookieConsent.remove();
}

function getCookie(name) {
  let cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    let [key, value] = cookie.split("=");
    key = key.trim();
    if (key === name) {
      return value;
    }
  }
  return null;
}

document.addEventListener("DOMContentLoaded", function () {
  const cookieConsent = document.getElementById("cookie_consent");

  if (getCookie("cookie_accepted") === "T") {
    cookieConsent.remove();
  } else {
    const cookie_accepted = document.getElementById("cookies_accept");
    const cookie_declined = document.getElementById("cookies_decline");

    cookie_accepted.addEventListener("click", acceptCookies);
    cookie_declined.addEventListener("click", declineCookies);
  }
});
