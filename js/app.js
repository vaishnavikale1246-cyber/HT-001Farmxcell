// AgriHelper - Main Application JavaScript

const uiText = (key) => window.AgriI18n?.t(key) || key;

// Router for SPA navigation
class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = 'home';
    }

    register(path, handler) {
        this.routes[path] = handler;
    }

    navigate(path) {
        if (this.routes[path]) {
            this.currentRoute = path;
            this.routes[path]();
            this.updateActiveNav(path);
            window.scrollTo(0, 0);
        }
    }

    updateActiveNav(path) {
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-route') === path) {
                link.classList.add('active');
            }
        });
    }
}

// Initialize router
const router = new Router();

const dashboardDataService = {
    async load() {
        const response = await fetch('/api/dashboard-data', {
            headers: { 'Accept': 'application/json' },
            cache: 'no-store'
        });
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || 'The server could not load the latest information.');
        }

        return data;
    }
};

const dashboardStatsService = {
    async load() {
        const response = await fetch('/api/dashboard-stats', {
            headers: { 'Accept': 'application/json' },
            cache: 'no-store'
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(data.error || 'Dashboard totals could not be loaded.');
        }
        return data;
    }
};

// Sends small, validated usage events to PostgreSQL. Tracking failures never
// interrupt the farmer's dashboard experience.
const farmerAnalytics = {
    async track(activityType, payload = {}) {
        if (window.AGRIHELPER_SESSION?.role !== 'user') return;

        try {
            await fetch('/api/farmer-activity', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ activity_type: activityType, ...payload }),
                keepalive: true
            });
        } catch (_error) {
            // Analytics are deliberately non-blocking.
        }
    }
};

window.farmerAnalytics = farmerAnalytics;

// Authentication Manager
class AuthManager {
    constructor() {
        this.checkAuth();
    }

    checkAuth() {
        const serverSession = window.AGRIHELPER_SESSION || {};
        if (serverSession.loggedIn && serverSession.username) {
            this.showUserMenu(serverSession.username);
        } else {
            localStorage.removeItem('isLoggedIn');
            localStorage.removeItem('username');
            this.showLoginLink();
        }
    }

    showUserMenu(username) {
        const loginLink = document.getElementById('loginLink');
        const userMenu = document.getElementById('userMenu');

        if (loginLink) loginLink.style.display = 'none';
        if (userMenu) {
            userMenu.style.display = 'flex';
            document.getElementById('userName').textContent = username;
        }
    }

    showLoginLink() {
        const loginLink = document.getElementById('loginLink');
        const userMenu = document.getElementById('userMenu');

        if (loginLink) loginLink.style.display = 'block';
        if (userMenu) userMenu.style.display = 'none';
    }

    logout() {
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('username');

        window.location.href = '/logout';
    }
}

// Initialize auth manager
const authManager = new AuthManager();

// Content Manager
class ContentManager {
    constructor() {
        this.mainContent = document.getElementById('mainContent');
    }

