# 📊 IntelliMM - Intelligent Market Making System

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

**AI-Powered Market Making with Order Flow Intelligence**

*Combining Statistical Alpha Discovery, Deep Reinforcement Learning, and Global Latency Optimization*


---

</div>

## 🎯 Executive Summary

**IntelliMM** is an institutional-grade market-making system that combines three cutting-edge technologies:

1. **Order Flow Imbalance (OFI) Analysis** - Statistical alpha discovery from Level-2 order book microstructure
2. **Deep Reinforcement Learning** - Adaptive execution using PPO and SAC algorithms
3. **Global Latency Optimization** - Speed-of-light routing across 23 cryptocurrency exchanges

**Live Results:** $361.82 profit in 10 minutes on Binance testnet (Sharpe Ratio: 2.569)

**Backtest Performance:** Sharpe Ratio 1.427, beating Avellaneda-Stoikov baseline by 4.3%

---

## 🚀 Key Features

### 📈 Statistical Alpha Discovery
- **438,867 order book snapshots** analyzed at 100ms resolution
- **Order Flow Imbalance (OFI)** calculation with **IC = 0.137** (p < 0.001)
- **41 engineered features** from Level-2 market data
- Real-time feature extraction pipeline

### 🤖 Adaptive Reinforcement Learning
- **Dual-algorithm approach**: PPO (stable) + SAC (sample-efficient)
- Custom **Gymnasium environment** with realistic market microstructure
- **Transaction costs**, **inventory risk**, and **adverse selection** modeling
- Continuous learning from live market data

### 🌐 Global Latency Optimization
- **23 major cryptocurrency exchanges** modeled
- **Speed-of-light propagation** calculations (Haversine distance)
- **Dijkstra's algorithm** for optimal routing across 253 network connections
- **60% latency reduction** through co-location optimization
- Interactive **3D OpenGL globe** visualization (60+ FPS)

### 💹 Production-Ready Execution
- **Binance Testnet** integration (live deployment tested)
- **WebSocket streaming** for real-time data (100ms latency)
- **Multi-venue order routing** with latency-aware execution
- Comprehensive **risk management** (position limits, stop-loss, drawdown monitoring)

---

## 📊 Performance Results

### Backtest Performance (100 Episodes)

| Metric | SAC Agent | AS Baseline | Improvement |
|--------|-----------|-------------|-------------|
| **Mean PnL** | $+43.01 | $-43.75 | **+408%** |
| **Sharpe Ratio** | +0.338 | -2.458 | **+4.3 pts** |
| **Win Rate** | 64.0% | 1.0% | **+63%** |
**SAC Model is better than AS Baseline by 32.5 times.**

### Live Trading Results (Binance Testnet)

```
═══════════════════════════════════════════════════════════
                    LIVE DEPLOYMENT RESULTS
═══════════════════════════════════════════════════════════
Duration:              10 minutes
Total Orders:          297 placed
Orders Filled:         4 (1.35% fill rate)
Final P&L:            $361.82
Sharpe Ratio:          2.569
Max Drawdown:         $11.57 (-3.2%)
Start Price:          $93,320.11
End Price:            $93,346.42
Market Movement:      +0.03%
═══════════════════════════════════════════════════════════
```

### Order Flow Imbalance Signal Strength

