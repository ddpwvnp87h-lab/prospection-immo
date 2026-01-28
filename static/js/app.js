// ============================================================================
// PWA - Service Worker Registration
// ============================================================================

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}

// ============================================================================
// Auto-hide flash messages
// ============================================================================

setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    });
}, 5000);

// ============================================================================
// Image error handling
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const images = document.querySelectorAll('.listing-image img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.parentElement.innerHTML = '<div class="listing-no-image">📷</div>';
        });
    });
});

// ============================================================================
// Photo gallery for listing detail
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const thumbnails = document.querySelectorAll('.photo-thumbnails img');
    const mainPhoto = document.querySelector('.photo-main img');

    if (mainPhoto && thumbnails.length > 0) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', () => {
                mainPhoto.src = thumbnail.src;
            });
        });
    }
});

// ============================================================================
// Confirm deletion
// ============================================================================

const deleteButtons = document.querySelectorAll('[data-confirm]');
deleteButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        if (!confirm(button.dataset.confirm)) {
            e.preventDefault();
        }
    });
});

// ============================================================================
// Touch gestures for mobile
// ============================================================================

let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false);

function handleSwipe() {
    const swipeThreshold = 100;
    const diff = touchStartX - touchEndX;

    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0) {
            // Swipe left - could be used for next listing
            console.log('Swipe left');
        } else {
            // Swipe right - could be used for previous listing
            console.log('Swipe right');
        }
    }
}

// ============================================================================
// iOS PWA detection and prompt
// ============================================================================

const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
const isInStandaloneMode = ('standalone' in window.navigator) && (window.navigator.standalone);

if (isIOS && !isInStandaloneMode) {
    // Could show a banner to prompt iOS users to add to home screen
    // For now, just log it
    console.log('iOS user - suggest adding to home screen');
}

// ============================================================================
// Pull to refresh (for PWA)
// ============================================================================

let pStart = { x: 0, y: 0 };
let pCurrent = { x: 0, y: 0 };

document.addEventListener('touchstart', (e) => {
    pStart.x = e.changedTouches[0].pageX;
    pStart.y = e.changedTouches[0].pageY;
}, false);

document.addEventListener('touchmove', (e) => {
    pCurrent.x = e.changedTouches[0].pageX;
    pCurrent.y = e.changedTouches[0].pageY;
}, false);

document.addEventListener('touchend', () => {
    const swipeDistance = pCurrent.y - pStart.y;

    if (window.scrollY === 0 && swipeDistance > 100) {
        // Pull to refresh - reload page
        location.reload();
    }
}, false);

// ============================================================================
// Keyboard shortcuts
// ============================================================================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
        }
    }
});

// ============================================================================
// Auto-save status changes
// ============================================================================

const statusSelects = document.querySelectorAll('.status-select');
statusSelects.forEach(select => {
    select.addEventListener('change', () => {
        // Add a loading indicator
        select.style.opacity = '0.6';
        select.disabled = true;

        // Form will submit automatically via onchange
        // After page reload, the change will be visible
    });
});

// ============================================================================
// Statistics update (for dashboard)
// ============================================================================

function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update stat cards if they exist
                const stats = data.stats;
                // This would update the DOM with new stats
                console.log('Stats updated:', stats);
            }
        })
        .catch(error => console.error('Error fetching stats:', error));
}

// Update stats every 30 seconds if on dashboard
if (window.location.pathname === '/') {
    setInterval(updateStats, 30000);
}

// ============================================================================
// Smooth scroll
// ============================================================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================================================
// Log app info
// ============================================================================

console.log('%c🏠 Prospection Immo', 'font-size: 20px; font-weight: bold; color: #4F46E5');
console.log('%cApplication web de prospection immobilière', 'color: #6B7280');
console.log('Version: 1.0.0');
