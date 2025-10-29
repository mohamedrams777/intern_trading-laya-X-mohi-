// (() => {
//   const socket = io();

//   const chatBox = document.getElementById("chatBox");
//   const chatForm = document.getElementById("chatForm");
//   const chatInput = document.getElementById("chatInput");

//   function addChatMessage(username, text) {
//     const msgEl = document.createElement("div");
//     msgEl.innerHTML = `<strong>${username}:</strong> ${text}`;
//     chatBox.appendChild(msgEl);
//     chatBox.scrollTop = chatBox.scrollHeight;
//   }

//   async function loadChatHistory() {
//     try {
//       const res = await fetch("/api/chat");
//       const messages = await res.json();
//       chatBox.innerHTML = "";
//       messages.forEach(msg => addChatMessage(msg.username, msg.text));
//     } catch (err) {
//       console.error("Error loading chat history:", err);
//     }
//   }

//   chatForm.addEventListener("submit", async (e) => {
//     e.preventDefault();
//     const msg = chatInput.value.trim();
//     if (!msg) return;

//     addChatMessage("You", msg);

//     try {
//       const res = await fetch("/api/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message: msg }),
//       });
//       const data = await res.json();
//       if (data.reply) addChatMessage("Bot", data.reply);
//     } catch (err) {
//       addChatMessage("System", "Error sending message");
//       console.error(err);
//     }
//     chatInput.value = "";
//   });

//   window.addEventListener("load", loadChatHistory);
// })();

(() => {
  const socket = io(); // Connect to Socket.IO server

  // ---- DOM Elements ----
  const chatBox = document.getElementById("chatBox");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");

  // ---- Helper to add a message to chat box ----
  function addChatMessage(username, text, type = "user") {
    const msgEl = document.createElement("div");
    msgEl.className = `chat-message ${type}`;
    msgEl.innerHTML = `<strong>${username}:</strong> ${text}`;
    chatBox.appendChild(msgEl);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // ---- Load initial chat history ----
  async function loadChatHistory() {
    try {
      const res = await fetch("/api/chat"); // Expects [{username, text}]
      const messages = await res.json();
      chatBox.innerHTML = "";
      messages.slice(-100).forEach(msg => addChatMessage(msg.username, msg.text));
    } catch (err) {
      console.error("Error loading chat history:", err);
      addChatMessage("System", "Failed to load chat history", "system");
    }
  }

  // ---- Handle new chat submission ----
  chatForm.addEventListener("submit", e => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;

    // Add own message immediately
    addChatMessage("You", msg, "self");

    // Send to server
    socket.emit("community_message", { text: msg });

    chatInput.value = "";
  });

  // ---- Listen for incoming messages ----
  socket.on("community_message", payload => {
    if (payload.username && payload.text) {
      addChatMessage(payload.username, payload.text);
    }
  });

  socket.on("connect", () => {
    console.log("Connected to community chat server.");
  });

  socket.on("disconnect", () => {
    addChatMessage("System", "Disconnected from server", "system");
  });

  // ---- Initialize on page load ----
  window.addEventListener("load", loadChatHistory);
})();
