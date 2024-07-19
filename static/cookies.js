var cookie_accepted = document.getElementById('cookies_accepted')
var cookie_declined = document.getElementById('decline_cookies')

var date = new Date();
var cookiesExpiry = date.setDate(date.getDate() + 14);

function acceptCookies(){

    cookie_box.style.display = 'none'

    if (cookie_accepted.value = 'Accept'){
        console.log('accepted')
    
        document.cookie = "cookie_accepted=T; expires=" + cookiesExpiry + "; path=/"
    }
}

cookie_accepted.addEventListener("click", acceptCookies)

function declineCookies(){

    cookie_box.style.display = 'none'
}

cookie_declined.addEventListener("click", declineCookies)