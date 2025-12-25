# ==============================
# STEP 1: DATA DOWNLOAD & RETURNS
# ==============================

import yfinance as yf
import pandas as pd
import numpy as np

# Asset selection
TICKER = "SPY"
START_DATE = "2018-01-01"
END_DATE = "2024-01-01"

# Download auto-adjusted prices
prices = yf.download(
    TICKER,
    start=START_DATE,
    end=END_DATE,
    auto_adjust=True
)

# Keep close prices
prices = prices[['Close']]
prices.dropna(inplace=True)

# Calculate daily returns
returns = prices['Close'].pct_change(fill_method=None).dropna()

# Scale returns (important for GARCH stability)
returns = returns * 100

# Save data
prices.to_csv("prices.csv")
returns.to_csv("returns.csv", header=["Return"])

print("STEP 1 COMPLETE: Data & returns prepared")
print(returns.describe())
# ==============================
# STEP 2: FIT GARCH(1,1) MODEL
# ==============================

from arch import arch_model

# Load returns
returns = pd.read_csv("returns.csv")
returns['Return'] = pd.to_numeric(returns['Return'], errors='coerce')
returns.dropna(inplace=True)

# Fit GARCH(1,1) model
garch = arch_model(
    returns['Return'],
    mean='Zero',
    vol='GARCH',
    p=1,
    q=1,
    dist='normal'
)

garch_result = garch.fit(disp='off')

print("\nSTEP 2 COMPLETE: GARCH(1,1) fitted")
print(garch_result.summary())
# ==============================
# STEP 3: PLOT CONDITIONAL VOLATILITY
# ==============================

import matplotlib.pyplot as plt

# Extract conditional volatility
cond_vol = garch_result.conditional_volatility

# Create time index
dates = returns.index[-len(cond_vol):]

plt.figure(figsize=(12, 6))
plt.plot(dates, cond_vol, color='black', linewidth=1)

plt.title("GARCH(1,1) Conditional Volatility (SPY)")
plt.xlabel("Time")
plt.ylabel("Volatility (%)")
plt.grid(alpha=0.3)

# Save figure for GitHub
plt.tight_layout()
plt.savefig("garch_conditional_volatility.png", dpi=300)
plt.show()

print("\nSTEP 3 COMPLETE: Conditional volatility plotted and saved")
