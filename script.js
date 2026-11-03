// JavaScript: browser (client) ke andar chalta hai, server par nahi.
const service = document.getElementById("service");
const price = document.getElementById("price");
const date = document.getElementById("date");

if (service) {
  const showPrice = () => {
    const p = service.selectedOptions[0].dataset.price;
    price.textContent = "Fee: Rs " + p;
  };
  service.addEventListener("change", showPrice);
  showPrice();
}
if (date) {
  // purani tareekh select na ho sakay
  date.min = new Date().toISOString().split("T")[0];
}
