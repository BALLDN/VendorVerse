// firebase.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.1.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/9.1.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/9.1.0/firebase-firestore.js";

// Your Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyAopZbRsbPXV-t9Ba8QFF6vc4xCiIGUjAo",
    authDomain: "balldn.firebaseapp.com",
    projectId: "balldn",
    storageBucket: "balldn.appspot.com",
    messagingSenderId: "267440458442",
    appId: "1:267440458442:web:d11d19d9b17d2becfec233",
    measurementId: "G-59X368RBXR"
  };

  const app = initializeApp(firebaseConfig);
  export const auth = getAuth(app);
  export const firestore = getFirestore(app);
