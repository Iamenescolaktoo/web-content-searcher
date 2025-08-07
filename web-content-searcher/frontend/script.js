// This file will now fetch real data from your backend APIs.

// The API endpoints for your services as defined in docker-compose.yml
// We will use relative paths or proxies configured in the nginx.conf
const SCRAPPER_API_URL = "http://localhost:8001";
const ANALYZER_API_URL = "http://localhost:5001";

// Select UI elements
const newsList = document.getElementById('newsList');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const sentimentFilter = document.getElementById('sentimentFilter');

// Function to render news cards to HTML
function renderNews(newsToDisplay) {
    newsList.innerHTML = ''; // Clear the list
    if (newsToDisplay.length === 0) {
        newsList.innerHTML = '<p class="col-span-full text-center text-gray-500 text-lg">No news found.</p>';
        return;
    }

    newsToDisplay.forEach(news => {
        // The backend now returns a "risk_point" instead of a "score"
        const scoreColor = news.risk_point > 7 ? 'bg-red-500' : news.risk_point > 4 ? 'bg-yellow-500' : 'bg-green-500';

        // Create the card
        const card = `
            <div class="bg-white border border-gray-200 rounded p-4">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs text-gray-500">${new URL(news.source).hostname} - ${new Date(news.datetime).toLocaleDateString()}</span>
                    <div class="flex items-center space-x-2">
                        <span class="px-2 py-0.5 text-xs font-medium text-white rounded ${scoreColor}">${news.risk_point || 'N/A'}</span>
                    </div>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">${news.title}</h3>
                <div class="flex flex-wrap gap-1 mt-2">
                    ${news.category ? `<span class="px-2 py-0.5 text-xs font-medium text-blue-800 bg-blue-100 rounded">${news.category}</span>` : ''}
                    </div>
                <div class="mt-2">
                    <h4 class="text-sm text-gray-700">Keywords:</h4>
                    <div class="flex flex-wrap gap-1 mt-1">
                        ${news.keywords ? news.keywords.map(keyword => `<span class="px-2 py-0.5 text-xs text-gray-600 bg-gray-200 rounded">${keyword}</span>`).join('') : 'N/A'}
                    </div>
                </div>
            </div>
        `;
        newsList.innerHTML += card;
    });
}

// Function to fetch news from the scraper backend
async function fetchNews() {
    // You might want to add a loading state here
    newsList.innerHTML = '<p class="col-span-full text-center text-gray-500 text-lg">Loading news...</p>';

    try {
        // Example of a hardcoded URL. You can make this dynamic later.
        const response = await fetch(`${SCRAPPER_API_URL}/scrape?url=https://www.cnnturk.com/feed/rss/all/all`, {
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const newsData = data.data; // The actual news list is in the 'data' field
        renderNews(newsData);

    } catch (error) {
        console.error("Failed to fetch news:", error);
        newsList.innerHTML = `<p class="col-span-full text-center text-red-500 text-lg">Error fetching news: ${error.message}</p>`;
    }
}

// Function to analyze a piece of text using the LLM API
async function analyzeText(text) {
    try {
        const response = await fetch(`${ANALYZER_API_URL}/metin_analiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ metin: text })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log("Analyzed text result:", data);
        return data;

    } catch (error) {
        console.error("Failed to analyze text:", error);
        return null;
    }
}

// Event listeners to run on page load and when filters change
document.addEventListener('DOMContentLoaded', () => {
    // We now call the fetchNews function instead of rendering mock data
    fetchNews();
});

// The filter and search functions would need to be updated to work with the fetched data
// and potentially make new API calls, but for now, we'll just focus on fetching the initial data.
function filterAndSearch() {
    // This function will need to be updated to filter the fetched newsData
    // For now, we will simply refetch the data.
    console.log("Filter and search functionality to be implemented with fetched data.");
}

searchInput.addEventListener('input', filterAndSearch);
categoryFilter.addEventListener('change', filterAndSearch);
sentimentFilter.addEventListener('change', filterAndSearch);