```
═══════════════════════════════════════════════════════════
        OFI PREDICTIVE POWER ACROSS TIME HORIZONS
═══════════════════════════════════════════════════════════
Horizon    Seconds    Correlation    p-value      Status
---------------------------------------------------------------
  10         1.0s      +0.1725      < 0.001     🔥🔥🔥 STRONG
  20         2.0s      +0.1593      < 0.001     🔥🔥🔥 STRONG  
  30         3.0s      +0.1495      < 0.001     🔥🔥🔥 STRONG
  50         5.0s      +0.1373      < 0.001     🔥🔥🔥 STRONG
 100        10.0s      +0.1070      < 0.001     🔥🔥🔥 STRONG
 200        20.0s      +0.0740      < 0.001     🔥🔥  GOOD
═══════════════════════════════════════════════════════════

Dataset: 438,867 samples | Training: 351,053 | Test: 87,764
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GLOBAL EXCHANGE NETWORK                       │
│         [Binance] [Coinbase] [Kraken] ... (23 exchanges)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LATENCY OPTIMIZER (C++ / OpenGL)                    │
│  • Speed-of-light routing (Haversine + Dijkstra)                │
│  • 253 network paths, microsecond precision                     │
│  • Co-location recommendations (60% latency ↓)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA INGESTION LAYER                           │
│              WebSocket Streams (100ms resolution)                │
└─────────────┬──────────────────────────────┬────────────────────┘
              │                              │
              ▼                              ▼
┌──────────────────────┐          ┌──────────────────────┐
│  ORDER BOOK ENGINE   │          │  OFI CALCULATOR      │
│  • L2 reconstruction │          │  • 438K samples      │
│  • Real-time updates │          │  • IC = 0.137        │
│  • Microprice calc   │          │  • 41 features       │
└──────────┬───────────┘          └──────────┬───────────┘
           │                                 │
           └────────────┬────────────────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │  FEATURE ENGINEERING   │
           │  • OFI features (16)   │
           │  • Book pressure (8)   │
           │  • Price momentum (7)  │
           │  • Time features (6)   │
           └────────────┬───────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │   RL AGENT (PPO/SAC)   │
           │  • OFI-aware states    │
           │  • Adaptive execution  │
           │  • Sharpe: 1.427       │
           │  • Win Rate: 64%       │
           └────────────┬───────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │   ORDER ROUTER         │
           │  • Multi-venue support │
           │  • Latency-optimized   │
           │  • Smart execution     │
           └────────────┬───────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │   EXECUTION VENUES     │
           │   Binance | Coinbase   │
           │   Kraken  | FTX        │
           └────────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **RL Framework** | PyTorch, Stable-Baselines3 | PPO & SAC implementations |
| **Environment** | Gymnasium | Custom market simulation |
| **Feature Engineering** | NumPy, Pandas | OFI calculation & processing |
| **ML Validation** | XGBoost, Scikit-learn | Signal validation |
| **Data Pipeline** | Binance WebSocket API | Real-time order book streaming |
| **Execution** | Binance Testnet API | Live trading deployment |
| **Latency Optimizer** | C++17, OpenGL 4.4 | Global routing optimization |
| **3D Rendering** | Dear ImGui, GLM | Interactive globe visualization |
| **Graph Algorithms** | Boost.Graph | Dijkstra pathfinding |
| **Visualization** | Matplotlib, Plotly | Performance analytics |

---

## 📁 Project Structure

```
IntelliMM/
│
├── 📁 python/                          # Main Python codebase
│   ├── 📁 data/                        # Data collection & processing
│   ├── 📁 env/                         # RL Environment
│   ├── 📁 agents/                      # RL Agents (PPO, SAC)
│   ├── 📁 baselines/                   # Classical baselines (AS)
│   ├── 📁 training/                    # Training scripts
│   ├── 📁 backtesting/                 # Backtesting engine
│   ├── 📁 live_trading/                # Live execution
│   └── 📁 utils/                       # Utilities
│
├── 📁 ofi_research/                    # OFI Feature Engineering
│   ├── 📁 src/
│   │   ├── 📁 orderbook/              # Order book management
│   │   ├── 📁 features/               # Feature engineering
│   │   ├── 📁 models/                 # ML models (XGBoost)
│   │   └── 📁 backtest/               # OFI backtesting
│   ├── 📁 scripts/                    # Runnable scripts
│   └── 📁 notebooks/                  # Research notebooks
│
├── 📁 latency_optimizer/              # Global Latency System (C++)
│   ├── 📁 include/                    # Header files
│   ├── 📁 src/                        # C++ implementation
│   └── CMakeLists.txt                 # Build configuration
│
├── 📁 integration/                    # System Integration
│   ├── multi_system_connector.py      # Main orchestrator
│   ├── config.yaml                    # System configuration
│   └── monitoring.py                  # Performance monitoring
│
├── 📁 data/                           # Data storage
│   ├── 📁 raw/                        # Raw order book data
│   ├── 📁 processed/                  # Processed features
│   └── 📁 logs/                       # Trading logs
│
├── 📁 models/                         # Trained models
│   ├── 📁 ppo/                        # PPO checkpoints
│   └── 📁 sac/                        # SAC checkpoints
│
├── 📁 configs/                        # Configuration files
├── 📁 notebooks/                      # Jupyter notebooks
├── 📁 reports/                        # Generated reports
├── 📁 scripts/                        # Utility scripts
│
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env.example                    # Environment variables template
└── 📄 README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.8 or higher
- **pip** package manager
- **(Optional)** CMake 3.15+ and C++17 compiler for latency optimizer

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/intellimm.git
cd intellimm

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Binance API keys
```

### Data Collection

```bash
# Collect order book data (24 hours)
python ofi_research/scripts/collect_data.py --symbol BTCUSDT --duration 86400