    render(html) {
        if (typeof window.stopDiseaseCamera === 'function') {
            window.stopDiseaseCamera();
            window.stopDiseaseCamera = null;
        }
        this.mainContent.innerHTML = html;
        window.AgriI18n?.apply(this.mainContent);
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Attach any dynamic event listeners here
        const logoutBtn = document.getElementById('logoutBtn');

        if (logoutBtn) {
            logoutBtn.onclick = () => {
                authManager.logout();
            };
        }

        // Weather page functionality
        const searchWeatherBtn = document.getElementById('searchWeatherBtn');
        const getCurrentLocationBtn = document.getElementById('getCurrentLocationBtn');
        const weatherLocation = document.getElementById('weatherLocation');

        if (searchWeatherBtn) {
            searchWeatherBtn.addEventListener('click', () => {
                const city = weatherLocation.value.trim();
                if (city) {
                    WeatherController.loadWeather(city);
                } else {
                    alert(uiText('weather.cityRequired'));
                }
            });
        }

        if (weatherLocation) {
            weatherLocation.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const city = weatherLocation.value.trim();
                    if (city) {
                        WeatherController.loadWeather(city);
                    }
                }
            });
        }

        if (getCurrentLocationBtn) {
            getCurrentLocationBtn.addEventListener('click', () => {
                WeatherController.getCurrentLocation();
            });
        }

        // Initialize weather if on weather page
        if (router.currentRoute === 'weather' && typeof WeatherController !== 'undefined') {
            WeatherController.init();
        }

        // Crop filter functionality
        this.initCropFilters();
        this.initFertilizerFilters();
        this.initFertilizerTracking();
        this.initLoanFilters();
        this.initLoanTracking();
        this.initAccordions();
        this.initCropDetailAccordions();
        this.initDiseaseDetection();
        if (router.currentRoute === 'calendar' && typeof CalendarController !== 'undefined') {
            CalendarController.init();
        }
    }

    initDiseaseDetection() {
        const form = document.getElementById('diseaseDetectionForm');
        const imageInput = document.getElementById('diseaseImageInput');
        if (!form || !imageInput) return;

        const preview = document.getElementById('diseasePreview');
        const previewImage = document.getElementById('diseasePreviewImage');
        const fileName = document.getElementById('diseaseFileName');
        const submitButton = document.getElementById('detectDiseaseBtn');
        const status = document.getElementById('diseaseStatus');
        const resultPanel = document.getElementById('diseaseResult');
        const openCameraButton = document.getElementById('openDiseaseCamera');
        const cameraPanel = document.getElementById('diseaseCameraPanel');
        const cameraVideo = document.getElementById('diseaseCameraVideo');
        const cameraCanvas = document.getElementById('diseaseCameraCanvas');
        const captureButton = document.getElementById('captureDiseasePhoto');
        const closeCameraButton = document.getElementById('closeDiseaseCamera');
        let previewUrl = null;
        let capturedFile = null;
        let cameraStream = null;
        let cameraRequestActive = false;

        const stopCamera = () => {
            cameraRequestActive = false;
            if (cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
                cameraStream = null;
            }
            if (cameraVideo) cameraVideo.srcObject = null;
            if (cameraPanel) cameraPanel.hidden = true;
            if (openCameraButton) {
                openCameraButton.disabled = false;
                openCameraButton.setAttribute('aria-expanded', 'false');
            }
        };

        window.stopDiseaseCamera = stopCamera;

        const clearPreview = () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
                previewUrl = null;
            }
            previewImage.removeAttribute('src');
            fileName.textContent = '';
            preview.hidden = true;
            submitButton.disabled = true;
        };

        const showPreview = (file) => {
            status.textContent = '';
            status.className = 'disease-status';
            resultPanel.hidden = true;

            if (!file) {
                clearPreview();
                return false;
            }

            if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
                clearPreview();
                status.textContent = uiText('disease.invalidType');
                status.className = 'disease-status error';
                return false;
            }

            if (file.size > 10 * 1024 * 1024) {
                clearPreview();
                status.textContent = uiText('disease.tooLarge');
                status.className = 'disease-status error';
                return false;
            }

            if (previewUrl) URL.revokeObjectURL(previewUrl);
            previewUrl = URL.createObjectURL(file);
            previewImage.src = previewUrl;
            fileName.textContent = file.name;
            preview.hidden = false;
            submitButton.disabled = false;
            return true;
        };

        imageInput.addEventListener('change', () => {
            const file = imageInput.files[0];
            capturedFile = null;
            stopCamera();
            if (!showPreview(file)) {
                imageInput.value = '';
            }
        });

        openCameraButton?.addEventListener('click', async () => {
            if (!navigator.mediaDevices?.getUserMedia) {
                status.textContent = uiText('disease.cameraUnsupported');
                status.className = 'disease-status error';
                return;
            }

            stopCamera();
            cameraRequestActive = true;
            openCameraButton.disabled = true;
            status.textContent = uiText('disease.cameraStarting');
            status.className = 'disease-status';

            try {
                const requestedStream = await navigator.mediaDevices.getUserMedia({
                    video: { facingMode: { ideal: 'environment' } },
                    audio: false
                });
                if (!cameraRequestActive || !cameraVideo.isConnected) {
                    requestedStream.getTracks().forEach(track => track.stop());
                    return;
                }
                cameraStream = requestedStream;
                cameraVideo.srcObject = cameraStream;
                cameraPanel.hidden = false;
                openCameraButton.setAttribute('aria-expanded', 'true');
                await cameraVideo.play();
                status.textContent = uiText('disease.cameraReady');
            } catch (error) {
                const requestWasActive = cameraRequestActive && cameraVideo.isConnected;
                stopCamera();
                if (!requestWasActive) return;
                status.textContent = ['NotAllowedError', 'SecurityError'].includes(error.name)
                    ? uiText('disease.cameraPermission')
                    : uiText('disease.cameraError');
                status.className = 'disease-status error';
            }
        });

        captureButton?.addEventListener('click', () => {
            if (!cameraStream || !cameraVideo.videoWidth || !cameraVideo.videoHeight) {
                status.textContent = uiText('disease.captureFailed');
                status.className = 'disease-status error';
                return;
            }

            cameraCanvas.width = cameraVideo.videoWidth;
            cameraCanvas.height = cameraVideo.videoHeight;
            cameraCanvas.getContext('2d').drawImage(
                cameraVideo,
                0,
                0,
                cameraCanvas.width,
                cameraCanvas.height
            );

            cameraCanvas.toBlob((blob) => {
                if (!blob) {
                    status.textContent = uiText('disease.captureFailed');
                    status.className = 'disease-status error';
                    return;
                }

                capturedFile = new File(
                    [blob],
                    `leaf-camera-${Date.now()}.jpg`,
                    { type: 'image/jpeg' }
                );
                imageInput.value = '';
                showPreview(capturedFile);
                stopCamera();
                status.textContent = uiText('disease.cameraCaptured');
            }, 'image/jpeg', 0.92);
        });

        closeCameraButton?.addEventListener('click', () => {
            stopCamera();
            status.textContent = '';
            status.className = 'disease-status';
        });

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const file = capturedFile || imageInput.files[0];
            if (!file) return;

            submitButton.disabled = true;
            submitButton.textContent = uiText('disease.analysing');
            status.textContent = uiText('disease.modelLoading');
            status.className = 'disease-status';
            resultPanel.hidden = true;

            try {
                const formData = new FormData();
                formData.append('image', file);

                const response = await fetch('/detect-disease', {
                    method: 'POST',
                    headers: { 'Accept': 'application/json' },
                    body: formData
                });
                const data = await response.json().catch(() => ({}));

                if (!response.ok) {
                    throw new Error(uiText('disease.failed'));
                }

                document.getElementById('detectedDisease').textContent = data.disease;
                document.getElementById('detectedCrop').textContent = `${uiText('disease.cropLabel')}: ${data.crop}`;
                document.getElementById('diseaseConfidence').textContent = `${data.confidence.toFixed(1)}%`;
                document.getElementById('confidenceBar').style.width = `${Math.min(data.confidence, 100)}%`;

                const recommendationList = document.getElementById('diseaseRecommendations');
                recommendationList.replaceChildren();
                data.recommendations.forEach((recommendation) => {
                    const item = document.createElement('li');
                    item.textContent = recommendation;
                    recommendationList.appendChild(item);
                });

                resultPanel.classList.toggle('healthy-result', data.healthy);
                resultPanel.hidden = false;
                status.textContent = uiText('disease.complete');
                resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } catch (error) {
                status.textContent = error.message === 'Failed to fetch'
                    ? uiText('disease.serverUnavailable')
                    : error.message;
                status.className = 'disease-status error';
            } finally {
                submitButton.disabled = !(capturedFile || imageInput.files[0]);
                submitButton.textContent = uiText('disease.detect');
            }
        });
    }

    initCropFilters() {
        const searchInput = document.getElementById('cropSearch');
        const seasonFilter = document.getElementById('cropSeasonFilter');
        const categoryButtons = document.querySelectorAll('.category-btn');
        let searchTimer = null;

        if (searchInput) {
            searchInput.addEventListener('input', () => {
                this.filterCrops();
                clearTimeout(searchTimer);
                const query = searchInput.value.trim();
                if (query.length >= 2) {
                    searchTimer = setTimeout(() => {
                        farmerAnalytics.track('crop_search', { details: { query } });
                    }, 700);
                }
            });
        }

        if (seasonFilter) {
            seasonFilter.addEventListener('change', () => this.filterCrops());
        }

        categoryButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                categoryButtons.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterCrops();
            });
        });
    }

    filterCrops() {
        const searchValue = document.getElementById('cropSearch')?.value.toLowerCase() || '';
        const activeCategory = document.querySelector('.category-btn.active')?.dataset.categoryValue || 'All';
        const activeSeason = document.getElementById('cropSeasonFilter')?.value || 'All';
        const cards = document.querySelectorAll('.crop-card');
        let visibleCount = 0;

        cards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const category = card.getAttribute('data-category');
            const season = card.getAttribute('data-season');

            const matchesSearch = title.includes(searchValue);
            const matchesCategory = activeCategory === 'All' || category === activeCategory;
            const matchesSeason = activeSeason === 'All' || season === activeSeason;

            if (matchesSearch && matchesCategory && matchesSeason) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        const noResult = document.getElementById('noResult');
        if (noResult) {
            noResult.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    initFertilizerFilters() {
        const searchInput = document.getElementById('fertilizerSearch');
        const typeFilter = document.getElementById('fertilizerTypeFilter');
        let searchTimer = null;

        if (searchInput) {
            searchInput.addEventListener('input', () => {
                this.filterFertilizers();
                clearTimeout(searchTimer);
                const query = searchInput.value.trim();
                if (query.length >= 2) {
                    searchTimer = setTimeout(() => {
                        farmerAnalytics.track('fertilizer_search', { details: { query } });
                    }, 700);
                }
            });
        }
        typeFilter?.addEventListener('change', () => this.filterFertilizers());
    }

    filterFertilizers() {
        const search = document.getElementById('fertilizerSearch')?.value.toLowerCase().trim() || '';
        const type = document.getElementById('fertilizerTypeFilter')?.value || 'All';
        const cards = document.querySelectorAll('.fertilizer-data-card');
        let visibleCount = 0;

        cards.forEach(card => {
            const matchesSearch = (card.dataset.search || '').includes(search);
            const matchesType = type === 'All' || card.dataset.type === type;
            const visible = matchesSearch && matchesType;
            card.style.display = visible ? 'block' : 'none';
            if (visible) visibleCount++;
        });

        const noResult = document.getElementById('noFertilizerResult');
        if (noResult) noResult.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    initFertilizerTracking() {
        const cards = document.querySelectorAll('[data-fertilizer-id]');
        if (!cards.length) return;

        if (!('IntersectionObserver' in window)) {
            cards.forEach(card => {
                card.addEventListener('click', () => {
                    farmerAnalytics.track('fertilizer_view', {
                        fertilizer_id: Number(card.dataset.fertilizerId)
                    });
                }, { once: true });
            });
            return;
        }

        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (!entry.isIntersecting || entry.intersectionRatio < 0.55) return;
                farmerAnalytics.track('fertilizer_view', {
                    fertilizer_id: Number(entry.target.dataset.fertilizerId)
                });
                observer.unobserve(entry.target);
            });
        }, { threshold: 0.55 });

        cards.forEach(card => observer.observe(card));
    }

    initLoanFilters() {
        const searchInput = document.getElementById('loanSearch');
        const typeFilter = document.getElementById('typeFilter');
        const regionFilter = document.getElementById('regionFilter');

        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterLoans());
        }
        if (typeFilter) {
            typeFilter.addEventListener('change', () => this.filterLoans());
        }
        if (regionFilter) {
            regionFilter.addEventListener('change', () => this.filterLoans());
        }
    }

    initLoanTracking() {
        document.querySelectorAll('[data-loan-id]').forEach(card => {
            card.addEventListener('click', () => {
                if (card.dataset.activityRecorded === 'true') return;
                card.dataset.activityRecorded = 'true';
                farmerAnalytics.track('loan_view', {
                    loan_id: Number(card.dataset.loanId)
                });
            });
        });
    }

    filterLoans() {
        const search = document.getElementById('loanSearch')?.value.toLowerCase() || '';
        const type = document.getElementById('typeFilter')?.value || 'All';
        const region = document.getElementById('regionFilter')?.value || 'All';
        const cards = document.querySelectorAll('.loan-card');
        let visibleCount = 0;

        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const cardType = card.getAttribute('data-type');
            const cardRegion = card.getAttribute('data-region');

            const matchesSearch = text.includes(search);
            const matchesType = type === 'All' || cardType === type;
            const matchesRegion = region === 'All' || cardRegion === region;

            const visible = matchesSearch && matchesType && matchesRegion;
            card.style.display = visible ? 'block' : 'none';
            if (visible) visibleCount++;
        });

        const noResult = document.getElementById('noLoanResult');
        if (noResult) noResult.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    initAccordions() {
        const headers = document.querySelectorAll('.accordion-header');

        headers.forEach(header => {
            header.addEventListener('click', () => {
                const content = header.nextElementSibling;
                const isOpen = content.style.maxHeight;

                document.querySelectorAll('.accordion-content').forEach(c => {
                    c.style.maxHeight = null;
                    const icon = c.previousElementSibling.querySelector('.accordion-icon');
                    if (icon) icon.textContent = '+';
                });

                if (!isOpen) {
                    content.style.maxHeight = content.scrollHeight + 'px';
                    const icon = header.querySelector('.accordion-icon');
                    if (icon) icon.textContent = '−';
                }
            });
        });
    }

    initCropDetailAccordions() {
        const headers = document.querySelectorAll('.accordion-header-detail');

        headers.forEach(header => {
            header.addEventListener('click', () => {
                const item = header.parentElement;
                const content = header.nextElementSibling;
                const isActive = item.classList.contains('active');

                // Close all accordions
                document.querySelectorAll('.accordion-item-detail').forEach(i => {
                    i.classList.remove('active');
                });

                // Open clicked accordion if it was closed
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        });
    }
}

// Initialize content manager
const contentManager = new ContentManager();

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    const renderHome = async () => {
        contentManager.render(Pages.home());
        try {
            const stats = await dashboardStatsService.load();
            if (router.currentRoute === 'home') {
                contentManager.render(Pages.home(stats));
            }
        } catch (_error) {
            // The dashboard remains usable if summary totals are unavailable.
        }
    };

    const renderLiveModule = async (routeName, moduleName, dataKey, pageRenderer) => {
        contentManager.render(Pages.dataLoading(moduleName));

        try {
            const data = await dashboardDataService.load();
            if (router.currentRoute !== routeName) return;

            if (dataKey === 'crops') {
                data.crops.forEach(crop => {
                    router.register(`crop-db-${crop.id}`, () => {
                        contentManager.render(Pages.databaseCropDetail(crop));
                    });
                });
            }

            contentManager.render(pageRenderer(data[dataKey] || []));
        } catch (error) {
            if (router.currentRoute === routeName) {
                contentManager.render(Pages.dataError(error.message));
            }
        }
    };

    // Register routes
    router.register('home', renderHome);
    router.register('crops', () => renderLiveModule('crops', 'crops', 'crops', Pages.crops));
    router.register('calendar', () => contentManager.render(Pages.calendar()));
    router.register('disease', () => contentManager.render(Pages.disease()));
    router.register('fertilizer', () => renderLiveModule('fertilizer', 'fertilizers', 'fertilizers', Pages.fertilizer));
    router.register('loans', () => renderLiveModule('loans', 'loan schemes', 'loans', Pages.loans));
    router.register('weather', () => contentManager.render(Pages.weather()));
    // Navigation click handlers - Use event delegation for dynamic content
    document.addEventListener('click', (e) => {
        const link = e.target.closest('[data-route]');
        if (link) {
            e.preventDefault();
            e.stopPropagation();
            const route = link.getAttribute('data-route');
            router.navigate(route);

            if (route.startsWith('crop-db-')) {
                farmerAnalytics.track('crop_view', { crop_id: Number(route.replace('crop-db-', '')) });
            } else if (route === 'weather') {
                farmerAnalytics.track('weather_view');
            } else if (route === 'loans') {
                farmerAnalytics.track('loan_view');
            }
        }
    });

    document.addEventListener('agrihelper:languagechange', () => {
        router.navigate(router.currentRoute || 'home');
    });

    // Load initial page
    router.navigate('home');
});


