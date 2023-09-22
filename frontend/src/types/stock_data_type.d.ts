export interface StockData {
  symbol: string;
  ohlc: {
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    timestamp: string;
  }[];
  sma: number;
  ema: number;
  rsi: number;
}