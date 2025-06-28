import R from "./ramda.js";

const candycrush = Object.create(null);

// WORKING FUNCTIONS
/**
 * Swaps the candies
 * @memberof candycrush
 * @function
 * @param {number} td1 the grid position of the first candy
 * @param {number} td2 the grid position of the second candy
 */
candycrush.swapCandies = function (td1, td2, grid) {
  const bg1 = td1.style.backgroundImage;
  const bg2 = td2.style.backgroundImage;
  const class1 = td1.className;
  const class2 = td2.className;

  td1.style.backgroundImage = bg2;
  td2.style.backgroundImage = bg1;

  td1.className = class2;
  td2.className = class1;

  // Swap data in the array
  const [row1, col1] = td1.dataset.position.split(",").map(Number);
  const [row2, col2] = td2.dataset.position.split(",").map(Number);

  const temp = grid[row1][col1];
  grid[row1][col1] = grid[row2][col2];
  grid[row2][col2] = temp;
};

/**
 * Swaps the candies 
 * @memberof candycrush
 * @function
 * @param {number} td1 the grid position of the first candy
 * @param {number} td2 the grid position of the second candy
 * @returns {boolean} If the two candies are adjacent
 */
candycrush.isAdjacent = function(td1, td2) {
  const id1 = td1.dataset.position.split(",").map(Number);
  const id2 = td2.dataset.position.split(",").map(Number);
  const [row1, col1] = id1;
  const [row2, col2] = id2;

  const rowDiff = Math.abs(row1 - row2);
  const colDiff = Math.abs(col1 - col2);

  return (rowDiff === 1 && colDiff === 0) || (rowDiff === 0 && colDiff === 1);
};

// MATCH FUNCTIONS
// ARE YA WINNNING SON

// REMOVE FUNCTIONS

// Returns an array of [row, col] positions for horizontal matches of 3
/**
 * Checks for horizontal matches of 3 candies
 * @memberof candycrush
 * @function
 * @param {candycrush.grid} grid the grid position of the first candy
 * @returns {array} Coordinate pairs of matched candies in the grid
 */
const horizontal_match_positions = function (grid) {
  return R.addIndex(R.chain)((row, rowIndex) =>
    R.addIndex(R.chain)((_, colIndex) => {
      const window = row.slice(colIndex, colIndex + 3);
      return window.length === 3 && window.every(c => c === window[0])
        ? [[rowIndex, colIndex], [rowIndex, colIndex + 1], [rowIndex, colIndex + 2]]
        : [];
    })(row)
  )(grid);
};

const vertical_match_positions = function (grid) {
  const transposed = R.transpose(grid); // Flip rows <-> columns
  return R.addIndex(R.chain)((col, colIndex) =>
    R.addIndex(R.chain)((_, rowIndex) => {
      const window = col.slice(rowIndex, rowIndex + 3);
      return window.length === 3 && window.every(c => c === window[0])
        ? [[rowIndex, colIndex], [rowIndex + 1, colIndex], [rowIndex + 2, colIndex]]
        : [];
    })(col)
  )(transposed);
};


//chatgpt
const removeMatchedPositions = function (grid, matchedPositions) {
  const matchSet = new Set(matchedPositions.map(([r, c]) => `${r},${c}`));

  return R.addIndex(R.map)((row, rowIndex) =>
    R.addIndex(R.map)((candy, colIndex) =>
      matchSet.has(`${rowIndex},${colIndex}`) ? null : candy
    )(row)
  )(grid);
};

candycrush.removeHorizontalMatches = function (grid) {
  const matches = horizontal_match_positions(grid);
  return removeMatchedPositions(grid, matches);
};

candycrush.removeVerticalMatches = function (grid) {
  const matches = vertical_match_positions(grid);
  return removeMatchedPositions(grid, matches);
};

candycrush.removeMatches = function (grid) {
  const horizontalMatches = horizontal_match_positions(grid);
  const verticalMatches = vertical_match_positions(grid);
  const allMatches = [...horizontalMatches, ...verticalMatches];
  
  return removeMatchedPositions(grid, allMatches);
};

// update board

candycrush.updateBoardVisuals = function (board, grid, candies) {
  board.forEach((row, rowIndex) => {
    row.forEach((td, colIndex) => {
      const candyType = grid[rowIndex][colIndex];

      if (candyType === null) {
        td.style.backgroundImage = "none";
        td.className = td.classList.contains("selected") ? "selected" : "";
      } else {
        const isSelected = td.classList.contains("selected");
        td.className = `candy-${candyType}` + (isSelected ? " selected" : "");
        td.style.backgroundImage = candies[candyType];
      }
    });
  });
};

// ===== Utility =====
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ===== Cascade Logic =====
const cascadeGrid = grid =>
  R.pipe(
    R.transpose,
    R.map(col => {
      const nonNulls = R.filter(R.complement(R.isNil), col);
      const missing = R.repeat(null, col.length - nonNulls.length);
      return R.concat(missing, nonNulls); // Push nulls to top
    }),
    R.transpose
  )(grid);

// ===== Candy Fill =====
candycrush.fillNewCandies = function (grid, randomCandy) {
  return R.map(
    row => R.map(
      cell => (cell === null ? randomCandy() : cell),
      row
    ),
    grid
  );
};


// ===== Match Detection =====
const matchPositions = function (grid) {
  const h = horizontal_match_positions(grid);
  const v = vertical_match_positions(grid);
  return R.uniqWith(R.equals, R.concat(h, v));
};

// update score :P
const updateScoreDisplay = (gameState) => {
  document.getElementById("score-display1").textContent = `Score: ${gameState.score[1]}`;
  console.log(`Score 1 updated: ${gameState.score[1]}`);
  document.getElementById("score-display2").textContent = `Score: ${gameState.score[2]}`;
  console.log(`Score 2 updated: ${gameState.score[2]}`);
};

const countMatches = function (grid) {
  return matchPositions(grid).length;
};

// ===== Resolve Matches with Delay (for animation cycle) =====
candycrush.resolveMatches = async function (grid, board, candies, gameState, randomCandy, explosion) {
  while (true) {
    const matches = matchPositions(grid); // <-- FIX: get the actual matched positions array
    console.log("Matches found:", matches.length);
    if (matches.length === 0) break;

    matches.forEach(([r, c]) => {
      const cell = board[r][c];
      if (cell) {
        cell.style.backgroundImage = explosion;
      }
    });

    // Wait before removing
    await sleep(250);

    const removed = removeMatchedPositions(grid, matches);
    const cascaded = cascadeGrid(removed);
    const refilled = candycrush.fillNewCandies(cascaded, randomCandy);

    candycrush.updateBoardVisuals(board, refilled, candies);
    grid.splice(0, grid.length, ...refilled);

    await sleep(200);

    // update score
    gameState.score[gameState.currentPlayer] += matches.length * 10; // Optional: scale by matches
    updateScoreDisplay(gameState);

    // check for win
    if (gameState.score[gameState.currentPlayer] >= 250) {
      gameState.gameOver = true;
      alert(`Player ${gameState.currentPlayer} wins!`);
      return;
    }
  }
};


candycrush.switchPlayerTurn = function (gameState) {
  gameState.currentPlayer = (gameState.currentPlayer === 1) ? 2 : 1;
};


export default Object.freeze(candycrush);