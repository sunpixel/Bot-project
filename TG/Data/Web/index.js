const tg = window.Telegram.WebApp;
tg.expand(); // Optional

function placeOrder() {
  const orderData = {
    items: [
      { name: "Apple", qty: 3, price: 6 },
      { name: "Banana", qty: 5, price: 5 },
      { name: "Orange", qty: 2, price: 4 }
    ],
    total: 15
  };

  tg.sendData(JSON.stringify(orderData));
  tg.close();
}
