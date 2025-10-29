(() => {
  const socket = io(); // connect to backend

  // ---- DOM Elements ----
  const symbolInput = document.getElementById("symbolInput");
  const btnLoad = document.getElementById("btnLoad");
  const lastPriceEl = document.getElementById("lastPrice");
  const currentSymbolEl = document.getElementById("currentSymbol");
  const signalEl = document.getElementById("signal");
  const bidsList = document.getElementById("bidsList");
  const asksList = document.getElementById("asksList");
  const tradesList = document.getElementById("tradesList");
  const marketData = document.getElementById("marketData");
  const newsFeed = document.getElementById("newsFeed");
  const chatBox = document.getElementById("chatBox");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const orderForm = document.getElementById("orderForm");
  const orderMsg = document.getElementById("orderMsg");
  const communityChatBtn = document.getElementById("communityChatBtn");
  const marketDataEl = document.getElementById("marketData");
  const usernameBtn = document.getElementById("usernameBtn");
  const userMenu = document.getElementById("userMenu");


  // ---- Chart Variables ----
  let priceChart = null;
  let depthChart = null;
  const priceTimeWindow = 100;

    // ----------------- Username Dropdown -----------------
  usernameBtn?.addEventListener("click", (e) => {
  e.stopPropagation();
  const dropdown = usernameBtn.closest(".user-dropdown");
  dropdown.classList.toggle("show");
});
  // Close dropdown if clicked outside
  window.addEventListener("click", (e) => {
    if (!e.target.matches("#usernameBtn")) {
      document
        .querySelectorAll(".user-dropdown")
        .forEach((drop) => drop.classList.remove("show"));
    }
  });

  // ----------------- Price Chart -----------------
  function createPriceChart(ctx) {
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Historical Price",
            data: [],
            borderColor: "rgba(75,192,192,1)",
            backgroundColor: "rgba(75,192,192,0.2)",
            pointRadius: 0,
            tension: 0.3,
          },
          {
            label: "Predicted 7 Days",
            data: [],
            borderColor: "orange",
            borderDash: [5, 5],
            fill: false,
            tension: 0.3,
          },
          {
            label: "Predicted 50 Days",
            data: [],
            borderColor: "green",
            borderDash: [5, 5],
            fill: false,
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        scales: {
          x: { type: "time", time: { unit: "day" }, title: { display: true, text: "Date" } },
          y: { beginAtZero: false, title: { display: true, text: "Price (USD)" } },
        },
        plugins: {
          legend: { position: "top" },
          zoom: {
            zoom: { wheel: { enabled: true }, pinch: { enabled: true }, drag: { enabled: true }, mode: "x" },
            pan: { enabled: true, mode: "x" },
          },
        },
      },
    });
  }

  // ----------------- Depth Chart -----------------
  function createDepthChart(ctx) {
    return new Chart(ctx, {
      type: "bar",
      data: { labels: [], datasets: [
        { label: "Bids", data: [], stack: "s1", backgroundColor: "rgba(0,128,0,0.6)" },
        { label: "Asks", data: [], stack: "s1", backgroundColor: "rgba(255,0,0,0.6)" },
      ]},
      options: { animation: false, plugins: { legend: { position: "bottom" } } },
    });
  }

    // ----------------- Market Snapshot -----------------
  async function fetchMarketSnapshot(symbol) {
    try {
      symbol = symbol.toUpperCase();
      const res = await fetch(`/api/market_snapshot/${symbol}`);
      if (!res.ok) throw new Error("Failed to fetch market snapshot");

      const data = await res.json();

      marketData.innerHTML = `
        <p>Symbol: <strong>${data.symbol}</strong></p>
        <p>Last Price: <strong>${data.last_price}</strong></p>
        <p>Open: <strong>${data.open}</strong></p>
        <p>High: <strong>${data.high}</strong></p>
        <p>Low: <strong>${data.low}</strong></p>
        <p>Volume: <strong>${data.volume}</strong></p>
        <p>Bid: <strong>${data.bid}</strong></p>
        <p>Ask: <strong>${data.ask}</strong></p>
      `;

      currentSymbolEl.textContent = data.symbol;
    } catch (err) {
      console.error("Market Snapshot error:", err);
      marketData.innerHTML = `<p class="error">Failed to load market snapshot</p>`;
    }
  }

  // ----------------- Load Symbol Data -----------------
  async function loadSymbol(sym) {
    sym = sym.toUpperCase();
    currentSymbolEl.textContent = sym;

    // ---- Historical Prices ----
    try {
      const resp = await fetch(`/api/historical/${sym}`);
      if (!resp.ok) throw new Error("Historical data fetch failed");
      const data = await resp.json();

      priceChart.data.labels = data.dates;
      priceChart.data.datasets[0].data = data.prices;
      priceChart.data.datasets[1].data = [];
      priceChart.data.datasets[2].data = [];
      priceChart.update();

      lastPriceEl.textContent = data.prices[data.prices.length - 1].toFixed(2);

      // Zoom last 30 days
      const allDates = data.dates.map(d => new Date(d));
      const lastDate = allDates[allDates.length - 1];
      const oneMonthAgo = new Date(lastDate); oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
      priceChart.options.scales.x.min = oneMonthAgo;
      priceChart.options.scales.x.max = lastDate;
      priceChart.update();
    } catch (err) { console.warn(err); }

    // ---- Order Book & Depth Chart ----
    try {
      const ob = await fetch(`/orderbook/${sym}`).then(r => r.json());
      renderOrderBook(ob);
      renderDepthChart(ob);
    } catch (err) { console.warn(err); }

    // ---- Recent Orders ----
    try {
      const all = await fetch("/orders").then(r => r.json());
      renderOrders(all.orders || []);
    } catch (err) { console.warn(err); }

    // ---- News ----
    try { await loadNews(); } catch (err) { console.warn("News fetch failed:", err); }



    // ---- Chat ----
    try { await loadChatHistory(); } catch (err) { console.warn("Chat load failed:", err); }

    // ---- Prediction ----
    try {
      const resp = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: sym }),
      });
      const pred = await resp.json();
      if (!pred.error) {
        const lastDate = new Date(priceChart.data.labels[priceChart.data.labels.length - 1]);
        let futureDates7 = [], futureDates50 = [];
        for (let i = 1; i <= 7; i++) { let d = new Date(lastDate); d.setDate(d.getDate() + i); futureDates7.push(d.toISOString().split("T")[0]); }
        for (let i = 1; i <= 50; i++) { let d = new Date(lastDate); d.setDate(d.getDate() + i); futureDates50.push(d.toISOString().split("T")[0]); }

        priceChart.data.labels = priceChart.data.labels.concat(futureDates50);
        priceChart.data.datasets[1].data = Array(priceChart.data.labels.length - futureDates7.length - 1).fill(null).concat(pred.prediction_next_7_days);
        priceChart.data.datasets[2].data = Array(priceChart.data.labels.length - futureDates50.length - 1).fill(null).concat(pred.prediction_next_50_days);
        priceChart.update();
        signalEl.textContent = pred.decision;
      }
    } catch (err) { console.warn(err); }

    
    // ---- Market Snapshot ----
    fetchMarketSnapshot(sym);
  }

  // ----------------- Load News -----------------
  async function loadNews() {
    try {
      const res = await fetch("/api/news");
      const data = await res.json();
      const newsArray = Array.isArray(data) ? data : data.news || [];
      newsFeed.innerHTML = "";
      newsArray.slice(0, 10).forEach(news => {
        const li = document.createElement("li");
        li.innerHTML = `<a href="${news.url}" target="_blank">${news.headline || news.title}</a><br><small>${news.source || ''} • ${news.datetime ? new Date(news.datetime * 1000).toLocaleDateString() : ''}</small>`;
        newsFeed.appendChild(li);
      });
    } catch (err) { console.error("Error loading news:", err); }
  }

  // ----------------- Chat -----------------
  function addChatMessage(username, text) {
    const msgEl = document.createElement("div");
    msgEl.innerHTML = `<strong>${username}:</strong> ${text}`;
    chatBox.appendChild(msgEl);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  async function loadChatHistory() {
    try {
      const res = await fetch("/api/chat");
      const messages = await res.json();
      chatBox.innerHTML = "";
      messages.slice(-50).forEach(msg => addChatMessage(msg.username, msg.text));
    } catch (err) { console.error("Error loading chat history:", err); }
  }

  communityChatBtn?.addEventListener("click", () => {
    window.location.href = "/community-chat";
});



  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    addChatMessage("You", msg);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      });
      const data = await res.json();
      if (data.reply) addChatMessage("Bot", data.reply);
      else if (data.error) addChatMessage("System", data.error);
    } catch (err) {
      addChatMessage("System", "Error sending message");
      console.error(err);
    }
    chatInput.value = "";
  });

  // ----------------- Render Helpers -----------------
  function renderOrderBook(book) {
    bidsList.innerHTML = "";
    asksList.innerHTML = "";
    (book.bids || []).forEach(b => { const li = document.createElement("li"); li.innerHTML = `<span>${b.price.toFixed(2)}</span><span>${b.quantity}</span>`; bidsList.prepend(li); });
    (book.asks || []).forEach(a => { const li = document.createElement("li"); li.innerHTML = `<span>${a.price.toFixed(2)}</span><span>${a.quantity}</span>`; asksList.appendChild(li); });
  }

  function renderDepthChart(book) {
    const bids = (book.bids || []).slice(0, 10).map(x => x.quantity);
    const asks = (book.asks || []).slice(0, 10).map(x => x.quantity);
    const labels = (book.bids || []).slice(0, 10).map(x => x.price.toFixed(2));
    depthChart.data.labels = labels;
    depthChart.data.datasets[0].data = bids;
    depthChart.data.datasets[1].data = asks;
    depthChart.update();
  }

  function renderOrders(orders) {
    tradesList.innerHTML = "";
    orders.slice(-30).reverse().forEach(o => {
      const li = document.createElement("li");
      li.innerHTML = `<div>${o.symbol} • ${o.side.toUpperCase()} ${o.quantity}</div><div>${o.price.toFixed(2)}</div>`;
      tradesList.appendChild(li);
    });
  }

  function addPricePoint(price) {
    const labels = priceChart.data.labels;
    const ds = priceChart.data.datasets[0].data;
    const t = new Date().toLocaleTimeString();
    labels.push(t); ds.push(price);
    if (labels.length > priceTimeWindow) { labels.shift(); ds.shift(); }
    priceChart.update();
  }

  // ----------------- Socket.IO Events -----------------
  socket.on("connect", () => console.log("Socket connected"));

  socket.on("price_update", payload => {
    if (payload.symbol === (symbolInput.value || "AAPL").toUpperCase()) {
      addPricePoint(payload.price);
      if (payload.signal) signalEl.textContent = payload.signal;
    }
  });

  socket.on("order_update", data => { renderOrderBook(data); renderDepthChart(data); });
  socket.on("trade_update", trade => { const li = document.createElement("li"); li.textContent = `${trade.quantity} @ ${trade.price}`; tradesList.prepend(li); });

  socket.on("news_update", payload => {
    newsFeed.innerHTML = "";
    payload.slice(0, 10).forEach(news => {
      const li = document.createElement("li");
      li.innerHTML = `<a href="${news.url}" target="_blank">${news.title}</a><br><small>${news.source || ''} • ${news.published_at || ''}</small>`;
      newsFeed.appendChild(li);
    });
  });

  // ----------------- Order Submission -----------------
  orderForm.addEventListener("submit", async e => {
    e.preventDefault();
    const symbol = symbolInput.value.trim().toUpperCase();
    const side = document.getElementById("orderSide").value;
    const quantity = document.getElementById("orderQty").value;
    if (!symbol || !quantity) return alert("Please enter a valid symbol and quantity.");

    try {
      const res = await fetch("/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, order_type: side, quantity }),
      });
      const data = await res.json();
      if (res.ok) { alert(`✅ ${data.message}`); orderMsg.textContent = data.message; renderOrderBook({ bids: [], asks: [] }); }
      else { alert(`⚠️ ${data.error || "Order failed"}`); orderMsg.textContent = data.error || "Order failed"; }
    } catch (err) { console.error(err); alert("❌ Error placing order. Check console."); }
  });

  // ----------------- Initialize -----------------
  window.addEventListener("load", () => {
    priceChart = createPriceChart(document.getElementById("priceChart").getContext("2d"));
    depthChart = createDepthChart(document.getElementById("depthChart").getContext("2d"));
    loadSymbol(symbolInput.value || "AAPL");
     setInterval(() => {
      const symbol = symbolInput.value.trim() || "AAPL";
      fetchMarketSnapshot(symbol);
    }, 5000);
  });

  btnLoad.addEventListener("click", () => loadSymbol(symbolInput.value || "AAPL"));
})();



