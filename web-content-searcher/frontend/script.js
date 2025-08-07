document.addEventListener('DOMContentLoaded', () => {
    const dashboard = document.getElementById('news-dashboard');
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter');
    const importanceSlider = document.getElementById('importance-slider');
    const importanceValue = document.getElementById('importance-value');
    const sourceFilter = document.getElementById('source-filter');

    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close-btn');

    let allNews = [];

    // Verileri yükleme fonksiyonu
    async function loadNewsData() {
        // Bu kısım, bir API'den veya statik bir dosyadan veri çekecek
        // Örneğin:
        const response = await fetch('news_data.json');
        allNews = await response.json();
        renderNews(allNews);
        populateFilters(allNews);
    }

    // Haberleri ekrana basma fonksiyonu
    function renderNews(newsToDisplay) {
        dashboard.innerHTML = '';
        newsToDisplay.forEach(news => {
            const card = document.createElement('div');
            card.className = 'news-card';
            card.innerHTML = `
                <h2>${news.title}</h2>
                <p class="source">Kaynak: ${news.source}</p>
                <p class="date">Tarih: ${news.date}</p>
                <div class="importance-score" style="background-color: ${getScoreColor(news.importance)};">${news.importance}</div>
                <p class="summary">${news.summary}</p>
                <button class="details-btn">Detaylar</button>
            `;
            card.querySelector('.details-btn').addEventListener('click', () => showDetails(news));
            dashboard.appendChild(card);
        });
    }

    // Filtreleri doldurma fonksiyonu
    function populateFilters(newsData) {
        // Benzersiz kategorileri ve kaynakları bulup filtre seçeneklerini oluşturur
        // Bu kısım projenizin detaylarına göre doldurulmalıdır.
    }

    // Filtreleme mantığı
    function filterNews() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedCategory = categoryFilter.value;
        const minImportance = importanceSlider.value;
        const selectedSource = sourceFilter.value;

        const filteredNews = allNews.filter(news => {
            const matchesSearch = news.title.toLowerCase().includes(searchTerm) || news.content.toLowerCase().includes(searchTerm);
            const matchesCategory = selectedCategory === "" || news.category === selectedCategory;
            const matchesImportance = news.importance >= minImportance;
            const matchesSource = selectedSource === "" || news.source === selectedSource;

            return matchesSearch && matchesCategory && matchesImportance && matchesSource;
        });

        renderNews(filteredNews);
    }

    // Detayları gösteren modal
    function showDetails(news) {
        // Modal içeriğini doldurur
        document.getElementById('modal-title').textContent = news.title;
        // Diğer içerik de bu şekilde doldurulacak...
        modal.style.display = 'block';
    }

    // Olay dinleyicileri
    searchInput.addEventListener('input', filterNews);
    categoryFilter.addEventListener('change', filterNews);
    importanceSlider.addEventListener('input', () => {
        importanceValue.textContent = `${importanceSlider.value}+`;
        filterNews();
    });
    sourceFilter.addEventListener('change', filterNews);

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Başlangıçta verileri yükle
    loadNewsData();
});
