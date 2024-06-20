// main.js
import { signUp, signIn, signOutUser } from './auth.js';

document.getElementById('signUpButton').addEventListener('click', () => {
  const email = document.getElementById('Email').value;
  const password = document.getElementById('Password').value;
  const status = document.getElementById('Status').value;
  const user_type = document.getElementById('User_type').value;

  signUp(email, password, { status, user_type })
    .then(() => {
      alert('User signed up and data stored in Firestore');
    })
    .catch((error) => {
      alert('Error: ' + error.message);
    });
});

document.getElementById('signInButton').addEventListener('click', () => {
  const email = document.getElementById('Email').value;
  const password = document.getElementById('Password').value;
  
  signIn(email, password)
    .then((userData) => {
      console.log(userData);
      alert('User signed in');
    })
    .catch((error) => {
      alert('Error: ' + error.message);
    });
});

document.getElementById('signOutButton').addEventListener('click', () => {
  signOutUser()
    .then(() => {
      alert('User signed out');
    })
    .catch((error) => {
      alert('Error: ' + error.message);
    });
});
