document.addEventListener("DOMContentLoaded", async () => {
  const holdingsTableBody = document.getElementById("holdingsTableBody");
  const totalBalanceEl = document.getElementById("totalBalance");
  const investedAmountEl = document.getElementById("investedAmount");
  const unrealizedProfitEl = document.getElementById("unrealizedProfit");

  try {
    // Fetch portfolio data from backend
    const res = await fetch("/api/portfolio");
    const data = await res.json();

    // Render table
    holdingsTableBody.innerHTML = "";
    data.holdings.forEach(stock => {
      const tr = document.createElement("tr");
      const pnlClass = stock.pnl >= 0 ? "profit" : "loss";
      tr.innerHTML = `
        <td>${stock.symbol}</td>
        <td>${stock.quantity}</td>
        <td>${stock.avg_price.toFixed(2)}</td>
        <td>${stock.market_value.toFixed(2)}</td>
        <td class="${pnlClass}">${stock.pnl >= 0 ? '+' : ''}${stock.pnl.toFixed(2)}</td>
      `;
      holdingsTableBody.appendChild(tr);
    });

    // Summary cards
    totalBalanceEl.textContent = `$${data.total_balance.toFixed(2)}`;
    investedAmountEl.textContent = `$${data.invested_amount.toFixed(2)}`;
    unrealizedProfitEl.textContent = `${data.unrealized_profit >= 0 ? '+' : ''}$${data.unrealized_profit.toFixed(2)}`;
    unrealizedProfitEl.className = data.unrealized_profit >= 0 ? "profit" : "loss";

    // Portfolio chart
    const ctx = document.getElementById("portfolioChart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.performance.dates,
        datasets: [{
          label: "Portfolio Value",
          data: data.performance.values,
          borderColor: "rgba(0,194,168,1)",
          backgroundColor: "rgba(0,194,168,0.2)",
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } },
        scales: {
          y: { beginAtZero: false, title: { display: true, text: "Value ($)" } },
          x: { title: { display: true, text: "Date" } }
        }
      }
    });
  } catch (err) {
    console.error("Error loading portfolio:", err);
    holdingsTableBody.innerHTML = `<tr><td colspan="5">Failed to load portfolio data</td></tr>`;
  }
});
