// Admin Farmer Analytics - renders only data returned from PostgreSQL.

const AdminAnalytics = {
    filtersReady: false,

    escape(value) {
        return String(value ?? '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    },

    number(value) {
        return new Intl.NumberFormat('en-IN').format(Number(value) || 0);
    },

    queryString() {
        const parameters = new URLSearchParams();
        const fields = {
            period: document.getElementById('analyticsPeriod').value,
            crop_id: document.getElementById('analyticsCrop').value,
            disease: document.getElementById('analyticsDisease').value,
            fertilizer_id: document.getElementById('analyticsFertilizer').value,
            activity_type: document.getElementById('analyticsActivity').value
        };
        Object.entries(fields).forEach(([key, value]) => {
            if (value) parameters.set(key, value);
        });
        return parameters.toString();
    },

    async load() {
        const status = document.getElementById('analyticsStatus');
        const content = document.getElementById('analyticsContent');
        status.hidden = false;
        status.className = 'analytics-status';
        status.textContent = 'Loading actual farmer activity...';

        try {
            const response = await fetch(`/admin/api/analytics?${this.queryString()}`, {
                headers: { Accept: 'application/json' },
                cache: 'no-store'
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(data.error || 'Analytics could not be loaded.');

            if (!this.filtersReady) {
                this.populateFilters(data.availableFilters);
                this.filtersReady = true;
            }
            this.render(data);
            status.hidden = true;
            content.hidden = false;
        } catch (error) {
            status.className = 'analytics-status error';
            status.textContent = error.message;
            content.hidden = true;
        }
    },

    populateFilters(options) {
        const addOptions = (elementId, values, valueKey, labelKey) => {
            const select = document.getElementById(elementId);
            values.forEach(item => {
                const option = document.createElement('option');
                option.value = valueKey ? item[valueKey] : item;
                option.textContent = labelKey ? item[labelKey] : item;
                select.appendChild(option);
            });
        };
        addOptions('analyticsCrop', options.crops, 'id', 'name');
        addOptions('analyticsDisease', options.diseases);
        addOptions('analyticsFertilizer', options.fertilizers, 'id', 'name');
        addOptions('analyticsActivity', options.activityTypes, 'value', 'label');
    },

    render(data) {
        const overview = data.overview;
        document.getElementById('metricFarmers').textContent = this.number(overview.totalFarmers);
        document.getElementById('metricCrops').textContent = this.number(overview.totalCrops);
        document.getElementById('metricTotalFertilizers').textContent = this.number(overview.totalFertilizers);
        document.getElementById('metricLoans').textContent = this.number(overview.totalLoans);
        document.getElementById('metricCropInterest').textContent = this.number(overview.cropInterests);
        document.getElementById('metricDiseaseUploads').textContent = this.number(overview.diseaseUploads);
        document.getElementById('metricFertilizers').textContent = this.number(overview.fertilizerInteractions);
        document.getElementById('metricActivities').textContent = this.number(overview.totalActivities);
        document.getElementById('analyticsTrackingNotice').textContent = data.trackingNotice;

        this.renderBars('cropInterestChart', data.charts.cropInterest, 'crop-bars');
        this.renderBars('diseaseCropChart', data.charts.diseaseByCrop, 'disease-bars');
        this.renderBars('diseaseChart', data.charts.diseaseCounts, 'disease-bars');
        this.renderBars('fertilizerChart', data.charts.fertilizerCounts, 'fertilizer-bars');
        this.renderLine('monthlyActivityChart', data.charts.monthlyActivity);

        document.getElementById('highestDisease').textContent = data.insights.highestDisease || 'No data';
        document.getElementById('lowestDisease').textContent = data.insights.lowestDisease || 'No data';
        document.getElementById('topFertilizer').textContent = data.insights.topFertilizer || 'No data';
        document.getElementById('topFertilizerType').textContent = data.insights.topFertilizerType || 'No data';

        this.renderTopCrops(data.topCrops);
        this.renderRecentActivity(data.recentActivity);
    },

    renderBars(elementId, items, className) {
        const container = document.getElementById(elementId);
        container.className = `analytics-chart ${className}`;
        if (!items.length) {
            container.innerHTML = '<div class="analytics-empty">No recorded activity matches these filters.</div>';
            return;
        }

        const maximum = Math.max(...items.map(item => Number(item.value)), 1);
        container.innerHTML = items.map(item => `
            <div class="analytics-bar-row">
                <div class="analytics-bar-label">
                    <span title="${this.escape(item.label)}">${this.escape(item.label)}</span>
                    <strong>${this.number(item.value)}</strong>
                </div>
                <div class="analytics-bar-track" role="img" aria-label="${this.escape(item.label)}: ${this.number(item.value)}">
                    <div class="analytics-bar-fill" style="width:${Math.max(2, (Number(item.value) / maximum) * 100)}%"></div>
                </div>
            </div>
        `).join('');
    },

    renderLine(elementId, items) {
        const container = document.getElementById(elementId);
        if (!items.length) {
            container.innerHTML = '<div class="analytics-empty">No monthly activity has been recorded yet.</div>';
            return;
        }

        const width = 760;
        const height = 270;
        const left = 48;
        const right = 22;
        const top = 22;
        const bottom = 48;
        const plotWidth = width - left - right;
        const plotHeight = height - top - bottom;
        const maxValue = Math.max(...items.map(item => Number(item.value)), 1);
        const x = index => items.length === 1
            ? left + plotWidth / 2
            : left + (index * plotWidth / (items.length - 1));
        const y = value => top + plotHeight - (Number(value) / maxValue * plotHeight);
        const points = items.map((item, index) => `${x(index)},${y(item.value)}`).join(' ');
        const grid = [0, .25, .5, .75, 1].map(fraction => {
            const gridY = top + plotHeight - (fraction * plotHeight);
            return `<line class="grid-line" x1="${left}" y1="${gridY}" x2="${width - right}" y2="${gridY}" />
                <text x="${left - 8}" y="${gridY + 4}" text-anchor="end">${Math.round(maxValue * fraction)}</text>`;
        }).join('');
        const dots = items.map((item, index) => {
            const label = new Date(`${item.label}-01T00:00:00`).toLocaleDateString('en-IN', {
                month: 'short', year: '2-digit', timeZone: 'Asia/Kolkata'
            });
            return `<circle class="activity-dot" cx="${x(index)}" cy="${y(item.value)}" r="5">
                        <title>${this.escape(label)}: ${this.number(item.value)}</title>
                    </circle>
                    <text x="${x(index)}" y="${height - 18}" text-anchor="middle">${this.escape(label)}</text>`;
        }).join('');

        container.innerHTML = `
            <svg class="analytics-line-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Monthly farmer activity line chart">
                ${grid}
                <polyline class="activity-line" points="${points}" />
                ${dots}
            </svg>
        `;
    },

    renderTopCrops(rows) {
        const body = document.getElementById('topCropsBody');
        if (!rows.length) {
            body.innerHTML = '<tr class="analytics-table-empty"><td colspan="4">No crop activity has been recorded yet.</td></tr>';
            return;
        }
        body.innerHTML = rows.map(row => `
            <tr>
                <td><strong>${this.escape(row.name)}</strong></td>
                <td>${this.number(row.views)}</td>
                <td>${this.number(row.diseaseUploads)}</td>
                <td>${this.number(row.interestedFarmers)}</td>
            </tr>
        `).join('');
    },

    renderRecentActivity(rows) {
        const body = document.getElementById('recentActivityBody');
        if (!rows.length) {
            body.innerHTML = '<tr class="analytics-table-empty"><td colspan="4">No farmer activity has been recorded yet.</td></tr>';
            return;
        }
        const dateFormatter = new Intl.DateTimeFormat('en-IN', {
            dateStyle: 'medium',
            timeStyle: 'short',
            timeZone: 'Asia/Kolkata'
        });
        body.innerHTML = rows.map(row => `
            <tr>
                <td>${this.escape(row.farmer)}</td>
                <td>${this.escape(row.activity)}</td>
                <td>${this.escape(row.resource)}</td>
                <td>${this.escape(dateFormatter.format(new Date(row.createdAt)))}</td>
            </tr>
        `).join('');
    },

    init() {
        const form = document.getElementById('analyticsFilters');
        if (!form) return;
        form.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', () => this.load());
        });
        document.getElementById('resetAnalyticsFilters').addEventListener('click', () => {
            form.reset();
            this.load();
        });
        this.load();
    }
};

document.addEventListener('DOMContentLoaded', () => AdminAnalytics.init());