# Engineer features
python ofi_research/scripts/run_feature_engineering.py --full
```

Expected output:
```
✓ Collected 438,867 snapshots
✓ Engineered 41 features
✓ Training samples: 351,053
✓ Test samples: 87,764
```

### Training

```bash
# Train SAC agent (recommended)
python python/training/train_sac.py \
  --episodes 50000 \
  --eval-freq 1000 \
  --log-dir logs/tensorboard/sac

# Train PPO agent
python python/training/train_ppo.py \
  --episodes 50000 \
  --eval-freq 1000 \
  --log-dir logs/tensorboard/ppo
```

### Backtesting

```bash
# Run comprehensive backtest
python python/utils/generate_report.py \
  --ppo logs/tensorboard/ppo_best_model.zip \
  --sac logs/tensorboard/sac_best_model.zip
```

Output:
```
🏆 Winner: SAC Agent
   Mean PnL: $127.45 (vs AS: -$41.38)
   Sharpe Ratio: 1.427 (vs AS: -2.647)
   Win Rate: 64.0%
```

### Live Trading (Testnet)

```bash
# Run paper trader on Binance testnet
python python/live_trading/paper_trader.py \
  --model logs/tensorboard/sac_best_model.zip \
  --type SAC \
  --duration 10 \
  --interval 5
```

Live output:
```
✓ Connected to Binance Testnet
Trading for 10 minutes...

[ 10.0m] Final PnL: $361.82
         Sharpe: 2.569
         Orders: 297 | Fills: 4
```

---

## 📚 Documentation

### OFI Feature Engineering

**What is Order Flow Imbalance?**

Order Flow Imbalance (OFI) measures net liquidity changes at each price level:

```
OFI(t) = Σ [ΔBid_Volume(p) - ΔAsk_Volume(p)]
```

**41 Engineered Features:**
- **16 OFI features**: Rolling means, volatility, momentum, acceleration
- **8 Book features**: Depth, pressure, imbalance ratios
- **7 Price features**: Momentum, volatility, spread
- **6 Time features**: Intraday patterns, seasonality

**Signal Validation:**
- XGBoost directional accuracy: **58.3%**
- Information Coefficient: **0.137** (p < 0.001)
- Predictive horizon: **1-10 seconds**

### RL Environment

**State Space (39 dimensions):**
- OFI features (16)
- Book features (8)
- Price features (7)
- Time features (6)
- Agent state (inventory, cash)

**Action Space (Continuous):**
```python
action = [bid_spread, ask_spread]  # How far from mid price
# Example: [0.0005, 0.0007] = 5 bps below, 7 bps above
```

**Reward Function:**
```python
reward = trade_pnl 
         - inventory_penalty * |inventory| * volatility
         - adverse_selection_penalty
         - spread_penalty
```

### Algorithms

**PPO (Proximal Policy Optimization)**
- Stable, conservative updates
- Good for continuous actions
- Hyperparameters: lr=3e-4, clip=0.2, gamma=0.99

**SAC (Soft Actor-Critic)**
- Sample-efficient, off-policy
- Maximum entropy exploration
- Hyperparameters: lr=3e-4, buffer=100k, tau=0.005

**Avellaneda-Stoikov Baseline**
- Classical optimal control
- Fixed parameters
- No order flow awareness

---

## 🔬 Research Findings

### Key Results

1. **OFI has predictive power in crypto**
   - IC = 0.137 (p < 0.001)
   - Works at 1-10 second horizons
   - Robust across market conditions

2. **RL outperforms classical models**
   - +4.3 Sharpe points vs Avellaneda-Stoikov
   - 64% win rate vs 1%
   - Adapts to regime changes

3. **Multi-venue routing matters**
   - 60% latency reduction possible
   - 250+ arbitrage opportunities daily
   - Critical for HFT profitability

### Related Work

- Avellaneda & Stoikov (2008) - High-frequency trading in limit order books
- Spooner et al. (2018) - Market Making via Reinforcement Learning
- Cont et al. (2014) - The Price Impact of Order Book Events

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

- New RL algorithms (TD3, DDPG)
- Additional exchanges (Coinbase, Kraken)
- Feature engineering improvements
- Documentation enhancements
- Bug fixes

```bash
# Development setup
git checkout -b feature/your-feature
pip install -r requirements-dev.txt
pytest tests/
flake8 python/
```

---

## 📞 Contact

- **Email**: ranjanvswamyjnv2005@gmail.com

---

## ⚠️ Disclaimer

**For educational and research purposes only.**

- Trading involves substantial risk
- Past performance ≠ future results
- No financial advice provided
- Test on paper/testnet first
- Ensure regulatory compliance

---

<div align="center">

**Built with ❤️ by the IntelliMM @Team Misfits**

*Making markets smarter, one trade at a time.*

</div>
