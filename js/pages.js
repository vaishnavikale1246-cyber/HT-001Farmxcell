// AgriHelper - Page Templates

const Pages = {
    home: () => `
        <header class="hero">
            <h1>Cultivating Tomorrow, <span>Today</span></h1>
            <p>Your trusted partner in modern agriculture. Access crop info, fertilizer recommendations, and weather updates all in one place.</p>
        </header>

        <div class="container">
            <div class="features-grid">
                <a href="#" data-route="crops" class="card">
                    <div class="icon-box">🌾</div>
                    <h3>Crop Information</h3>
                    <p>Explore detailed crop guides and growth durations.</p>
                </a>

                <a href="#" data-route="fertilizer" class="card">
                    <div class="icon-box">💧</div>
                    <h3>Fertilizer</h3>
                    <p>Get nutrient recommendations for maximum yield.</p>
                </a>

                <a href="#" data-route="loans" class="card">
                    <div class="icon-box">🏛️</div>
                    <h3>Gov Loans</h3>
                    <p>Find financial support and government schemes.</p>
                </a>

                <a href="#" data-route="weather" class="card">
                    <div class="icon-box">🌤️</div>
                    <h3>Weather</h3>
                    <p>Check local forecasts and agricultural alerts.</p>
                </a>
            </div>
        </div>

        <section class="stats-bar">
            <div class="stat-item"><h2>50+</h2><p>Crop Varieties</p></div>
            <div class="stat-item"><h2>100+</h2><p>Fertilizer Guides</p></div>
            <div class="stat-item"><h2>20+</h2><p>Loan Schemes</p></div>
            <div class="stat-item"><h2>24/7</h2><p>Weather Updates</p></div>
        </section>
    `,

    crops: () => `
        <div class="container">
            <h1>Crop Information</h1>
            <p class="description">
                Explore detailed information about various crops, their growing conditions, and best practices.
            </p>

            <div class="filters">
                <div class="search-box">
                    <input type="text" id="cropSearch" placeholder="Search crops..." />
                </div>

                <div class="category-buttons">
                    <button class="category-btn active">All</button>
                    <button class="category-btn">Cereal</button>
                    <button class="category-btn">Vegetable</button>
                    <button class="category-btn">Pulse</button>
                    <button class="category-btn">Cash Crop</button>
                </div>
            </div>

            <div class="grid">
                ${CropData.map(crop => `
                    <div class="crop-card card" data-category="${crop.category}">
                        <div class="card-image">${crop.icon}</div>
                        <div class="card-content">
                            <h3>${crop.name}</h3>
                            <span class="badge">${crop.category}</span>
                            <p>${crop.description}</p>
                            <div class="season">Season: ${crop.season}</div>
                            <a href="#" data-route="crop-${crop.id}" class="btn">View Details →</a>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div class="empty" id="noResult" style="display: none;">No crops found.</div>
        </div>
    `,

    fertilizer: () => `
        <div class="container">
            <h1>Fertilizer Recommendations</h1>
            <p class="description">
                Learn about different fertilizers, their application methods, and crop-specific recommendations.
            </p>

            <h2>Common Fertilizers</h2>
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <h3>Urea</h3>
                        <span class="badge">Nitrogen Fertilizer</span>
                    </div>
                    <div class="card-content">
                        <p>Urea is a widely used nitrogen fertilizer that promotes vegetative growth.</p>
                        <div class="info-row"><span class="info-label">Nutrients:</span> 46% Nitrogen</div>
                        <div class="info-row"><span class="info-label">Dosage:</span> 100 kg per hectare</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3>DAP</h3>
                        <span class="badge">Phosphatic Fertilizer</span>
                    </div>
                    <div class="card-content">
                        <p>Diammonium phosphate supplies both nitrogen and phosphorus.</p>
                        <div class="info-row"><span class="info-label">Nutrients:</span> 18% N, 46% P</div>
                        <div class="info-row"><span class="info-label">Dosage:</span> 50 kg per hectare</div>
                    </div>
                </div>
            </div>

            <h2 style="margin-top: 40px;">Application Guide</h2>
            <div class="accordion-item">
                <div class="accordion-header">
                    Timing of Fertilizer Application 
                    <span class="accordion-icon">+</span>
                </div>
                <div class="accordion-content">
                    <p>Proper timing ensures maximum nutrient uptake.</p>
                    <ul>
                        <li>Basal application at sowing</li>
                        <li>Top dressing during growth</li>
                        <li>Foliar application for deficiencies</li>
                        <li>Critical stages: flowering & grain filling</li>
                    </ul>
                </div>
            </div>

            <div class="accordion-item">
                <div class="accordion-header">
                    Correct Dosage Guidelines 
                    <span class="accordion-icon">+</span>
                </div>
                <div class="accordion-content">
                    <p>Correct dosage prevents waste and damage.</p>
                    <ul>
                        <li>Conduct soil testing</li>
                        <li>Follow crop requirements</li>
                        <li>Use split application</li>
                        <li>Follow local guidelines</li>
                    </ul>
                </div>
            </div>

            <h2 style="margin-top: 40px;">Crop-Specific Fertilizer Pairing</h2>
            <div class="grid-4">
                <div class="crop-card"><div class="crop-title">Wheat</div><div class="small-text">Recommended: Urea, DAP</div></div>
                <div class="crop-card"><div class="crop-title">Rice</div><div class="small-text">Recommended: Urea</div></div>
                <div class="crop-card"><div class="crop-title">Maize</div><div class="small-text">Recommended: DAP</div></div>
                <div class="crop-card"><div class="crop-title">Tomato</div><div class="small-text">Recommended: Urea, Compost</div></div>
            </div>
        </div>
    `,

    loans: () => `
        <div class="container">
            <h1>Government Loan Schemes</h1>
            <p class="description">
                Explore various government schemes and financial assistance programs available for farmers.
            </p>

            <div class="filters">
                <div class="search-box">
                    <input type="text" id="loanSearch" placeholder="Search schemes...">
                </div>

                <select id="typeFilter">
                    <option value="All">All Types</option>
                    <option value="Subsidy">Subsidy</option>
                    <option value="Crop Loan">Crop Loan</option>
                </select>

                <select id="regionFilter">
                    <option value="All">All Regions</option>
                    <option value="National">National</option>
                    <option value="State">State</option>
                </select>
            </div>

            <div class="grid">
                ${LoanData.map(loan => `
                    <div class="loan-card card" data-type="${loan.type}" data-region="${loan.region}">
                        <div class="card-header">
                            <div class="badge">${loan.type}</div>
                            <h3>${loan.name}</h3>
                            <div class="short-name">${loan.shortName}</div>
                        </div>
                        <div class="card-content">
                            <p>${loan.description}</p>
                            <div class="stats">
                                <div>Interest: <span>${loan.interest}</span></div>
                                <div>Max: <span>${loan.maxAmount}</span></div>
                            </div>
                            <ul class="benefits">
                                ${loan.benefits.map(b => `<li>${b}</li>`).join('')}
                            </ul>
                            <a href="#" class="btn">Learn More →</a>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `,

    weather: () => `
        <div class="container">
            <h1>Weather Dashboard</h1>
            <p class="description">
                Get real-time weather updates, forecasts, and agricultural alerts for your location.
            </p>

            <div class="search-bar">
                <input type="text" id="weatherLocation" placeholder="Enter city name (e.g., Delhi, Mumbai)...">
                <button class="btn-primary" id="searchWeatherBtn">Search</button>
                <button class="btn-primary" id="getCurrentLocationBtn" style="margin-left: 10px;">📍 Use My Location</button>
            </div>

            <div id="weatherLoading" style="display: none; text-align: center; padding: 40px;">
                <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #2e7d32; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                <p style="margin-top: 20px; color: #666;">Loading weather data...</p>
            </div>

            <div id="weatherError" style="display: none; text-align: center; padding: 40px;">
                <p style="color: #ef4444; font-size: 1.1rem;">⚠️ Unable to fetch weather data. Please try again.</p>
            </div>

            <div id="weatherContent" class="weather-grid">
                <div class="weather-main">
                    <div class="card">
                        <h3>Current Weather - <span id="cityName">Delhi</span></h3>
                        <div class="current-weather">
                            <div>
                                <div class="temperature" id="currentTemp">--°C</div>
                                <div id="weatherDesc">Loading...</div>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 10px;">
                                    Feels like: <span id="feelsLike">--°C</span>
                                </div>
                            </div>
                            <div class="weather-stats">
                                <div>Humidity<br><span id="humidity">--%</span></div>
                                <div>Wind<br><span id="windSpeed">-- km/h</span></div>
                                <div>Pressure<br><span id="pressure">-- hPa</span></div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <h3>5-Day Forecast</h3>
                        <div class="forecast-grid" id="forecastContainer">
                            <div class="forecast-item">Loading...</div>
                        </div>
                    </div>
                </div>

                <div class="weather-sidebar">
                    <div class="card">
                        <h3>Agricultural Alerts</h3>
                        <div id="agricAlerts">
                            <div class="alert low">
                                <strong>Loading...</strong><br>
                                Fetching agricultural alerts...
                            </div>
                        </div>
                    </div>

                    <div class="card tips">
                        <h3>Weather Tips for Farmers</h3>
                        <ul>
                            <li>Monitor weather forecasts before irrigation.</li>
                            <li>Plan spraying activities during calm weather.</li>
                            <li>Protect crops from frost when temperatures drop.</li>
                            <li>Harvest during dry spells to prevent crop damage.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `,

    login: () => `
        <div class="auth-container">
            <div class="auth-card">
                <h2>Sign In</h2>
                <form id="loginForm">
                    <input type="email" id="email" placeholder="Email Address" required>
                    <input type="password" id="password" placeholder="Password" required>
                    <button type="submit" class="btn-primary">Login</button>
                </form>
                <div class="auth-links">
                    <p>Don't have an account? <a href="#" data-route="register">Sign Up</a></p>
                </div>
            </div>
        </div>
    `,

    register: () => `
        <div class="auth-container">
            <div class="auth-card">
                <h2>Create Account</h2>
                <form id="registerForm">
                    <input type="text" id="name" placeholder="Full Name" required>
                    <input type="email" id="email" placeholder="Email Address" required>
                    <input type="password" id="password" placeholder="Password" required>
                    <button type="submit" class="btn-primary">Register</button>
                </form>
                <div class="auth-links">
                    <p>Already have an account? <a href="#" data-route="login">Sign In</a></p>
                </div>
            </div>
        </div>
    `,

    cropDetail: (cropId) => {
        const crop = CropData.find(c => c.id === cropId);
        if (!crop) return '<div class="container"><h1>Crop not found</h1></div>';

        return `
            <div class="container">
                <div class="crop-header">
                    <h1>${crop.icon} ${crop.name}</h1>
                    <span class="badge">${crop.category}</span>
                    <p>${crop.fullDescription || crop.description}</p>
                </div>

                <div class="info-grid">
                    <div class="info-card"><h3>Season</h3><p>${crop.season}</p></div>
                    <div class="info-card"><h3>Water Requirement</h3><p>${crop.water}</p></div>
                    <div class="info-card"><h3>Soil Type</h3><p>${crop.soil}</p></div>
                    <div class="info-card"><h3>Growth Duration</h3><p>${crop.duration}</p></div>
                    <div class="info-card"><h3>Expected Yield</h3><p>${crop.yield}</p></div>
                </div>

                <div class="section">
                    <h2>Common Diseases</h2>
                    <div class="list">
                        <ul>
                            ${crop.diseases.map(d => `<li>${d}</li>`).join('')}
                        </ul>
                    </div>
                </div>

                <div class="section">
                    <h2>Best Practices</h2>
                    <div class="list">
                        <ul>
                            ${crop.practices.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    </div>
                </div>

                <div class="section">
                    <h2>Related Resources</h2>
                    <div class="resources">
                        <a href="#" data-route="fertilizer" class="btn-primary">Fertilizer Recommendations</a>
                        <a href="#" data-route="weather" class="btn-primary">Weather Forecast</a>
                        <a href="#" data-route="loans" class="btn-primary">Government Schemes</a>
                    </div>
                </div>

                <a href="#" data-route="crops" class="back-btn">← Back to Crop List</a>
            </div>
        `;
    }
};
