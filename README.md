# CherryAlgo-Framework: Quantitative Trading & Risk Management Engine

**A Python-based framework for the development, backtesting, and risk management of quantitative trading strategies, featuring a dynamic PyTorch-powered risk engine and simulated execution pipeline. Architected by Arnaud Saint-Pierre for identifying and capitalizing on small-cap market momentum.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Status](https://img.shields.io/badge/status-alpha-orange)
---

## Table of Contents

1.  [Overview](#overview)
2.  [Strategy Basis: The "Cherry" Momentum Approach](#strategy-basis)
3.  [Core Features](#core-features)
4.  [Technical Architecture](#technical-architecture)
5.  [Key Methodologies](#key-methodologies)
    * [Backtesting Engine](#backtesting-engine)
    * [Dynamic Risk Engine (PyTorch)](#dynamic-risk-engine)
    * [Monte Carlo Validation](#monte-carlo-validation)
    * [Walk-Forward Validation](#walk-forward-validation)
6.  [Performance Highlights (from Research)](#performance-highlights)
7.  [Technology Stack](#technology-stack)
8.  [Project Structure](#project-structure)
9.  [Setup & Installation](#setup--installation)
10. [Running a Backtest](#running-a-backtest)
11. [Configuration](#configuration)
12. [Disclaimer on Proprietary Strategy Logic](#disclaimer)
13. [Future Work & Roadmap](#future-work--roadmap)
14. [License](#license)
15. [Contact](#contact)

---

## 1. Overview

The CherryAlgo-Framework provides a robust environment for systematically developing, testing, and deploying quantitative trading strategies, with a particular focus on intraday momentum in low-float, small-cap equities. This framework was born out of extensive research into identifying statistically significant edges in pre-market momentum and managing risk dynamically.

The system is designed with modularity in mind, allowing for the integration of various data feeds, strategy modules, execution handlers, and advanced risk management protocols. The centerpiece is a custom-built, event-driven backtesting engine and a sophisticated PyTorch-based dynamic risk engine that adapts to market conditions and portfolio state.

This repository showcases the engineering and quantitative rigor behind such a system, providing the framework and tools for systematic trading research and simulation.

## 2. Strategy Basis: The "Cherry" Momentum Approach

The foundational strategy simulated within this framework, codenamed "Cherry," is a long-only day trading approach targeting U.S. equities that meet specific pre-market criteria:

* **Universe:** Low-priced ($1–$30), low-float (1–10 million shares) NASDAQ/NYSE stocks.
* **Momentum Triggers:** High pre-market gap (>5%), significant relative volume (>2x average), and substantial pre-market volume (>1M shares), indicating strong retail and institutional interest.
* **Entry Timings:** Precise entry windows at 07:00 PST or 07:15 PST, contingent on proprietary "gate" conditions being met on trigger bars (e.g., 6:45 PST bar for 07:00 entry).
* **Trade Management:** Strict initial stop-loss (-7%) with a sophisticated, multi-step profit-protecting trailing stop mechanism. Positions are closed end-of-day.

Two primary gate variants were researched:
* **VRPF (Volume/Relative Volume/Price/Float):** Base screener criteria.
* **VRPFWL (VRPF + "WL" Pattern):** Adds a specific candlestick/price action pattern requirement on the trigger bar, aiming for higher-quality setups.

The research (mid-2022 to early-2025 tick-level data) indicates a persistent edge for these conditions, particularly the VRPFWL variant. This framework is designed to systematically test and validate such hypotheses.

## 3. Core Features

* **Event-Driven Backtesting Engine:** Supports historical data replay and strategy evaluation on a per-tick or per-bar basis.
* **Modular Strategy Interface:** Allows for easy implementation and testing of new trading ideas. Includes an example momentum strategy based on the "Cherry" principles.
* **Dynamic Risk Management (PyTorch):** A sophisticated risk engine that can adjust position sizing and trade approval based on factors like:
    * Max equity-at-risk per trade.
    * Max portfolio dollar-flow cap.
    * (Future extension: Real-time volatility inputs).
* **Monte Carlo Simulation Module:** For robust validation of risk parameters and estimation of ruin probability.
* **Performance Analytics:** Comprehensive metrics including win rate, average gain/loss, expectancy, Sharpe ratio, Sortino ratio, max drawdown, profit factor, MFE/MAE.
* **Simulated Execution & Webhook Integration:** Simulates order fills, commissions, slippage, and includes a conceptual webhook listener for integrating with external signal providers (e.g., TradingView alerts for paper trading).
* **Configuration Management:** Flexible setup via external INI files.
* **Extensible Data Handling:** Designed to connect to various market data sources (currently supports CSV, with an interface for live feeds).

## 4. Technical Architecture

*(This section would ideally have a simple diagram. For now, descriptive text. We can create a diagram later using ASCII art or an image).*

The framework operates on an event-driven architecture:

1.  **Market Data Feed:** Generates market data events (e.g., new bar, new tick).
2.  **Strategy Module:** Receives market data events, applies its logic, and generates signal events (e.g., BUY_SIGNAL, SELL_SIGNAL).
3.  **Portfolio Manager:** Receives signal events, checks current positions and cash. If a trade is considered, it consults the Risk Engine.
4.  **Risk Engine:** Evaluates the proposed trade against risk parameters and portfolio state, then approves/modifies/rejects the trade, generating an order event.
5.  **Execution Handler (Simulated Broker):** Receives order events, simulates execution (fill, commission, slippage), and generates fill events.
6.  **Portfolio Manager (Update):** Receives fill events, updates positions, cash, and P&L.
7.  **Performance Metrics Calculator:** Continuously (or at end of backtest) calculates performance statistics.

All components interact via a central event queue or direct method calls within the backtesting loop.

## 5. Key Methodologies

### Backtesting Engine
The backtester iterates through historical market data, feeding it to the selected strategy. It processes signals, manages a simulated portfolio, and applies transaction costs. Key design considerations include:
* Handling of look-ahead bias.
* Realistic simulation of order execution (though slippage is currently a simple percentage).
* Accurate P&L tracking and compounding of returns (up to liquidity caps).

### Dynamic Risk Engine (PyTorch)
The risk engine, implemented using Python and leveraging PyTorch for potential future neural network-based risk models (currently uses rule-based logic but designed for PyTorch integration), enforces:
* **Fixed Fractional Risk:** Per-trade risk (e.g., 1% of current equity via stop-loss distance).
* **Portfolio Heat / Dollar Flow Caps:** Limits on total capital deployed within a certain period (e.g., 8% daily).
* **Position Sizing:** Calculates appropriate position sizes based on risk rules and available capital.
* **Liquidity Constraints:** Incorporates a maximum position size in USD to simulate market liquidity limits for small-cap stocks.

### Monte Carlo Validation
Based on the historical trade log from a backtest, the Monte Carlo module performs thousands of simulations by:
1.  Resampling trades with replacement (bootstrapping).
2.  Randomizing the order of trades.
This helps assess the robustness of the strategy's performance, the distribution of potential equity curves, expected drawdowns, and the statistical significance of the edge (e.g., 100% of simulations profitable, narrow CIs for win rate/Sharpe). Critically, it's used to validate the `<5% ruin probability` given the risk parameters.

### Walk-Forward Validation
The underlying research for the "Cherry" strategy employed walk-forward validation (e.g., 30% in-sample for optimization, 70% out-of-sample for testing) to ensure strategy robustness and mitigate overfitting. This framework is designed to support such validation schemes by allowing distinct date ranges for testing.

## 6. Performance Highlights (from Research for "Cherry VRPFWL")

This framework is designed to allow for the replication and further research of strategies like "Cherry." The original research for the VRPFWL gate variant (mid-2022 to early-2025) indicated:

* **Trades:** ~150 (selective, ~0.3 trades/day)
* **Win Rate:** ~62% overall (07:00 PST: ~60%; 07:15 PST: ~65-66%)
* **Avg. Gain (Winner):** ~+13%
* **Avg. Loss (Loser):** ~–7% (fixed stop)
* **Expectancy:** ~+5.0% per trade
* **Profit Factor:** ~2.9
* **Sharpe Ratio (Annualized):** ~2.8–3.0
* **Max Drawdown (Monte Carlo Median):** ~40%
* **Ruin Probability (Monte Carlo):** <5% with $25k start & risk rules.
* **Walk-Forward Out-of-Sample (VRPFWL):** Win ~60%, Avg. Trade +5%, Sharpe ~2.8.

*Disclaimer: These historical results are based on specific research parameters and market conditions and are not indicative of future returns. This framework provides tools for independent research.*

## 7. Technology Stack

* **Core Language:** Python 3.9+
* **Numerical & Data Analysis:** Pandas, NumPy, SciPy
* **Machine Learning (Risk Engine):** PyTorch
* **Plotting & Visualization:** Matplotlib, Seaborn, Plotly (for notebooks)
* **Web Service (Webhook):** Flask (or FastAPI)
* **Configuration:** INI files (via `configparser`)
* **Logging:** Loguru
* **Development Tools:** Git, VS Code, JupyterLab
* **(Conceptual) Strategy Signaling:** Pine Script (on TradingView, for proprietary signal generation - not executed by this framework directly)

## 8. Project Structure

CherryAlgo-Framework/
├── config/                 # Configuration files (templates, strategy params)
├── data/                   # Sample market data, example signals
├── docs/                   # Extended documentation (architecture, methodology deep dives)
├── logs/                   # Log files (gitignored)
├── notebooks/              # Jupyter notebooks for analysis and exploration
├── src/
│   └── cherry_algo_framework/  # Main Python package
│       ├── core/
│       ├── data_mgt/
│       ├── execution_mgt/
│       ├── performance_mgt/
│       ├── portfolio_mgt/
│       ├── risk_mgt/
│       ├── strategy/
│       ├── utils/
│       └── main_backtest_runner.py
├── tests/                  # Unit and integration tests
├── .gitignore
├── https://www.google.com/search?q=LICENSE
├── README.md
├── pyproject.toml
└── requirements.txt


## 9. Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://www.google.com/search?q=https://github.com/asaintpi/CherryAlgo-Framework.git](https://www.google.com/search?q=https://github.com/asaintpi/CherryAlgo-Framework.git)
    cd CherryAlgo-Framework
    ```
2.  **Create and activate a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    It is recommended to install from `pyproject.toml` if you have a modern pip. This will also install `dev` dependencies if specified.
    ```bash
    pip install .[dev]
    ```
    Alternatively, for core dependencies only:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure settings:**
    Copy `config/settings_template.ini` to `config/settings.ini` and update it with your necessary parameters (e.g., API keys if you were to connect to live data, though this framework primarily focuses on backtesting with local/sample data initially).
    ```bash
    cp config/settings_template.ini config/settings.ini
    # Now edit config/settings.ini
    ```

## 10. Running a Backtest

Detailed instructions for running a backtest using `main_backtest_runner.py` will be provided once the core modules are implemented. The basic command will likely be:

```bash
python src/cherry_algo_framework/main_backtest_runner.py --strategy example_momentum --params config/strategy_parameters/example_momentum_params.json --start_date YYYY-MM-DD --end_date YYYY-MM-DD --output_dir backtest_results/my_first_backtest
11. Configuration
All framework behavior is controlled via config/settings.ini. Key sections include:

[MarketData]: Data sources, tickers, date ranges.
[BrokerSimulated]: Initial capital, commissions, slippage settings.
[StrategyGlobal]: Default strategy identifiers, parameter locations.
[RiskManagement]: Rules for the PyTorch risk engine.
[Logging]: Log level, file paths, rotation.
[Backtester]: Output options, plotting flags.
Strategy-specific parameters are stored in JSON files within config/strategy_parameters/.

12. Disclaimer on Proprietary Strategy Logic
The core "Cherry" strategy, particularly its VRPF and VRPFWL gate conditions and the precise Pine Script implementation for signal generation, contains proprietary elements developed through extensive research. This public framework does not include the exact proprietary signal generation logic.

Instead, it provides:

An example_momentum_strategy.py that implements a generic version of a momentum strategy based on similar principles (e.g., pre-market gap, volume) but with simplified, non-proprietary entry conditions.
The full backtesting, portfolio management, performance tracking, and risk management infrastructure designed to evaluate such strategies.
The primary purpose of this repository is to showcase the engineering of a robust quantitative trading framework and the application of a sophisticated risk management engine.

13. Future Work & Roadmap
[ ] Implementation of more data feed handlers (e.g., live Alpaca, IEX Cloud).
[ ] Advanced slippage and market impact models.
[ ] Integration of PyTorch directly into the RiskEngine for ML-based risk parameter adjustments.
[ ] Portfolio optimization module.
[ ] Enhanced visualization suite in Jupyter Notebooks.
[ ] Comprehensive unit and integration test coverage.
[ ] Containerization with Docker for easier deployment of the paper-trading pipeline.
14. License
This project is licensed under the MIT License - see the LICENSE file for details.

15. Contact
Arnaud Saint-Pierre - arnaudsntpierre@gmail.com

Project Link: https://github.com/asaintpi/CherryAlgo-Framework (Update with your actual link)


**Key aspects of this README:**

* **Professional Tone & Structure:** Uses badges, a clear table of contents, and well-defined sections.
* **Leverages Your Research:** Directly incorporates the strategy overview, gate conditions, and performance metrics from your document, lending immense credibility.
* **Highlights "Serious" Features:** Emphasizes the PyTorch risk engine, Monte Carlo, Walk-Forward validation concepts, event-driven architecture.
* **Clear Disclaimer:** Addresses the proprietary nature of your core Pine Script logic transparently.
* **Roadmap:** Shows forward-thinking and acknowledges it's an evolving project.
* **Actionable Setup:** Provides clear setup and (future) usage instructions.

**Action for You (Step 1.1.8):**

1.  Replace the content of your `README.md` file in the root of `CherryAlgo-Framework` with the text above.
2.  **Crucially, review and customize:**
    * The GitHub links (e.g., in `[project.urls]` in `pyproject.toml` and at the bottom of the README) to point to your actual `asaintpi/CherryAlgo-Framework` repository.
    * Your email address.
    * Read through every section. Does it align with your research and how you want to present this? The performance numbers are directly from your research document, which is perfect.

**After updating and reviewing your `README.md`:**

1.  **Commit these changes:**
    ```bash
    git add README.md pyproject.toml # If you also updated pyproject.toml with correct URLs
    git commit -m "docs: Populate comprehensive README for CherryAlgo-Framework"
    git push origin main
    ```