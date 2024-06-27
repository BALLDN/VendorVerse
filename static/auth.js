// auth.js
console.log('login.js is loaded');

import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/9.1.0/firebase-auth.js";
import { doc, setDoc, getDoc } from "https://www.gstatic.com/firebasejs/9.1.0/firebase-firestore.js";
import { auth, firestore } from './firebase.js'; // Assuming firebase.js is in the same directory

export const signUp = (email, password, status, user_type) => {
  return createUserWithEmailAndPassword(auth, email, password, status, user_type)
    .then((userCredential) => {
      const user = userCredential.user;
      console.log('User signed up:', user);

      return setDoc(doc(firestore, "Users", user.uid), {
        Email: user.email,
        Password: user.password,
        Status: user.status,
        User_type: user.user_type
      });
    })
    .then(() => {
      console.log('User data stored in Firestore');
    })
    .catch((error) => {
      console.error('Error signing up:', error.code, error.message);
      throw error;
    });
};

export const signIn = (email, password) => {
  return signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => {
      const user = userCredential.user;
      console.log('User signed in:', user);

      return getDoc(doc(firestore, "Users", user.uid));
    })
    .then((docSnap) => {
      if (docSnap.exists()) {
        console.log('User data:', docSnap.data());
        return docSnap.data();
      } else {
        console.log('No such document!');
        return null;
      }
    })
    .catch((error) => {
      console.error('Error signing in:', error.code, error.message);
      throw error;
    });
};

export const signOutUser = () => {
  return signOut(auth)
    .then(() => {
      console.log('User signed out');
    })
    .catch((error) => {
      console.error('Error signing out:', error);
      throw error;
    });
};
