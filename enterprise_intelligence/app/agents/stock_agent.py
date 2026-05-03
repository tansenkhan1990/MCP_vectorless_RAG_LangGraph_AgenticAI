import yfinance as yf

def stock_node(state):

    ticker = "AAPL"

    if "tesla" in state["question"].lower():
        ticker = "TSLA"

    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        "answer": f"""
Ticker: {ticker}
Price: {info.get("currentPrice")}
PE Ratio: {info.get("trailingPE")}
Market Cap: {info.get("marketCap")}
"""
    }