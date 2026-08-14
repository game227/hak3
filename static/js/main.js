/**
 * QuietSpace Tashkent — Main Interactive JS
 */

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5s
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// AI Search Quick Assistant
async function runAISearch(queryText) {
    const resultsContainer = document.getElementById('ai-results-container');
    const loadingSpinner = document.getElementById('ai-loading');
    
    if (loadingSpinner) loadingSpinner.classList.remove('d-none');
    if (resultsContainer) resultsContainer.innerHTML = '';

    try {
        const response = await fetch('/ai/api/matchmaker/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: queryText })
        });

        const data = await response.json();
        if (loadingSpinner) loadingSpinner.classList.add('d-none');

        if (data.status === 'success' && data.results.length > 0) {
            renderAIResults(data.results, resultsContainer);
        } else {
            resultsContainer.innerHTML = `
                <div class="p-4 text-center text-muted">
                    <i class="bi bi-search display-6 d-block mb-2"></i>
                    Afsuski, so‘rovingizga to‘liq mos keladigan joy topilmadi. Qidiruv parametrlarini o‘zgartirib ko‘ring.
                </div>
            `;
        }
    } catch (err) {
        if (loadingSpinner) loadingSpinner.classList.add('d-none');
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="alert alert-danger">Xatolik yuz berdi: ${err.message}</div>`;
        }
    }
}

function renderAIResults(results, container) {
    let html = '<div class="row g-3">';
    results.forEach((item, idx) => {
        const badgeClass = item.live_status === 'quiet' ? 'badge-live-quiet' : (item.live_status === 'moderate' ? 'badge-live-moderate' : 'badge-live-busy');
        html += `
            <div class="col-md-4">
                <div class="qs-card h-100 d-flex flex-column">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="${badgeClass}">${item.live_status_text}</span>
                        <span class="badge bg-purple-900 text-purple-200"><i class="bi bi-robot me-1"></i>Match #${idx + 1}</span>
                    </div>
                    <h5 class="fw-bold text-white mb-1">${item.name}</h5>
                    <p class="text-muted small mb-2"><i class="bi bi-geo-alt me-1"></i>${item.district} — ${item.category}</p>
                    
                    <div class="d-flex gap-2 my-2">
                        <span class="badge bg-blue-950 text-blue-300 border border-blue-800"><i class="bi bi-wifi me-1"></i>${item.avg_download_mbps} Mbps</span>
                        <span class="badge bg-emerald-950 text-emerald-300 border border-emerald-800"><i class="bi bi-volume-down me-1"></i>${item.current_db_level} dB</span>
                    </div>

                    <ul class="list-unstyled small text-slate-300 my-2 flex-grow-1">
                        ${item.reasons.map(r => `<li class="mb-1"><i class="bi bi-check2-circle text-emerald-400 me-1"></i>${r}</li>`).join('')}
                    </ul>

                    <div class="d-flex justify-content-between align-items-center mt-3 pt-2 border-top border-slate-800">
                        <span class="fw-bold text-emerald-400">${parseInt(item.hourly_price).toLocaleString()} so‘m/soat</span>
                        <a href="${item.url}" class="btn btn-sm btn-qs-primary">Batafsil & Bron</a>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}
