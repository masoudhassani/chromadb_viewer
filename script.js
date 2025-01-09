const BASE_URL = "http://localhost:5000"; // Replace with your backend URL
const RESULTS_PER_PAGE = 6;

async function loadCollections() {
    const collectionsDropdown = document.getElementById("collections");

    try {
        const response = await fetch(`${BASE_URL}/collections`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        const collections = data.collections;

        collectionsDropdown.innerHTML = collections
            .map(collection => `<option value="${collection}">${collection}</option>`)
            .join("");
    } catch (error) {
        console.error("Error loading collections:", error);
        collectionsDropdown.innerHTML = `<option value="" disabled>Error loading collections</option>`;
    }
}

async function submitQuery() {
    const collection = document.getElementById("collections").value;
    const query = document.getElementById("query").value;
    const metadataInput = document.getElementById("metadata").value;

    if (!collection) {
        alert("Please select a collection.");
        return;
    }

    let metadata = {};
    if (metadataInput.trim()) {
        try {
            metadata = eval(`(${metadataInput})`); // Safely parse Python-like dict
        } catch (e) {
            alert("Invalid metadata format. Use a Python-like dictionary.");
            return;
        }
    }

    try {
        const response = await fetch(`${BASE_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ collection, query, metadata })
        });

        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        displayResults(data.results);
    } catch (error) {
        console.error("Error processing query:", error);
        document.getElementById("results").innerHTML = "Error loading results.";
    }
}

function displayResults(results) {
    const resultsContainer = document.getElementById("results");
    const paginationControls = document.getElementById("pagination-controls");

    // Clear previous results
    resultsContainer.innerHTML = "";
    paginationControls.innerHTML = "";

    // Paginate results
    const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE);

    function renderPage(page) {
        resultsContainer.innerHTML = "";
        const start = (page - 1) * RESULTS_PER_PAGE;
        const end = start + RESULTS_PER_PAGE;

        results.slice(start, end).forEach(result => {
            const card = document.createElement("div");
            card.classList.add("result-card");
            card.innerHTML = `<p>${JSON.stringify(result)}</p>`;
            resultsContainer.appendChild(card);
        });
    }

    // Render initial page
    renderPage(1);

    // Create pagination buttons
    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.classList.add("pagination-button");
        button.innerText = i;
        button.onclick = () => renderPage(i);
        paginationControls.appendChild(button);
    }
}

// Initialize app
document.getElementById("submit-btn").addEventListener("click", submitQuery);
loadCollections();
