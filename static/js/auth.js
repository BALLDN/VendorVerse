import {
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.1.0/firebase-auth.js";
import { auth, firestore } from "./firebase.js";

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
