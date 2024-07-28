import {
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.1.0/firebase-auth.js";
import { auth, firestore } from "./firebase.js";

export function signIn(email, password) {
  return signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      const idToken = userCredential.user.getIdToken();
      fetch("/login", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      }).then(function (response) {
        if (response.ok) {
          window.location.href = response.headers.get("Location") || "/";
        } else {
          console.error("Server responded with an error:", response.statusText);
        }
      });
    })
    .catch((error) => {
      console.error("Error signing in:", error.code, error.message);
      throw error;
    });
}

export function signOutUser() {
  return signOut(auth)
    .then(() => {
      console.log("User signed out");
    })
    .catch((error) => {
      console.error("Error signing out:", error);
      throw error;
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const frmLogin = document.getElementById("login_form");
  if (frmLogin) {
    frmLogin.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(frmLogin);
      const email = formData.get("email");
      const password = formData.get("password");
      signIn(email, password);
    });
  }
});
