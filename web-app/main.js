import R from "./ramda.js";
import candycrush from "./candycrush.js";

const row_count = 8;
const col_count = 8;
const candies = {
  1: "url(./assets/ship.png)",
  2: "url(./assets/map.png)",
  3: "url(./assets/parrot.png)",
  4: "url(./assets/hat.png)",
  5: "url(./assets/bottle.png)",
  6: "url(./assets/treasure.png)",
  7: "url(./assets/shiphoriz.png)",
  8: "url(./assets/maphoriz.png)",
  9: "url(./assets/parrothoriz.png)",
  10: "url(./assets/hathoriz.png)",
  11: "url(./assets/bottlehoriz.png)",
  12: "url(./assets/treasurehoriz.png)",
  13: "url(./assets/shipvert.png)",
  14: "url(./assets/mapvert.png)",
  15: "url(./assets/parrotvert.png)",
  16: "url(./assets/hatvert.png)",
  17: "url(./assets/bottlevert.png)",
  18: "url(./assets/treasurevert.png)"
};

const explosion = "url(./assets/explosion.png)";

const candy_grid = [
  [1,1,2,3,4,1,1,4],
  [3,5,1,6,2,5,4,5],
  [3,1,5,3,3,2,5,6],
  [1,2,6,3,5,4,1,2],
  [1,4,6,2,6,6,1,2],
  [6,5,3,2,4,5,2,6],
  [2,3,4,5,6,6,5,3],
  [3,4,1,1,2,6,5,4]
];

const grid = document.getElementById("grid");

let firstSelected = null;

let gameState = {
  score: { 1: 0, 2: 0 },
  currentPlayer: 1,
  gameOver: false
};


// random candy
const randomCandy = function () {
  return Math.floor(Math.random() * 6) + 1;
};

/*Generate our gorgeous candy board depending on start grid*/

const board = candy_grid.map(function (row, row_index) {
  const tr = document.createElement("tr");
  grid.append(tr);

  return row.map(function (candyType, col_index) {
    const td = document.createElement("td");

    td.className = `candy-${candyType}`;
    td.style.backgroundImage = candies[candyType];
    td.style.backgroundSize = "cover";
    td.dataset.position = `${row_index},${col_index}`;

    // Click to select or swap
    td.onclick = async function () {
      if (!firstSelected) {
        firstSelected = td;
        td.classList.add("selected");
        return;
      }

      if (td === firstSelected) {
        td.classList.remove("selected");
        firstSelected = null;
        return;
      }

      if (candycrush.isAdjacent(firstSelected, td)) {
        candycrush.swapCandies(firstSelected, td, candy_grid);

        // Handle cascade & matches
        await candycrush.resolveMatches(candy_grid, board, candies, gameState, randomCandy, explosion);
        candycrush.switchPlayerTurn(gameState);
      }

      // Deselect both
      firstSelected.classList.remove("selected");
      td.classList.remove("selected");
      firstSelected = null;
    };

    tr.append(td);
    return td;
  });
});
