// FlavorForge frontend logic
// This file talks to the Flask backend (app.py) at the /suggest endpoint.

const form = document.getElementById("ingredient-form");
const input = document.getElementById("ingredient-input");
const statusArea = document.getElementById("status-area");
const resultsGrid = document.getElementById("results-grid");

form.addEventListener("submit", async (e) => {
  e.preventDefault(); // stop the page from reloading on submit

  const ingredients = input.value.trim();
  if (!ingredients) {
    statusArea.textContent = "Type at least one ingredient to get started.";
    resultsGrid.innerHTML = "";
    return;
  }

  statusArea.textContent = "Firing up the forge...";
  resultsGrid.innerHTML = "";

  try {
    const response = await fetch("/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ingredients }),
    });

    if (!response.ok) {
      throw new Error("Server error: " + response.status);
    }

    const data = await response.json();
    renderResults(data.results);
  } catch (err) {
    console.error(err);
    statusArea.textContent = "Something went wrong talking to the server. Is app.py running?";
  }
});

function renderResults(results) {
  if (!results || results.length === 0) {
    statusArea.textContent = "No matching recipes found. Try different or fewer ingredients.";
    resultsGrid.innerHTML = "";
    return;
  }

  statusArea.textContent = `Found ${results.length} recipe${results.length > 1 ? "s" : ""} for you:`;

  resultsGrid.innerHTML = results.map(recipe => `
    <article class="recipe-card">
      <div class="card-top">
        <div>
          <h3>${escapeHtml(recipe.name)}</h3>
          <div class="meta-row">
            <span>${escapeHtml(recipe.cuisine)}</span>
            <span>${escapeHtml(recipe.diet)}</span>
            <span>${escapeHtml(String(recipe.time_minutes))} min</span>
          </div>
        </div>
        <div class="heat-gauge" style="--pct: ${recipe.match_percent}">
          <span>${recipe.match_percent}%</span>
        </div>
      </div>

      <div class="ingredient-tags">
        ${recipe.matched_ingredients.map(i => `<span class="tag have">${escapeHtml(i)}</span>`).join("")}
        ${recipe.missing_ingredients.map(i => `<span class="tag missing">+ ${escapeHtml(i)}</span>`).join("")}
      </div>

      <p class="instructions">${escapeHtml(recipe.instructions)}</p>
    </article>
  `).join("");
}

// Basic escaping so recipe text can never break the page's HTML
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
