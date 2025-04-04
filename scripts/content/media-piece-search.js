// Find media piece and render page

// List of link keys that will be used to generate link buttons.
const linkKeys = ["source_link", "download_link", "magnet_link"];

/**
 * getJsonFilePath()
 * -----------------
 * Extracts the topic, category and filename from the current URL to build the path to the JSON fragment.
 */
function getJsonFilePath() {
  let pathParts = window.location.pathname.split('/').filter(Boolean);
  // Expected URL structure: /content/{topic}/{category}/{fileName}.html
  if (pathParts.length < 4) {
    console.error('Invalid URL structure for locating dataset.');
    return null;
  }
  // directory layout:
  // [ "content", "{topic}", "{category}", "{fileName}.html" ]
  let topic = pathParts[pathParts.length - 3];    // topic
  let category = pathParts[pathParts.length - 2];   // category
  let fileName = pathParts[pathParts.length - 1].replace('.html', '').toLowerCase(); //media-piece
  return `/datasets/content/${topic}/${category}/${fileName}.json`; // directory
}

/**
 * capitalizeWords(str)
 * ---------------------
 * Capitalizes each word in a string.
 */
function capitalizeWords(str) {
  return str
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * createCard(data)
 * ----------------
 * Creates and returns a Bootstrap card with a two-column layout:
 * - The left column displays a table of details based on the data keys.
 * - It combines "file_size" and "data_metric" into one row labeled "File Size".
 * - The left column also displays link buttons that are disabled if the corresponding URL is null.
 * - The right column displays screenshot image(s) (stacked vertically if multiple).
 */
function createCard(data) {
  // Create the main card container.
  const card = document.createElement('div');
  card.className = 'card mt-3 mb-3';

  const cardBody = document.createElement('div');
  cardBody.className = 'card-body';

  const row = document.createElement('div');
  row.className = 'row';

  // LEFT COLUMN: Details and link buttons.
  const leftCol = document.createElement('div');
  leftCol.className = 'col-md-6';

  // Create a table for the details.
  const table = document.createElement('table');
  table.className = 'table table-sm';

  // Get all keys from the data object.
  const keys = Object.keys(data);

  // Filter out keys you want to exclude from the table display.
  const filteredKeys = keys.filter(key => !["id", "name", "media_piece_path", "screenshot_path"].includes(key) && !linkKeys.includes(key));

  // For each key in the data, add a row to the table.
  filteredKeys.forEach(field => {
    // If field is "data_metric", we skip it because we combine it with file_size.
    if (field === "data_metric") return;

    const tr = document.createElement('tr');
    const tdLabel = document.createElement('td');
    tdLabel.style.width = '30%';
    tdLabel.className = 'content-paragraph';
    const labelStrong = document.createElement('strong');
    // For "file_size", display label as "File Size".
    const labelText = field === "file_size" ? "file size" : field;
    labelStrong.textContent = capitalizeWords(labelText.replace(/_/g, ' '));
    tdLabel.appendChild(labelStrong);

    const tdValue = document.createElement('td');
    tdValue.className = 'content-paragraph';
    let value;
    if (field === "file_size") {
      // Combine file_size and data_metric.
      const size = data["file_size"];
      const metric = data["data_metric"];

      if (size !== null && size !== undefined) {
        value = (metric !== null && metric !== undefined) ? size + metric : size + "";
      } else {
        value = (metric !== null && metric !== undefined) ? "N/A" + " " + metric : "N/A";
      }
    } else {
      value = data[field] !== null && data[field] !== undefined ? data[field] : 'N/A';
    }
    tdValue.textContent = value;

    tr.appendChild(tdLabel);
    tr.appendChild(tdValue);
    table.appendChild(tr);
  });

  leftCol.appendChild(table);

  // Container for link buttons.
  const linksDiv = document.createElement('div');
  linksDiv.className = 'button-container';

  // Create a button for each link key.
  linkKeys.forEach(key => {
    const url = data[key]; // Get the URL from the JSON data.
    const a = document.createElement('a');
    a.className = 'btn btn-primary btn-lg'; // Base button styles

    if (url) {
      a.href = url;
      a.target = '_blank';
    } else {
      a.href = "#";
      a.classList.add("disabled");
      a.setAttribute("aria-disabled", "true");
    }

    // Create a <strong> element for the button text.
    const strong = document.createElement('strong');
    strong.textContent = capitalizeWords(key.replace(/_/g, ' '));
    a.appendChild(strong);

    linksDiv.appendChild(a);
  });

  leftCol.appendChild(linksDiv);

  // RIGHT COLUMN: Screenshot image(s).
  const rightCol = document.createElement('div');
  rightCol.className = 'col-md-6 d-flex flex-column align-items-center justify-content-center';
  if (data.screenshot_path) {
    let imageSource;
    if (Array.isArray(data.screenshot_path)) {
      imageSource = data.screenshot_path[0]; // Get the first image path from the array
    } else {
      imageSource = data.screenshot_path; // Get the single image path
    }

    const img = document.createElement('img');
    img.src = imageSource;
    img.alt = data.name;
    img.className = 'img-fluid';
    img.onerror = function() {
      this.onerror = null;
      this.src = '/media/owaf/images/image-404.png';
    };
    rightCol.appendChild(img);
  }

  row.appendChild(leftCol);
  row.appendChild(rightCol);

  cardBody.appendChild(row);
  card.appendChild(cardBody);

  return card;
}

/**
 * showLoadingScreen()
 * ---------------------
 * Displays a loading screen inside the element with class "media-piece-search"
 * while data is being fetched.
 */
function showLoadingScreen() {
  const container = document.querySelector('.media-piece-search');
  if (container) {
    container.innerHTML = ``;
  }
}

/**
 * loadFragmentData()
 * -------------------
 * Main function that:
 * 1. Shows the loading screen.
 * 2. Fetches the JSON data from the path determined by getJsonFilePath().
 * 3. Clears the loading screen and appends the card created by createCard(data)
 * to the container.
 * 4. Handles errors by displaying an alert.
 */
function loadFragmentData() {
  showLoadingScreen();

  const jsonUrl = getJsonFilePath();
  if (!jsonUrl) {
    console.error('Failed to determine JSON file path.');
    return;
  }

  fetch(jsonUrl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Unable to fetch data: ${response.statusText}`);
      }
      return response.json();
    })
    .then(data => {
      const container = document.querySelector('.media-piece-search');
      if (container) {
        container.innerHTML = ''; // Clear the loading screen.
        container.appendChild(createCard(data));
      } else {
        console.error('No container found with class "media-piece-search"');
      }
    })
    .catch(error => {
      console.error('Error loading JSON fragment:', error);
      const container = document.querySelector('.media-piece-search');
      if (container) {
        container.innerHTML = `<div class="alert alert-danger" role="alert">
          ${error.message}
        </div>`;
      }
    });
}

document.addEventListener('DOMContentLoaded', loadFragmentData);