# ChillTrade-binance

Template trading bot for futures market on binance exchange.

## Features
- GUI on PyQt5
- logging
- multi-threading

## Installation

```
git clone git://github.com/away2/ChillTrade-binance.git
cd ChillTrade-binance && pip install -r requirements.txt
```

## Usage

Before starting insert your credentials in settings.ini, implement some trade logic in strategy_btc_1h.py and run the bot:

```
cd ChillTrade-binance
./ChillTrade-binance.py
```