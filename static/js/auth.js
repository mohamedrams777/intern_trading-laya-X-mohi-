document.addEventListener("DOMContentLoaded", () => {

  // ---------- LOGIN ----------
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("loginUsername").value.trim();
      const password = document.getElementById("loginPassword").value.trim();
      const msg = document.getElementById("loginMsg");

      try {
        const res = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });

        const data = await res.json();
        msg.textContent = data.message;
        msg.style.color = res.ok ? "green" : "red";

        if (res.ok) {
          // redirect to homepage or dashboard
          setTimeout(() => window.location.href = "/", 1000);
        }
      } catch (err) {
        msg.textContent = "Login failed. Please try again.";
        msg.style.color = "red";
      }
    });
  }

  // ---------- SIGNUP ----------
  const signupForm = document.getElementById("signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const username = document.getElementById("signupName").value.trim();
      const email = document.getElementById("signupEmail").value.trim();
      const password = document.getElementById("signupPassword").value.trim();
      const confirm_password = document.getElementById("signupConfirmPassword").value.trim();
      const msg = document.getElementById("signupMsg");

      try {
        const res = await fetch("/api/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password, confirm_password }),
        });

        const data = await res.json();
        msg.textContent = data.message;
        msg.style.color = res.ok ? "green" : "red";

        if (res.ok) {
          // Redirect to login after successful signup
          setTimeout(() => window.location.href = "/login", 1500);
        }
      } catch (err) {
        msg.textContent = "Signup failed. Please try again.";
        msg.style.color = "red";
      }
    });
  }
});



// (() => {
//   const loginForm = document.getElementById("loginForm");
//   const signupForm = document.getElementById("signupForm");

//   if (loginForm) {
//     loginForm.addEventListener("submit", async (e) => {
//       e.preventDefault();
//       const email = document.getElementById("loginEmail").value;
//       const password = document.getElementById("loginPassword").value;
//       const msg = document.getElementById("loginMsg");

//       try {
//         const resp = await fetch("/api/login", {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ email, password }),
//         });
//         const data = await resp.json();
//         if (data.success) {
//           msg.textContent = "Login successful! Redirecting...";
//           setTimeout(() => (window.location.href = "/"), 1000);
//         } else msg.textContent = data.message;
//       } catch (err) {
//         msg.textContent = "Login failed!";
//       }
//     });
//   }

//   if (signupForm) {
//     signupForm.addEventListener("submit", async (e) => {
//       e.preventDefault();
//       const name = document.getElementById("signupName").value;
//       const email = document.getElementById("signupEmail").value;
//       const password = document.getElementById("signupPassword").value;
//       const msg = document.getElementById("signupMsg");

//       try {
//         const resp = await fetch("/api/signup", {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ name, email, password }),
//         });
//         const data = await resp.json();
//         if (data.success) {
//           msg.textContent = "Signup successful! Redirecting to login...";
//           setTimeout(() => (window.location.href = "/login"), 1000);
//         } else msg.textContent = data.message;
//       } catch (err) {
//         msg.textContent = "Signup failed!";
//       }
//     });
//   }
// })();
