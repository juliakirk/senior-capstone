const slider = document.getElementById("COL");
const sliderValue = document.getElementById("sliderValue");

slider.addEventListener("input", () => {
  sliderValue.textContent = `$${slider.value.toLocaleString()}`;
});
