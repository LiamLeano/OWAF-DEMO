// Find categories list and render buttons as a list

/**
 * slugify()
 * ----------
 * Converts a string into a URL-friendly slug.
 */
function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/[\s_]+/g, '-')      // Replace spaces and underscores with dash.
    .replace(/[^a-z0-9\-]/g, '');  // Remove all non-alphanumeric except dashes.
}

/**
 * getJsonFilePath()
 * -----------------
 * Determines the JSON file path for the current topic's category list.
 * For example, if the URL is /content/software.html, the topic is "software",
 * and the JSON file is expected at /datasets/content/software/software-categories.json.
 */
function getJsonFilePath() {
  let pathParts = window.location.pathname.split('/').filter(Boolean);
  if (pathParts.length < 2) {
    console.error('Invalid URL structure for topic page.');
    return null;
  }
  // The current page file (e.g., "software.html") gives the topic.
  let fileName = pathParts[pathParts.length - 1];
  let topic = fileName.replace('.html', '').toLowerCase();
  return `/datasets/content/${topic}/${topic}-categories.json`;
}

/**
 * renderCategoryButtons()
 * -------------------------
 * Renders category buttons inside the .button-container div.
 * Each button links to a page based on the topic and the category slug.
 * Example output:
 *   <a href="/content/software/drivers.html" class="btn btn-primary btn-lg">
 *     <strong>Drivers</strong>
 *   </a>
 */
function renderCategoryButtons(categories, topic) {
  const container = document.querySelector('.button-container');
  if (!container) {
    console.error("No container found with class 'button-container'.");
    return;
  }
  // Build the HTML for buttons.
  let buttonsHtml = "";
  categories.forEach(category => {
    let catSlug = slugify(category);
    buttonsHtml += `<a href="/content/${topic}/${catSlug}.html" class="btn btn-primary btn-lg"><strong>${category}</strong></a>\n`;
  });
  // Remove the loading screen if present.
  const loadingScreen = document.getElementById("loading-screen");
  if (loadingScreen) {
    loadingScreen.remove();
  }
  // Insert the buttons into the container.
  container.innerHTML = buttonsHtml;
}

/**
 * loadCategoryData()
 * ------------------
 * Main function to fetch the JSON file for the current topic's categories and render buttons.
 */
function loadCategoryData() {
  // Determine the topic from the current URL (e.g., "software" if on /content/software.html).
  let pathParts = window.location.pathname.split('/').filter(Boolean);
  if (pathParts.length < 2) {
    console.error('Invalid URL structure for topic page.');
    return;
  }
  let fileName = pathParts[pathParts.length - 1];
  let topic = fileName.replace('.html', '').toLowerCase();
  
  const jsonUrl = getJsonFilePath();
  if (!jsonUrl) return;

  fetch(jsonUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Unable to fetch data: ${response.statusText}`);
      }
      return response.json();
    })
    .then(categories => {
      // Ensure that categories is an array.
      if (!Array.isArray(categories)) {
        throw new Error("Invalid data format: Expected an array of categories.");
      }
      renderCategoryButtons(categories, topic);
    })
    .catch(error => {
      console.error("Error loading category data:", error);
      const container = document.querySelector('.button-container');
      if (container) {
        container.innerHTML = `<div class="alert alert-danger" role="alert">${error.message}</div>`;
      }
    });
}

// When the DOM is fully loaded, run the function.
document.addEventListener('DOMContentLoaded', loadCategoryData);
