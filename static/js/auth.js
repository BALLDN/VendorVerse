import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.1.0/firebase-auth.js";
import { auth, firestore } from "./firebase.js";

export function signUp(email, password, userType) {
  return createUserWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      const user = userCredential.user;
      const userData = {
        uid: user.uid,
        email: email,
        userType: userType,
      };

      fetch("/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(userData),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              `Error sending user data to /register: ${response.status}`
            );
          }

          return response.json();
        })

        .catch((error) => {
          console.error("Error sending user data to /register:", error);
        });
    })

    .catch((error) => {
      console.error("Error signing up:", error.code, error.message);

      throw error;
    });
}

export function signIn(email, password) {
  return signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      const user = userCredential.user;
      console.log("User signed in:", user);

      return getDoc(doc(firestore, "Users", user.uid));
    })
    .then((docSnap) => {
      if (docSnap.exists()) {
        console.log("User data:", docSnap.data());
        return docSnap.data();
      } else {
        console.log("No such document!");
        return null;
      }
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
  const frmRegister = document.getElementById("form-register");

  frmRegister.addEventListener("submit", function (event) {
    event.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const userType = document.getElementById("userType").value;

    signUp(email, password, userType);
  });
});
