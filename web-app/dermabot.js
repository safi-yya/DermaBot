import R from "./ramda.js";

const dermabot = Object.create(null);

// UTILITIES
dermabot.getTimeOfDayLabel = function(date = new Date()) {
  const hour = date.getHours();
  return hour < 12 ? "morning" : "evening";
}

dermabot.daysBetween = function(date1, date2) {
  return Math.floor((date1 - date2) / (1000 * 60 * 60 * 24));
}

dermabot.shouldUseProduct = function(product, date = new Date()) {
  const time = dermabot.getTimeOfDayLabel(date);
  const uses = product.usageLog || [];
  const lastUsed = uses.length ? new Date(uses[uses.length - 1]) : null;

  const matchesTime =
    product.timeOfDay === time || product.timeOfDay === "both";

  if (!matchesTime) return false;

  if (product.frequency === "daily") return true;
  if (product.frequency === "weekly") {
    if (!lastUsed) return true;
    return dermabot.daysBetween(date, lastUsed) >= 7;
  }
  if (typeof product.frequency === "number") {
    if (!lastUsed) return true;
    return dermabot.daysBetween(date, lastUsed) >= product.frequency;
  }

  return false;
}

dermabot.getRemainingVolume = function(product) {
  const used = (product.usageLog || []).length * product.usagePerUseMl;
  return Math.max(product.totalVolumeMl - used, 0);
}

// RENDER ROUTINE
dermabot.renderRoutine = function(products, container, timeOfDay) {
  container.innerHTML = ""; // clear existing

  const today = new Date();

  const routine = products
    .filter(p => dermabot.shouldUseProduct(p, today) && (p.timeOfDay === timeOfDay || p.timeOfDay === "both"))
    .sort((a, b) => a.stepOrder - b.stepOrder);

  routine.forEach(product => {
    const card = document.createElement("div");
    card.className = "product-card";
    if (dermabot.getRemainingVolume(product) <= 2) {
      card.classList.add("warning");
    }

    card.innerHTML = `
      <h2>${product.name}</h2>
      <p>${typeof product.frequency === "number" ? `Every ${product.frequency} days` : product.frequency}</p>
      <span class="step">Step ${product.stepOrder}</span>
      <button>Mark as Used</button>
    `;

    card.querySelector("button").addEventListener("click", () => {
      dermabot.logUsage(product);
      dermabot.renderRoutine(products, container, timeOfDay);
      dermabot.renderAlert(products);
    });

    container.appendChild(card);
  });
}

// LOG USAGE
dermabot.logUsage = function(product, date = new Date()) {
  product.usageLog = product.usageLog || [];
  product.usageLog.push(date.toISOString());
}

// ALERTS
dermabot.renderAlert = function(products) {
  const banner = document.querySelector(".alert-banner");
  const lowProducts = products.filter(p => dermabot.getRemainingVolume(p) <= 2);

  if (lowProducts.length) {
    banner.textContent = `⚠️ ${lowProducts[0].name} will run out soon!`;
    banner.style.display = "block";
  } else {
    banner.style.display = "none";
  }
}


export default Object.freeze(dermabot);
