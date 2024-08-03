import {
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.1.0/firebase-auth.js";
import { auth } from "./firebase.js";

export function signIn(email, password) {
  const btnSubmit = document.querySelector("button[type='submit']");
  signInWithEmailAndPassword(auth, email, password)
    .then(function (userCreds) {
      btnSubmit.innerHTML = `
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      `;
      fetch("/auth/login", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${userCreds.user.accessToken}`,
        },
      }).then(function (response) {
        auth_redirect(response);
      });
    })
    .catch(function (error) {
      btnSubmit.innerHTML = `
      <h4 class="m-0">Login</h4>
      `;
      if (error.code == "auth/invalid-login-credentials") {
        const email = document.getElementById("email");
        const password = document.getElementById("password");

        [email, password].forEach((input) => {
          input.classList.toggle("is-invalid");
          setTimeout(() => {
            input.classList.toggle("is-invalid");
          }, 1000);
        });
      }
      console.error("Error signing in:", error.code, error.message);
    });
}

function auth_redirect(response) {
  if (response.ok) {
    if (response.redirected) {
      window.location.assign(response.url);
    } else {
      window.location.assign("/");
    }
  } else {
    throw Exception(response.statusText);
  }
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

  const show_password = document.querySelector("#show_password");
  const password_fields = document.querySelectorAll("input.password-toggle");
  if (show_password) {
    show_password.addEventListener("change", () => {
      password_fields.forEach((field) => {
        const type =
          field.getAttribute("type") === "password" ? "text" : "password";
        field.setAttribute("type", type);
      });
    });
  }
});
