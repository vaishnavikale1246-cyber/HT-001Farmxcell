// AgriHelper - Page Templates

const escapeDashboardText = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

const tr = (key) => window.AgriI18n?.t(key) || key;

const splitDashboardBenefits = (value) => {
    if (Array.isArray(value)) return value;
    return String(value ?? '')
        .split(/\r?\n|;/)
        .map(item => item.trim())
        .filter(Boolean);
};

const getCropIcon = (crop = {}) => {
    const name = String(crop.name || '').toLowerCase();
    const category = String(crop.category || '').toLowerCase();
    const namedIcons = [
        [['maize', 'corn'], '&#127805;'],
        [['tomato'], '&#127813;'],
        [['potato'], '&#129364;'],
        [['onion'], '&#129477;'],
        [['chilli', 'pepper'], '&#127798;'],
        [['mango'], '&#129389;'],
        [['banana'], '&#127820;'],
        [['grape'], '&#127815;'],
        [['orange', 'citrus'], '&#127818;'],
        [['coconut'], '&#129381;'],
        [['coffee'], '&#9749;'],
        [['wheat', 'rice', 'barley', 'millet'], '&#127806;']
    ];
    const match = namedIcons.find(([names]) => names.some(item => name.includes(item)));
    if (match) return match[1];
    if (category.includes('fruit')) return '&#127822;';
    if (category.includes('vegetable')) return '&#129388;';
    if (category.includes('spice')) return '&#127807;';
    return '&#127793;';
};

const getFertilizerIcon = (fertilizer = {}) => {
    const text = `${fertilizer.name || ''} ${fertilizer.type || ''}`.toLowerCase();
    if (text.includes('organic') || text.includes('compost') || text.includes('manure')) return '&#127807;';
    if (text.includes('bio')) return '&#129516;';
    if (text.includes('liquid') || text.includes('foliar')) return '&#128167;';
    return '&#129514;';
};

