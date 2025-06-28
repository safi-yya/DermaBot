import R from "./ramda.js";
import dermabot from "./dermabot.js";

const products = [
  {
    name: "Retinol 0.5%",
    timeOfDay: "evening",
    stepOrder: 3,
    frequency: 3, // use every 3 days
    totalVolumeMl: 30,
    usagePerUseMl: 0.5,
    usageLog: ["2025-06-25T21:00:00Z"],
  },
  {
    name: "Cleanser",
    timeOfDay: "morning",
    stepOrder: 1,
    frequency: "daily",
    totalVolumeMl: 100,
    usagePerUseMl: 1,
    usageLog: [],
  },
  {
    name: "Moisturizer",
    timeOfDay: "both",
    stepOrder: 4,
    frequency: "daily",
    totalVolumeMl: 50,
    usagePerUseMl: 0.8,
    usageLog: [],
  }
];

document.addEventListener("DOMContentLoaded", () => {
  const routineGrid = document.querySelector(".routine-grid");
  const toggleButtons = document.querySelectorAll(".routine-toggle button");

  let currentTime = "morning";
  dermabot.renderRoutine(products, routineGrid, currentTime);
  dermabot.renderAlert(products);

  toggleButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      toggleButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentTime = btn.textContent.toLowerCase();
      renderRoutine(products, routineGrid, currentTime);
    });
  });
});
