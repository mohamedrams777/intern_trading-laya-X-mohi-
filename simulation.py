import random
import math
import numpy as np

def monte_carlo_gbm(initial_price: float, n_simulations: int = 500, days: int = 30,
                    mu: float = 0.0005, sigma: float = 0.01):
    sims = []
    dt = 1.0
    drift = (mu - 0.5 * sigma * sigma) * dt
    for _ in range(n_simulations):
        path = [initial_price]
        for _ in range(days):
            z = random.gauss(0, 1)
            shock = sigma * math.sqrt(dt) * z
            next_price = path[-1] * math.exp(drift + shock)
            path.append(next_price)
        sims.append(path)
    return sims

def summarize_final_prices(paths):
    finals = np.array([p[-1] for p in paths])
    return {
        "mean_final_price": float(np.mean(finals)),
        "median_final_price": float(np.median(finals)),
        "5pct": float(np.percentile(finals, 5)),
        "95pct": float(np.percentile(finals, 95)),
    }