const Pages = {
    home: (stats = {}) => `
        <header class="hero">
            <h1>${tr('home.cultivating')} <span>${tr('home.today')}</span></h1>
            <p>${tr('home.intro')}</p>
        </header>

        <div class="container">
            <div class="features-grid">
                <a href="#" data-route="crops" class="card">
                    <div class="icon-box" aria-hidden="true">&#127806;</div>
                    <h3>${tr('home.crop')}</h3>
                    <p>${tr('home.cropDesc')}</p>
                </a>

                <a href="#" data-route="fertilizer" class="card">
                    <div class="icon-box" aria-hidden="true">&#129514;</div>
                    <h3>${tr('home.fertilizer')}</h3>
                    <p>${tr('home.fertilizerDesc')}</p>
                </a>

                <a href="#" data-route="loans" class="card">
                    <div class="icon-box" aria-hidden="true">&#8377;</div>
                    <h3>${tr('home.loans')}</h3>
                    <p>${tr('home.loansDesc')}</p>
                </a>

                <a href="#" data-route="weather" class="card">
                    <div class="icon-box" aria-hidden="true">&#127780;</div>
                    <h3>${tr('home.weather')}</h3>
                    <p>${tr('home.weatherDesc')}</p>
                </a>

                <a href="#" data-route="disease" class="card">
                    <div class="icon-box">&#128269;</div>
                    <h3>${tr('home.disease')}</h3>
                    <p>${tr('home.diseaseDesc')}</p>
                </a>

                <a href="#" data-route="calendar" class="card smart-calendar-home-card">
                    <div class="icon-box">&#128197;</div>
                    <h3>${tr('home.calendar')}</h3>
                    <p>${tr('home.calendarDesc')}</p>
                </a>
            </div>
        </div>

        <section class="stats-bar">
            <div class="stat-item"><h2>${Number.isFinite(Number(stats.crops)) ? Number(stats.crops) : '--'}</h2><p>${tr('home.cropCount')}</p></div>
            <div class="stat-item"><h2>${Number.isFinite(Number(stats.fertilizers)) ? Number(stats.fertilizers) : '--'}</h2><p>${tr('home.fertilizerCount')}</p></div>
            <div class="stat-item"><h2>${Number.isFinite(Number(stats.loans)) ? Number(stats.loans) : '--'}</h2><p>${tr('home.loanCount')}</p></div>
            <div class="stat-item"><h2>24/7</h2><p>${tr('home.weatherCount')}</p></div>
        </section>
    `,

    calendar: () => `
        <div class="container smart-calendar-page">
            <header class="calendar-hero">
                <div>
                    <span class="calendar-eyebrow">${tr('calendar.eyebrow')}</span>
                    <h1>${tr('calendar.title')}</h1>
                    <p>${tr('calendar.desc')}</p>
                </div>
                <div class="calendar-live-context">
                    <span>${tr('calendar.location')}</span>
                    <strong id="calendarLocation">${tr('calendar.loadingLocation')}</strong>
                    <small>${tr('calendar.locationNote')}</small>
                </div>
            </header>

            <section class="calendar-toolbar" aria-label="Calendar crop selection">
                <label for="calendarCropSelect">
                    ${tr('calendar.choose')}
                    <select id="calendarCropSelect" disabled>
                        <option>${tr('calendar.loadingPlans')}</option>
                    </select>
                </label>
                <div class="calendar-auto-note">
                    <strong>${tr('calendar.preplanned')}</strong>
                    <span>${tr('calendar.autoNote')}</span>
                </div>
            </section>

            <div id="calendarStatus" class="calendar-status" role="status">${tr('calendar.loading')}</div>
            <div id="calendarContent" hidden>
                <section id="calendarSummary" class="calendar-summary"></section>
                <section id="calendarWeatherAlert" class="calendar-weather-alert"></section>
                <section id="plantThisMonth" class="plant-this-month"></section>
                <section id="calendarMonths" class="calendar-month-grid"></section>
                <section id="calendarHistory" class="calendar-history"></section>
            </div>
        </div>
    `,

    disease: () => `
        <div class="container disease-detection-page">
            <div class="disease-page-heading">
                <span class="eyebrow">${tr('disease.eyebrow')}</span>
                <h1>${tr('disease.title')}</h1>
                <p class="description">
                    ${tr('disease.desc')}
                </p>
            </div>

            <div class="disease-detection-layout">
                <form id="diseaseDetectionForm" class="disease-upload-card" enctype="multipart/form-data">
                    <label class="disease-drop-zone" for="diseaseImageInput">
                        <span class="upload-symbol" aria-hidden="true">&#128247;</span>
                        <strong>${tr('disease.choose')}</strong>
                        <span>${tr('disease.formats')}</span>
                          <input
                              type="file"
                              id="diseaseImageInput"
                              name="image"
                              accept="image/jpeg,image/png,image/webp"
                              capture="environment"
                          >
                      </label>

                      <div class="disease-input-divider" aria-hidden="true">
                          <span>${tr('disease.or')}</span>
                      </div>

                      <button
                          id="openDiseaseCamera"
                          type="button"
                          class="disease-camera-btn"
                          aria-controls="diseaseCameraPanel"
                          aria-expanded="false"
                      >
                          <span aria-hidden="true">&#128247;</span>
                          ${tr('disease.openCamera')}
                      </button>

                      <div id="diseaseCameraPanel" class="disease-camera-panel" hidden>
                          <video
                              id="diseaseCameraVideo"
                              autoplay
                              muted
                              playsinline
                              aria-label="${tr('disease.cameraPreview')}"
                          ></video>
                          <canvas id="diseaseCameraCanvas" hidden></canvas>
                          <div class="disease-camera-actions">
                              <button id="captureDiseasePhoto" type="button" class="capture-disease-photo-btn">
                                  ${tr('disease.capture')}
                              </button>
                              <button id="closeDiseaseCamera" type="button" class="close-disease-camera-btn">
                                  ${tr('disease.closeCamera')}
                              </button>
                          </div>
                      </div>

                      <div id="diseasePreview" class="disease-preview" hidden>
                        <img id="diseasePreviewImage" alt="${tr('disease.previewAlt')}">
                        <p id="diseaseFileName"></p>
                    </div>

                    <button id="detectDiseaseBtn" type="submit" class="detect-disease-btn" disabled>
                        ${tr('disease.detect')}
                    </button>
                    <p id="diseaseStatus" class="disease-status" role="status" aria-live="polite"></p>
                </form>

                <aside class="disease-help-card">
                    <h2>${tr('disease.tips')}</h2>
                    <ul>
                        <li>${tr('disease.tip1')}</li>
                        <li>${tr('disease.tip2')}</li>
                        <li>${tr('disease.tip3')}</li>
                    </ul>
                    <p class="disease-note">
                        ${tr('disease.note')}
                    </p>
                </aside>
            </div>

            <section id="diseaseResult" class="disease-result-panel" aria-live="polite" hidden>
                <div class="result-summary">
                    <div>
                        <span class="result-label">${tr('disease.prediction')}</span>
                        <h2 id="detectedDisease">--</h2>
                        <p id="detectedCrop"></p>
                    </div>
                    <div class="confidence-box">
                        <span>${tr('disease.confidence')}</span>
                        <strong id="diseaseConfidence">--%</strong>
                    </div>
                </div>
                <div class="confidence-track" aria-hidden="true">
                    <span id="confidenceBar"></span>
                </div>
                <div class="result-guidance">
                    <h3>${tr('disease.nextSteps')}</h3>
                    <ul id="diseaseRecommendations"></ul>
                </div>
            </section>
        </div>
    `,

    crops: (crops = []) => `
        <div class="container">
            <h1>${tr('crop.title')}</h1>
            <p class="description">
                ${tr('crop.desc')}
            </p>

            <div class="filters">
                <div class="search-box">
                    <input type="text" id="cropSearch" placeholder="${tr('crop.search')}" />
                </div>

                <div class="category-buttons">
                    ${[tr('crop.all'), ...new Set(crops.map(crop => crop.category).filter(Boolean))].map((category, index) => `
                        <button class="category-btn ${index === 0 ? 'active' : ''}"
                                data-category-value="${index === 0 ? 'All' : escapeDashboardText(category)}">${escapeDashboardText(category)}</button>
                    `).join('')}
                </div>

                <select id="cropSeasonFilter" aria-label="Filter crops by season">
                    <option value="All">${tr('crop.allSeasons')}</option>
                    ${[...new Set(crops.map(crop => crop.season).filter(Boolean))].map(season => `
                        <option value="${escapeDashboardText(season)}">${escapeDashboardText(season)}</option>
                    `).join('')}
                </select>
            </div>

            <div class="grid">
                ${crops.length ? crops.map(crop => `
                    <div class="crop-card card" data-category="${escapeDashboardText(crop.category)}" data-season="${escapeDashboardText(crop.season)}">
                        <div class="card-image crop-card-visual" aria-hidden="true">${getCropIcon(crop)}</div>
                        <div class="card-content">
                            <h3>${escapeDashboardText(crop.name)}</h3>
                            <span class="badge">${escapeDashboardText(crop.category)}</span>
                            <p><em>${escapeDashboardText(crop.scientificName)}</em></p>
                            <div class="season">${tr('crop.season')}: ${escapeDashboardText(crop.season)}</div>
                            <div class="season">${tr('crop.duration')}: ${escapeDashboardText(crop.duration)}</div>
                            <a href="#" data-route="crop-db-${Number(crop.id)}" class="btn btn-view-details">${tr('crop.view')}</a>
                        </div>
                    </div>
                `).join('') : `<div class="empty dashboard-empty">${tr('crop.empty')}</div>`}
            </div>

            <div class="empty" id="noResult" style="display: none;">${tr('crop.none')}</div>
        </div>
    `,

    fertilizer: (fertilizers = []) => `
        <div class="container">
            <h1>${tr('fert.title')}</h1>
            <p class="description">
                ${tr('fert.desc')}
            </p>

            <div class="filters fertilizer-filters">
                <div class="search-box">
                    <input type="text" id="fertilizerSearch" placeholder="${tr('fert.search')}" />
                </div>
                <select id="fertilizerTypeFilter" aria-label="Filter fertilizers by type">
                    <option value="All">${tr('common.allTypes')}</option>
                    ${[...new Set(fertilizers.map(item => item.type).filter(Boolean))].map(type => `
                        <option value="${escapeDashboardText(type)}">${escapeDashboardText(type)}</option>
                    `).join('')}
                </select>
            </div>

            <h2>${tr('fert.common')}</h2>
            <div class="grid-2">
                ${fertilizers.length ? fertilizers.map(fertilizer => `
                    <div class="card fertilizer-data-card"
                         data-fertilizer-id="${Number(fertilizer.id)}"
                         data-type="${escapeDashboardText(fertilizer.type)}"
                         data-search="${escapeDashboardText(`${fertilizer.name} ${fertilizer.nutrients}`.toLowerCase())}">
                        <div class="fertilizer-card-visual" aria-hidden="true">${getFertilizerIcon(fertilizer)}</div>
                        <div class="card-header">
                            <h3>${escapeDashboardText(fertilizer.name)}</h3>
                            <span class="badge">${escapeDashboardText(fertilizer.type)}</span>
                        </div>
                        <div class="card-content">
                            <p>${escapeDashboardText(fertilizer.description)}</p>
                            <div class="info-row"><span class="info-label">${tr('fert.nutrients')}:</span> ${escapeDashboardText(fertilizer.nutrients)}</div>
                            <div class="info-row"><span class="info-label">${tr('fert.dosage')}:</span> ${escapeDashboardText(fertilizer.dosage)}</div>
                        </div>
                    </div>
                `).join('') : `<div class="empty dashboard-empty">${tr('fert.empty')}</div>`}
            </div>
            <div class="empty" id="noFertilizerResult" style="display: none;">${tr('fert.none')}</div>

            <h2 style="margin-top: 40px;">${tr('fert.guide')}</h2>
            <div class="accordion-item">
                <div class="accordion-header">
                    ${tr('fert.timing')}
                    <span class="accordion-icon">+</span>
                </div>
                <div class="accordion-content">
                    <p>${tr('fert.timingIntro')}</p>
                    <ul>
                        <li>${tr('fert.timing1')}</li>
                        <li>${tr('fert.timing2')}</li>
                        <li>${tr('fert.timing3')}</li>
                        <li>${tr('fert.timing4')}</li>
                    </ul>
                </div>
            </div>

            <div class="accordion-item">
                <div class="accordion-header">
                    ${tr('fert.dosageGuide')}
                    <span class="accordion-icon">+</span>
                </div>
                <div class="accordion-content">
                    <p>${tr('fert.dosageIntro')}</p>
                    <ul>
                        <li>${tr('fert.dosage1')}</li>
                        <li>${tr('fert.dosage2')}</li>
                        <li>${tr('fert.dosage3')}</li>
                        <li>${tr('fert.dosage4')}</li>
                    </ul>
                </div>
            </div>

        </div>
    `,

    loans: (loans = []) => `
        <div class="container">
            <h1>${tr('loan.title')}</h1>
            <p class="description">
                ${tr('loan.desc')}
            </p>

            <div class="filters">
                <div class="search-box">
                    <input type="text" id="loanSearch" placeholder="${tr('loan.search')}">
                </div>

                <select id="typeFilter">
                    <option value="All">${tr('common.allTypes')}</option>
                    ${[...new Set(loans.map(loan => loan.type).filter(Boolean))].map(type => `
                        <option value="${escapeDashboardText(type)}">${escapeDashboardText(type)}</option>
                    `).join('')}
                </select>

                <select id="regionFilter">
                    <option value="All">${tr('loan.allRegions')}</option>
                    ${[...new Set(loans.map(loan => loan.region).filter(Boolean))].map(region => `
                        <option value="${escapeDashboardText(region)}">${escapeDashboardText(region)}</option>
                    `).join('')}
                </select>
            </div>

            <div class="grid">
                ${loans.length ? loans.map(loan => `
                    <div class="loan-card card" data-loan-id="${Number(loan.id)}" data-type="${escapeDashboardText(loan.type)}" data-region="${escapeDashboardText(loan.region)}">
                        <div class="loan-card-icon" aria-hidden="true">&#8377;</div>
                        <div class="card-header">
                            <div class="badge">${escapeDashboardText(loan.type)}</div>
                            <h3>${escapeDashboardText(loan.name)}</h3>
                            <div class="short-name">${escapeDashboardText(loan.shortName)}</div>
                        </div>
                        <div class="card-content">
                            <p>${escapeDashboardText(loan.description)}</p>
                            <div class="stats">
                                <div>${tr('loan.interest')}: <span>${escapeDashboardText(loan.interest)}</span></div>
                                <div>${tr('loan.maximum')}: <span>${escapeDashboardText(loan.maxAmount)}</span></div>
                            </div>
                            <ul class="benefits">
                                ${splitDashboardBenefits(loan.benefits).map(benefit => `<li>${escapeDashboardText(benefit)}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `).join('') : `<div class="empty dashboard-empty">${tr('loan.empty')}</div>`}
            </div>
            <div class="empty" id="noLoanResult" style="display: none;">${tr('loan.none')}</div>
        </div>
    `,

    weather: () => `
        <div class="container">
            <h1>${tr('weather.title')}</h1>
            <p class="description">
                ${tr('weather.desc')}
            </p>

            <div class="search-bar">
                <input type="text" id="weatherLocation" placeholder="${tr('weather.city')}">
                <button class="btn-primary" id="searchWeatherBtn">${tr('weather.search')}</button>
                <button class="btn-primary" id="getCurrentLocationBtn" style="margin-left: 10px;">&#128205; ${tr('weather.location')}</button>
            </div>

            <div id="weatherLoading" style="display: none; text-align: center; padding: 40px;">
                <div class="spinner" style="border: 4px solid #f3f3f3; border-top: 4px solid #2e7d32; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                <p style="margin-top: 20px; color: #666;">${tr('weather.loading')}</p>
            </div>

            <div id="weatherError" style="display: none; text-align: center; padding: 40px;">
                <p style="color: #ef4444; font-size: 1.1rem;">&#9888;&#65039; ${tr('weather.error')}</p>
            </div>

            <div id="weatherContent" class="weather-grid">
                <div class="weather-main">
                    <div class="card">
                        <h3>${tr('weather.current')} - <span id="cityName">Delhi</span></h3>
                        <div class="current-weather">
                            <div>
                                <div class="temperature" id="currentTemp">--&deg;C</div>
                                <div id="weatherDesc">${tr('weather.loading')}</div>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 10px;">
                                    ${tr('weather.feelsLike')}: <span id="feelsLike">--&deg;C</span>
                                </div>
                            </div>
                            <div class="weather-stats">
                                <div>${tr('weather.humidity')}<br><span id="humidity">--%</span></div>
                                <div>${tr('weather.wind')}<br><span id="windSpeed">-- km/h</span></div>
                                <div>${tr('weather.pressure')}<br><span id="pressure">-- hPa</span></div>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <h3>${tr('weather.forecast')}</h3>
                        <div class="forecast-grid" id="forecastContainer">
                            <div class="forecast-item">${tr('weather.loading')}</div>
                        </div>
                    </div>
                </div>

                <div class="weather-sidebar">
                    <div class="card">
                        <h3>${tr('weather.alerts')}</h3>
                        <div id="agricAlerts">
                            <div class="alert low">
                                <strong>${tr('weather.loading')}</strong><br>
                                ${tr('weather.fetchingAlerts')}
                            </div>
                        </div>
                    </div>

                    <div class="card tips">
                        <h3>${tr('weather.tips')}</h3>
                        <ul>
                            <li>${tr('weather.tip1')}</li>
                            <li>${tr('weather.tip2')}</li>
                            <li>${tr('weather.tip3')}</li>
                            <li>${tr('weather.tip4')}</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `,

    dataLoading: (moduleName) => `
        <div class="container dashboard-data-state">
            <div class="spinner"></div>
            <h2>${tr('data.loading')}</h2>
            <p>${tr('data.loadingDesc')}</p>
        </div>
    `,

    dataError: (message) => `
        <div class="container dashboard-data-state error-state">
            <h2>${tr('data.error')}</h2>
            <p>${escapeDashboardText(message)}</p>
            <a href="#" data-route="home" class="btn">${tr('data.back')}</a>
        </div>
    `,

    databaseCropDetail: (crop) => `
        <div class="container crop-detail-page">
            <div class="crop-detail-header">
                <div class="crop-header-content">
                    <div class="crop-icon-large" aria-hidden="true">${getCropIcon(crop)}</div>
                    <div>
                        <h1>${escapeDashboardText(crop.name)}</h1>
                        <p class="scientific-name"><em>${escapeDashboardText(crop.scientificName)}</em></p>
                        <span class="badge-large">${escapeDashboardText(crop.category)}</span>
                    </div>
                </div>
            </div>

            <div class="quick-stats-grid">
                <div class="stat-box"><div class="stat-label">${tr('crop.season')}</div><div class="stat-value">${escapeDashboardText(crop.season)}</div></div>
                <div class="stat-box"><div class="stat-label">${tr('crop.duration')}</div><div class="stat-value">${escapeDashboardText(crop.duration)}</div></div>
                <div class="stat-box"><div class="stat-label">${tr('detail.yield')}</div><div class="stat-value">${escapeDashboardText(crop.yieldPerAcre)}</div></div>
                <div class="stat-box"><div class="stat-label">${tr('detail.price')}</div><div class="stat-value">${escapeDashboardText(crop.marketPrice)}</div></div>
            </div>

            <div class="card database-crop-details">
                <h2>${tr('detail.requirements')}</h2>
                <div class="database-detail-grid">
                    <div><span>${tr('detail.soil')}</span><strong>${escapeDashboardText(crop.soil)}</strong></div>
                    <div><span>${tr('detail.ph')}</span><strong>${escapeDashboardText(crop.pH)}</strong></div>
                    <div><span>${tr('detail.temperature')}</span><strong>${escapeDashboardText(crop.temperature)}</strong></div>
                    <div><span>${tr('detail.rainfall')}</span><strong>${escapeDashboardText(crop.rainfall)}</strong></div>
                    <div><span>${tr('detail.profit')}</span><strong>${escapeDashboardText(crop.estimatedProfit)}</strong></div>
                </div>
            </div>

            <a href="#" data-route="crops" class="back-btn-detail">${tr('detail.back')}</a>
        </div>
    `,

};
