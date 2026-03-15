document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendation-form');
    const queryInput = document.getElementById('query-input');
    const loadingState = document.getElementById('loading-state');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const resultsContainer = document.getElementById('results-container');
    const searchBtn = document.getElementById('search-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const query = queryInput.value.trim();
        if (!query) return;

        // Reset UI
        resultsContainer.innerHTML = '';
        resultsContainer.classList.add('hidden');
        errorMessage.classList.add('hidden');
        loadingState.classList.remove('hidden');
        searchBtn.disabled = true;
        searchBtn.style.opacity = '0.7';

        try {
            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Server responded with an error');
            }

            renderGames(data.recommendations);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            errorText.textContent = error.message;
            errorMessage.classList.remove('hidden');
        } finally {
            loadingState.classList.add('hidden');
            searchBtn.disabled = false;
            searchBtn.style.opacity = '1';
        }
    });

    function renderGames(games) {
        if (!games || games.length === 0) {
            errorText.textContent = "No recommendations found. Try a different query.";
            errorMessage.classList.remove('hidden');
            return;
        }

        games.forEach((game, index) => {
            const card = document.createElement('div');
            card.className = 'game-card glass-panel';
            card.style.animationDelay = `${index * 0.15}s`;

            // Default image if Steam API didn't return one
            const imageUrl = game.image_url || 'https://via.placeholder.com/400x200/21262d/8b949e?text=' + encodeURIComponent(game.title);

            // Generate genre tags
            let genresHtml = '';
            if (game.genres && game.genres.length > 0) {
                genresHtml = `<div class="card-genres">
                    ${game.genres.slice(0, 3).map(g => `<span class="genre-badge">${g}</span>`).join('')}
                </div>`;
            }

            // Create Steam link
            let actionHtml = '';
            if (game.steam_url) {
                actionHtml = `<a href="${game.steam_url}" target="_blank" rel="noopener noreferrer" class="card-action">
                    <i class="fa-brands fa-steam"></i> View on Steam
                </a>`;
            }

            card.innerHTML = `
                <div class="card-image" style="background-image: url('${imageUrl}')">
                    ${game.price ? `<div class="price-tag">${game.price}</div>` : ''}
                </div>
                <div class="card-content">
                    <h3 class="card-title">${game.title}</h3>
                    <p class="card-reason">${game.reason}</p>
                    ${genresHtml}
                    ${actionHtml}
                </div>
            `;

            resultsContainer.appendChild(card);
        });

        resultsContainer.classList.remove('hidden');
    }
});
