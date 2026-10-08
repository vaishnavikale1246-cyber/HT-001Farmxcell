// Smart Agricultural Calendar UI. The farmer selects only a crop;
// all dates and activities come from verified server-side profiles.

const CalendarController = {
    selectedYear: new Date().getFullYear(),
    options: null,

    t(key) {
        return window.AgriI18n?.t(key) || key;
    },

    escape(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    },

    formatDate(value) {
        if (!value) return this.t('calendar.notAvailable');
        const locales = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' };
        const locale = locales[window.AgriI18n?.current] || 'en-IN';
        return new Date(`${value}T00:00:00`).toLocaleDateString(locale, {
            day: 'numeric', month: 'short', year: 'numeric'
        });
    },

    async request(url) {
        const response = await fetch(url, {
            headers: { Accept: 'application/json' },
            cache: 'no-store'
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(this.t('calendar.failed'));
        return data;
    },

    async init() {
        const status = document.getElementById('calendarStatus');
        if (!status) return;

        try {
            this.options = await this.request(`/api/calendar/options?year=${this.selectedYear}`);
            const select = document.getElementById('calendarCropSelect');
            if (!this.options.crops.length) {
                throw new Error(this.t('calendar.noProfiles'));
            }

            select.innerHTML = this.options.crops.map(crop =>
                `<option value="${Number(crop.id)}">${this.escape(crop.name)} - ${this.escape(crop.season)}</option>`
            ).join('');
            select.disabled = false;
            select.addEventListener('change', () => this.loadCrop(Number(select.value)));

            this.renderPlantingSuggestions();
            this.loadWeatherContext();
            await this.loadCrop(Number(select.value));
        } catch (error) {
            this.showError(error.message);
        }
    },

    async loadCrop(cropId) {
        const status = document.getElementById('calendarStatus');
        const content = document.getElementById('calendarContent');
        status.hidden = false;
        status.className = 'calendar-status';
        status.textContent = this.t('calendar.building');
        content.hidden = true;

        try {
            const plan = await this.request(`/api/calendar/${cropId}?year=${this.selectedYear}`);
            this.renderSummary(plan);
            this.renderMonths(plan);
            this.renderHistory(plan);
            window.farmerAnalytics?.track('calendar_view', { crop_id: cropId });
            status.hidden = true;
            content.hidden = false;
        } catch (error) {
            this.showError(error.message);
        }
    },

    renderSummary(plan) {
        const activeCycle = plan.cycles.find(cycle => cycle.sowingDate.startsWith(String(plan.year))) || plan.cycles[0];
        const source = plan.profile.source;
        document.getElementById('calendarSummary').innerHTML = `
            <div class="calendar-summary-main">
                <span class="calendar-source-badge">${this.escape(this.t('calendar.verifiedPlan'))}</span>
                <h2>${this.escape(plan.crop.name)} ${plan.year} ${this.escape(this.t('calendar.plan'))}</h2>
                <p>${this.escape(plan.profile.region)}</p>
            </div>
            <div class="calendar-summary-stat">
                <span>${this.escape(this.t('calendar.sowingDate'))}</span>
                <strong>${this.formatDate(activeCycle.sowingDate)}</strong>
            </div>
            <div class="calendar-summary-stat">
                <span>${this.escape(this.t('calendar.harvestWindow'))}</span>
                <strong>${this.formatDate(activeCycle.harvestWindow.start)} - ${this.formatDate(activeCycle.harvestWindow.end)}</strong>
            </div>
            <div class="calendar-summary-stat">
                <span>${this.escape(this.t('calendar.referenceSource'))}</span>
                <a href="${this.escape(source.url)}" target="_blank" rel="noopener noreferrer">${this.escape(source.name)}</a>
            </div>
            <p class="calendar-disclaimer">${this.escape(this.t('calendar.disclaimer'))}</p>
        `;
    },

    renderPlantingSuggestions() {
        const container = document.getElementById('plantThisMonth');
        const crops = this.options.plantThisMonth;
        const monthName = this.t(`month.${this.options.currentMonth}`);

        container.innerHTML = `
            <div>
                <span class="calendar-eyebrow">${this.escape(this.t('calendar.seasonalGuide'))}</span>
                <h2>${this.escape(this.t('calendar.plantIn'))} ${this.escape(monthName)}</h2>
            </div>
            ${crops.length ? `
                <div class="planting-chips">
                    ${crops.map(crop => `<button type="button" data-calendar-crop="${Number(crop.id)}">${this.escape(crop.name)}</button>`).join('')}
                </div>
            ` : `<p>${this.escape(this.t('calendar.noPlanting'))}</p>`}
        `;

        container.querySelectorAll('[data-calendar-crop]').forEach(button => {
            button.addEventListener('click', () => {
                const cropId = Number(button.dataset.calendarCrop);
                document.getElementById('calendarCropSelect').value = String(cropId);
                this.loadCrop(cropId);
            });
        });
    },

    renderMonths(plan) {
        const currentMonth = new Date().getFullYear() === plan.year ? new Date().getMonth() + 1 : 0;
        document.getElementById('calendarMonths').innerHTML = plan.months.map(month => {
            const empty = !month.activities.length && !month.risks.length;
            return `
                <article class="calendar-month-card ${month.number === currentMonth ? 'is-current' : ''}">
                    <header>
                        <div>
                            <span>${String(month.number).padStart(2, '0')}</span>
                            <h3>${this.escape(this.t(`month.${month.number}`))}</h3>
                        </div>
                        ${month.number === currentMonth ? `<b>${this.escape(this.t('calendar.currentMonth'))}</b>` : ''}
                    </header>
                    <div class="calendar-month-body">
                        ${empty ? `<p class="calendar-empty-month">${this.escape(this.t('calendar.emptyMonth'))}</p>` : ''}
                        ${month.activities.map(item => `
                            <div class="calendar-activity priority-${this.escape(item.priority)}">
                                <div class="calendar-activity-top">
                                    <span class="activity-type">${this.escape(item.type)}</span>
                                    <span class="activity-status ${this.escape(item.status)}">${this.escape(this.t(`calendar.status.${item.status}`))}</span>
                                </div>
                                <h4>${this.escape(item.title)}</h4>
                                <p>${this.escape(item.guidance)}</p>
                                <small>${this.formatDate(item.startDate)} - ${this.formatDate(item.endDate)} &middot; ${this.escape(item.stage)}</small>
                            </div>
                        `).join('')}
                        ${month.risks.map(risk => `
                            <div class="calendar-risk-card">
                                <span class="risk-badge">${this.escape(this.t('calendar.monitoringRisk'))}</span>
                                <h4>${this.escape(risk.disease)}</h4>
                                <p><strong>${this.escape(this.t('calendar.conditions'))}</strong> ${this.escape(risk.conditions)}</p>
                                <p><strong>${this.escape(this.t('calendar.watchFor'))}</strong> ${this.escape(risk.symptoms)}</p>
                                <ul>${risk.precautions.map(item => `<li>${this.escape(item)}</li>`).join('')}</ul>
                                <a href="#" data-route="disease">${this.escape(this.t('calendar.openDisease'))}</a>
                            </div>
                        `).join('')}
                    </div>
                </article>
            `;
        }).join('');
    },

    renderHistory(plan) {
        const history = plan.historicalComparison;
        document.getElementById('calendarHistory').innerHTML = `
            <span class="calendar-source-badge muted">${this.escape(this.t('calendar.history'))}</span>
            <h2>${this.escape(this.t(history.available ? 'calendar.farmHistory' : 'calendar.noHistory'))}</h2>
            <p>${this.escape(history.available ? history.message : this.t('calendar.historyMessage'))}</p>
        `;
    },

    async loadWeatherContext() {
        const city = localStorage.getItem('lastWeatherCity') || 'Delhi';
        document.getElementById('calendarLocation').textContent = city;
        const container = document.getElementById('calendarWeatherAlert');
        container.innerHTML = `<span>${this.escape(this.t('calendar.weatherApi'))}</span><p>${this.escape(this.t('calendar.checkingWeather'))}</p>`;

        if (typeof WeatherAPI === 'undefined') {
            container.innerHTML = `<span>${this.escape(this.t('calendar.weatherUnavailable'))}</span><p>${this.escape(this.t('calendar.calendarAvailable'))}</p>`;
            return;
        }

        try {
            const weather = await WeatherAPI.getCurrentWeather(city);
            const alerts = [];
            if (weather.main.temp > 35) alerts.push(this.t('calendar.highHeat'));
            if (weather.main.temp < 10) alerts.push(this.t('calendar.lowTemperature'));
            if (weather.main.humidity > 80) alerts.push(this.t('calendar.highHumidity'));
            if (weather.wind.speed * 3.6 > 40) alerts.push(this.t('calendar.strongWind'));
            if (new Set([51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]).has(weather.weather[0].code)) {
                alerts.push(this.t('calendar.rainDetected'));
            }

            container.innerHTML = `
                <span class="calendar-source-badge weather">${this.escape(this.t('calendar.liveWeather'))}</span>
                <strong>${this.escape(weather.name)}: ${Math.round(weather.main.temp)}&deg;C, ${this.escape(weather.weather[0].description)}</strong>
                <p>${this.escape(alerts[0] || this.t('calendar.normalWeather'))}</p>
            `;
        } catch (_error) {
            container.innerHTML = `<span class="calendar-source-badge muted">${this.escape(this.t('calendar.weatherUnavailable'))}</span><p>${this.escape(this.t('calendar.weatherLoadFailed'))}</p>`;
        }
    },

    showError(message) {
        const status = document.getElementById('calendarStatus');
        if (!status) return;
        status.hidden = false;
        status.className = 'calendar-status error';
        status.textContent = message;
        const content = document.getElementById('calendarContent');
        if (content) content.hidden = true;
    }
};
