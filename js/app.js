// AgriHelper - Main Application JavaScript

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

// Authentication Manager
class AuthManager {
    constructor() {
        this.checkAuth();
    }

    checkAuth() {
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        const username = localStorage.getItem('username');

        if (isLoggedIn === 'true' && username) {
            this.showUserMenu(username);
        } else {
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

    login(email, password) {
        if (email && password) {
            const username = email.split('@')[0];
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('username', username);
            this.showUserMenu(username);
            router.navigate('home');
            return true;
        }
        return false;
    }

    register(name, email, password) {
        if (name && email && password) {
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('username', name);
            this.showUserMenu(name);
            router.navigate('home');
            return true;
        }
        return false;
    }

    logout() {
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('username');
        this.showLoginLink();
        router.navigate('home');
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
        this.mainContent.innerHTML = html;
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Attach any dynamic event listeners here
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');
        const logoutBtn = document.getElementById('logoutBtn');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                if (authManager.login(email, password)) {
                    alert('Login successful!');
                }
            });
        }

        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const name = document.getElementById('name').value;
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                if (authManager.register(name, email, password)) {
                    alert('Registration successful!');
                }
            });
        }

        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                authManager.logout();
            });
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
                    alert('Please enter a city name');
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
        this.initLoanFilters();
        this.initAccordions();
    }

    initCropFilters() {
        const searchInput = document.getElementById('cropSearch');
        const categoryButtons = document.querySelectorAll('.category-btn');
        
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterCrops());
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
        const activeCategory = document.querySelector('.category-btn.active')?.textContent || 'All';
        const cards = document.querySelectorAll('.crop-card');
        let visibleCount = 0;

        cards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const category = card.getAttribute('data-category');

            const matchesSearch = title.includes(searchValue);
            const matchesCategory = activeCategory === 'All' || category === activeCategory;

            if (matchesSearch && matchesCategory) {
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

    filterLoans() {
        const search = document.getElementById('loanSearch')?.value.toLowerCase() || '';
        const type = document.getElementById('typeFilter')?.value || 'All';
        const region = document.getElementById('regionFilter')?.value || 'All';
        const cards = document.querySelectorAll('.loan-card');

        cards.forEach(card => {
            const text = card.textContent.toLowerCase();
            const cardType = card.getAttribute('data-type');
            const cardRegion = card.getAttribute('data-region');

            const matchesSearch = text.includes(search);
            const matchesType = type === 'All' || cardType === type;
            const matchesRegion = region === 'All' || cardRegion === region;

            card.style.display = (matchesSearch && matchesType && matchesRegion) ? 'block' : 'none';
        });
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
}

// Initialize content manager
const contentManager = new ContentManager();

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    // Register routes
    router.register('home', () => contentManager.render(Pages.home()));
    router.register('crops', () => contentManager.render(Pages.crops()));
    router.register('fertilizer', () => contentManager.render(Pages.fertilizer()));
    router.register('loans', () => contentManager.render(Pages.loans()));
    router.register('weather', () => contentManager.render(Pages.weather()));
    router.register('login', () => contentManager.render(Pages.login()));
    router.register('register', () => contentManager.render(Pages.register()));

    // Crop detail routes
    router.register('crop-wheat', () => contentManager.render(Pages.cropDetail('wheat')));
    router.register('crop-maize', () => contentManager.render(Pages.cropDetail('maize')));
    router.register('crop-soybean', () => contentManager.render(Pages.cropDetail('soybean')));
    router.register('crop-sugarcane', () => contentManager.render(Pages.cropDetail('sugarcane')));
    router.register('crop-tomato', () => contentManager.render(Pages.cropDetail('tomato')));

    // Navigation click handlers
    document.querySelectorAll('[data-route]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const route = e.currentTarget.getAttribute('data-route');
            router.navigate(route);
        });
    });

    // Logout button
    document.getElementById('logoutBtn')?.addEventListener('click', () => {
        authManager.logout();
    });

    // Load initial page
    router.navigate('home');
});
