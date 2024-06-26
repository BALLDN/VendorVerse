const cookieBanner = document.getElementById('cookieBanner')

const acceptCookies = document.getElementById('acceptCookies')
const declineCookies = document.getElementById('declineCookies')

acceptCookies.addEventListener('click', acceptCookiesFunc)
declineCookies.addEventListener('click', declineCookiesFunc)

function acceptCookiesFunc(){
    cookieBanner.style.display = 'none'

    console.log(acceptCookies.value)

    //Set expiry Date
    const d = new Date();
    const exdays = 7 //Cookies expire in 7 days

    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    const expires = d.toUTCString();

    //Set cookie so banner doesnt appear again
    document.cookie = "cookieChoice=Accepted; expires=" + expires + "; path=/"
}

function declineCookiesFunc(){
    cookieBanner.style.display = 'none'

    console.log(declineCookies.value)
}