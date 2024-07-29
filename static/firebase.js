// firebase.js

// Import the necessary Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";
import { getFirestore, doc, setDoc, getDoc } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";

// Your web app's Firebase configuration
const firebaseConfig = "PASTE HERE";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();
const db = getFirestore(app);

// Function to register a new user
async function registerUser(email, password, user_type) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Store user details in Firestore
    await setDoc(doc(db, "Users", user.uid), {
      Email: user.email,
      Uid: user.uid,
      User_type: user_type,
      Status: "P"
    });

    console.log("User registered and data stored in Firestore");
    

    const response = await fetch('/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: user.email,
        user_type: user_type,
      })
    });

    // Ensure response is successful
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();

    // Redirect based on the URL returned by the Flask backend
    if (data.redirect_url) {
      window.location.href = data.redirect_url;
    } else {
      console.error('No redirect URL provided');
    }

  } catch (error) {
    console.error("Error registering user:", error);
  }
}

// Function to login a user
async function loginUser(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Get the Firebase ID token
    const idToken = await user.getIdToken();

    // Send ID token to the server for further processing
    const response = await fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id_token: idToken }),
    });

    if (!response.ok) {
      const errorDetails = await response.text();
      throw new Error(`Network response was not ok: ${response.statusText}. Details: ${errorDetails}`);
    }

    const data = await response.json();

    if (data.redirect_url) {
      window.location.href = data.redirect_url;
    } else if (data.error) {
      alert(`Error: ${data.error}`);
    }
  } catch (error) {
    console.error('Error logging in user:', error);
  }
}

//     // Fetch user role from Firestore
//     const userDoc = await getDoc(doc(db, "Users", user.uid));
//     if (userDoc.exists()) {
//       const userData = userDoc.data();
//       const user_type = userData.User_type;

//       console.log("User logged in with role:", user_type);

//       // Redirect based on user role
//       if (user_type === "V") {
//         window.location.href = "/vendor_home_page";
//       } else if (user_type === "E") {
//         window.location.href = "/employee_home_page";
//       } else if (user_type === "A") {
//         window.location.href = "/admin_home_page";
//       } else {
//         console.error("Unknown user role:", user_type);
//         alert("Unknown user role");
//       }
//     } else {
//       console.error("No such user in Firestore");
//       alert("User data not found");
//     }
//   } catch (error) {
//     console.error("Error logging in user:", error);
//     alert(`Error: ${error.message}`);
//   }
// }

// Wait for DOM content to be loaded
document.addEventListener('DOMContentLoaded', (event) => {
  // Register form handling
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("Email").value;
      const password = document.getElementById("Password").value;
      const user_type = document.getElementById("user_type").value;
      await registerUser(email, password, user_type);
    });
  }

  // Login form handling
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("Email").value;
      const password = document.getElementById("Password").value;
      await loginUser(email, password);
    });
  }
});