// Mock news data (simulating data from the backend)
const newsData = [
    {
        id: 1,
        title: "Central Bank Announces New Interest Rate Decisions",
        source: "Economy Journal",
        date: "2024-08-07",
        category: "Economy",
        sentiment: "Neutral",
        toxicity: "Clean",
        score: 65,
        keywords: ["Central Bank", "interest rate", "economy"]
    },
    {
        id: 2,
        title: "Football Federation's Decisions for the New Season",
        source: "Sports News",
        date: "2024-08-06",
        category: "Sports",
        sentiment: "Positive",
        toxicity: "Clean",
        score: 45,
        keywords: ["Football", "season", "decisions"]
    },
    {
        id: 3,
        title: "Next-Generation AI Models Introduced",
        source: "Technology Post",
        date: "2024-08-07",
        category: "Technology",
        sentiment: "Positive",
        toxicity: "Clean",
        score: 80,
        keywords: ["AI", "technology", "next-gen"]
    },
    {
        id: 4,
        title: "Health Ministry's Statement on Epidemic",
        source: "News Portal",
        date: "2024-08-05",
        category: "Health",
        sentiment: "Negative",
        toxicity: "Slight",
        score: 95,
        keywords: ["health", "epidemic", "statement"]
    },
    {
        id: 5,
        title: "Lively Developments in Domestic Politics",
        source: "Political Analysis",
        date: "2024-08-07",
        category: "Politics",
        sentiment: "Neutral",
        toxicity: "Clean",
        score: 70,
        keywords: ["politics", "developments", "domestic policy"]
    },
    {
        id: 6,
        title: "Work Done After the Earthquake",
        source: "National Newspaper",
        date: "2024-08-07",
        category: "Politics",
        sentiment: "Neutral",
        toxicity: "Clean",
        score: 100, // Score increased due to "earthquake" keyword
        keywords: ["earthquake", "work", "aid"]
    }
];

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
        // Determine color class based on score
        const scoreColor = news.score > 90 ? 'bg-red-500' : news.score > 70 ? 'bg-yellow-500' : 'bg-green-500';
        
        // Create the card
        const card = `
            <div class="bg-white border border-gray-200 rounded p-4">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs text-gray-500">${news.source} - ${news.date}</span>
                    <div class="flex items-center space-x-2">
                        <span class="px-2 py-0.5 text-xs font-medium text-white rounded ${scoreColor}">${news.score}</span>
                        ${news.toxicity !== 'Clean' ? `<span class="px-2 py-0.5 text-xs font-medium text-white rounded bg-red-600">Alarm</span>` : ''}
                    </div>
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">${news.title}</h3>
                <div class="flex flex-wrap gap-1 mt-2">
                    <span class="px-2 py-0.5 text-xs font-medium text-blue-800 bg-blue-100 rounded">${news.category}</span>
                    <span class="px-2 py-0.5 text-xs font-medium text-purple-800 bg-purple-100 rounded">${news.sentiment}</span>
                    <span class="px-2 py-0.5 text-xs font-medium text-red-800 bg-red-100 rounded">${news.toxicity}</span>
                </div>
                <div class="mt-2">
                    <h4 class="text-sm text-gray-700">Keywords:</h4>
                    <div class="flex flex-wrap gap-1 mt-1">
                        ${news.keywords.map(keyword => `<span class="px-2 py-0.5 text-xs text-gray-600 bg-gray-200 rounded">${keyword}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
        newsList.innerHTML += card;
    });
}

// Function to handle filtering and searching
function filterAndSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    const selectedCategory = categoryFilter.value;
    const selectedSentiment = sentimentFilter.value;

    const filteredNews = newsData.filter(news => {
        const matchesSearch = news.title.toLowerCase().includes(searchTerm) || news.keywords.some(k => k.toLowerCase().includes(searchTerm));
        const matchesCategory = !selectedCategory || news.category === selectedCategory;
        const matchesSentiment = !selectedSentiment || news.sentiment === selectedSentiment;

        return matchesSearch && matchesCategory && matchesSentiment;
    });

    renderNews(filteredNews);
}

// Event listeners to run on page load and when filters change
document.addEventListener('DOMContentLoaded', () => {
    renderNews(newsData);
});

searchInput.addEventListener('input', filterAndSearch);
categoryFilter.addEventListener('change', filterAndSearch);
sentimentFilter.addEventListener('change', filterAndSearch);
