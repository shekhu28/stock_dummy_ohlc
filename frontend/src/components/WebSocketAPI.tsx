import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { StockData } from '@/types/stock_data_type';
import moment from 'moment';

const SOCKET_URL = 'http://localhost:8080';

const WebSocketComponent: React.FC = () => {
  const [data, setData] = useState<StockData | null>(null); // Initialize as null

  useEffect(() => {
    const socket: Socket = io(SOCKET_URL);

    socket.on('connect', () => {
      console.log('Connected to the server');
    });

    socket.on('stock_data', (newData) => {
      const parsedData: StockData = JSON.parse(newData);
      setData(parsedData);
      console.log('Received stock data from the server', parsedData);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-blue-500 text-white py-4 text-center">
        <h1 className="text-3xl font-bold">Stock Technical Indicator</h1>
        <div className="space-x-4 mt-4">
          {data ? ( // Check if data is available
            <>
              <div className="bg-gray-800 p-2 rounded-md inline-block">
                <span className="cursor-pointer hover:underline">SMA</span>: {data.sma.toFixed(2)}
              </div>
              <div className="bg-gray-800 p-2 rounded-md inline-block">
                <span className="cursor-pointer hover:underline">EMA</span>: {data.ema.toFixed(2)}
              </div>
              <div className="bg-gray-800 p-2 rounded-md inline-block">
                <span className="cursor-pointer hover:underline">RSI</span>: {data.rsi.toFixed(2)}
              </div>
            </>
          ) : (
            <div className="bg-gray-800 p-2 rounded-md inline-block">
              Unable to fetch the data from the server.
            </div>
          )}
        </div>
      </header>

      <main className="container mx-auto py-8 px-4">
        {data && data.symbol ? ( // Check if data and symbol are available
          <div className="mt-8">
            <h2 className="text-2xl font-bold mb-4">
              {data.symbol} Data - {moment(data.ohlc[0].timestamp).format('YYYY-MM-DD')}
            </h2>

            <div className="bg-gray-800 p-4 rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <div className="w-full h-128 overflow-auto">
                  <table className="w-full border-collapse shadow-lg bg-gray-900 text-white">
                    <thead className="bg-blue-500">
                      <tr>
                        <th className="border text-left px-4 py-2">Time</th>
                        <th className="border text-left px-4 py-2">Open</th>
                        <th className="border text-left px-4 py-2">High</th>
                        <th className="border text-left px-4 py-2">Low</th>
                        <th className="border text-left px-4 py-2">Close</th>
                        <th className="border text-left px-4 py-2">Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.ohlc.map((item: any, index: number) => (
                        <tr key={index}>
                          <td className="border px-4 py-2">
                            {moment(item.timestamp).format('HH:mm')}
                          </td>
                          <td className="border px-4 py-2">{item.open.toFixed(2)}</td>
                          <td className="border px-4 py-2">{item.high.toFixed(2)}</td>
                          <td className="border px-4 py-2">{item.low.toFixed(2)}</td>
                          <td className="border px-4 py-2">{item.close.toFixed(2)}</td>
                          <td className="border px-4 py-2">{item.volume.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
};

export default WebSocketComponent;
