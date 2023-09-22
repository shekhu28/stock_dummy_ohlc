// index.tsx

import Head from 'next/head';
import WebSocketComponent from '../components/WebSocketAPI';

const Home: React.FC = () => {
  return (
    <div>
      <Head>
        <title>Stock OHLC App</title>
        <meta name="description" content="Stock OHLC App" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <WebSocketComponent />
      </main>

    </div>
  );
};

export default Home;
