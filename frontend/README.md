This is the client side of the stock data project. It will a dummy OHLC data relative to the current time.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [https://localhost:3001](https://localhost:3001) with your browser to see the result. Note that the browser may show it s potentially harmful since the certificate is self signed

## Building and Running the project

Build the project:

```bash
npm run build
# or
yarn build
```

now, once the frontend is built, you can run the frontend by:

```bash
npm start
# or
yarn start
```

You can start editing the page by modifying `pages/index.tsx`. The page auto-updates as you edit the file.

## Key Storage

Generate a RSA key and a CRT certificate as a .pem file and place it inside .secure/ folder.