// ==================== Smooth Scroll ====================
document.addEventListener('click', (e) => {
    const target = e.target.closest('a[href^="#"]');
    // Only handle anchor links that don't have data-route attribute
    if (target && target.getAttribute('href') !== '#' && !target.hasAttribute('data-route')) {
        e.preventDefault();
        const targetId = target.getAttribute('href');
        const targetElement = document.querySelector(targetId);

        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// ==================== Scroll Animations ====================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const animateOnScroll = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe cards and sections
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card, .stat-item');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `all 0.6s ease ${index * 0.1}s`;
        animateOnScroll.observe(card);
    });
});

// ==================== Navbar Scroll Effect ====================
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
    } else {
        navbar.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
    }

    lastScroll = currentScroll;
});

// ==================== Counter Animation ====================
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = Math.round(target);
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

// Animate stat numbers when they come into view
const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
            const text = entry.target.textContent;
            const number = parseInt(text.replace(/\D/g, ''));
            if (number) {
                animateCounter(entry.target, number);
                entry.target.classList.add('counted');
            }
        }
    });
}, { threshold: 0.5 });

document.addEventListener('DOMContentLoaded', () => {
    const statNumbers = document.querySelectorAll('.stat-item h2');
    statNumbers.forEach(stat => counterObserver.observe(stat));
});

// ==================== Button Ripple Effect ====================
document.addEventListener('click', (e) => {
    const button = e.target.closest('.btn, .btn-primary, .btn-hero');
    if (button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            transform: scale(0);
            animation: ripple-animation 0.6s ease-out;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }
});

// Add ripple animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
