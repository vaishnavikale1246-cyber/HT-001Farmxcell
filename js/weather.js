// Weather API Integration
// Using Open-Meteo API (free, no API key required)

const WeatherAPI = {
    baseUrl: 'https://api.open-meteo.com/v1',
    geocodingUrl: 'https://geocoding-api.open-meteo.com/v1',

    // Get coordinates for a city
    async getCoordinates(city) {
        try {
            const response = await fetch(
                `${this.geocodingUrl}/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`
            );
            
            if (!response.ok) {
                throw new Error('City not found');
            }
            
            const data = await response.json();
            
            if (!data.results || data.results.length === 0) {
                throw new Error('City not found');
            }
            
            return {
                lat: data.results[0].latitude,
                lon: data.results[0].longitude,
                name: data.results[0].name,
                country: data.results[0].country
            };
        } catch (error) {
            console.error('Error fetching coordinates:', error);
            throw error;
        }
    },

    // Get current weather by city name
    async getCurrentWeather(city) {
        try {
            const coords = await this.getCoordinates(city);
            return await this.getWeatherByCoords(coords.lat, coords.lon, coords.name);
        } catch (error) {
            console.error('Error fetching weather:', error);
            throw error;
        }
    },

    // Get weather by coordinates
    async getWeatherByCoords(lat, lon, cityName = 'Your Location') {
        try {
            const response = await fetch(
                `${this.baseUrl}/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,pressure_msl&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto`
            );
            
            if (!response.ok) {
                throw new Error('Weather data not available');
            }
            
            const data = await response.json();
            
            // Transform to our format
            return {
                name: cityName,
                main: {
                    temp: data.current.temperature_2m,
                    feels_like: data.current.apparent_temperature,
                    humidity: data.current.relative_humidity_2m,
                    pressure: data.current.pressure_msl
                },
                wind: {
                    speed: data.current.wind_speed_10m / 3.6 // Convert km/h to m/s
                },
                weather: [{
                    main: this.getWeatherDescription(data.current.weather_code),
                    description: this.getWeatherDescription(data.current.weather_code)
                }],
                daily: data.daily
            };
        } catch (error) {
            console.error('Error fetching weather:', error);
            throw error;
        }
    },

    // Get 5-day forecast
    async getForecast(city) {
        try {
            const coords = await this.getCoordinates(city);
            const weather = await this.getWeatherByCoords(coords.lat, coords.lon, coords.name);
            
            // Transform daily data to forecast format
            const forecastList = [];
            for (let i = 0; i < 5 && i < weather.daily.time.length; i++) {
                forecastList.push({
                    dt: new Date(weather.daily.time[i]).getTime() / 1000,
                    dt_txt: weather.daily.time[i] + ' 12:00:00',
                    main: {
                        temp: (weather.daily.temperature_2m_max[i] + weather.daily.temperature_2m_min[i]) / 2,
                        temp_min: weather.daily.temperature_2m_min[i],
                        temp_max: weather.daily.temperature_2m_max[i]
                    },
                    weather: [{
                        main: this.getWeatherDescription(weather.daily.weather_code[i])
                    }]
                });
            }
            
            return { list: forecastList };
        } catch (error) {
            console.error('Error fetching forecast:', error);
            throw error;
        }
    },

    // Get forecast by coordinates
    async getForecastByCoords(lat, lon) {
        try {
            const weather = await this.getWeatherByCoords(lat, lon);
            
            const forecastList = [];
            for (let i = 0; i < 5 && i < weather.daily.time.length; i++) {
                forecastList.push({
                    dt: new Date(weather.daily.time[i]).getTime() / 1000,
                    dt_txt: weather.daily.time[i] + ' 12:00:00',
                    main: {
                        temp: (weather.daily.temperature_2m_max[i] + weather.daily.temperature_2m_min[i]) / 2,
                        temp_min: weather.daily.temperature_2m_min[i],
                        temp_max: weather.daily.temperature_2m_max[i]
                    },
                    weather: [{
                        main: this.getWeatherDescription(weather.daily.weather_code[i])
                    }]
                });
            }
            
            return { list: forecastList };
        } catch (error) {
            console.error('Error fetching forecast:', error);
            throw error;
        }
    },

    // Convert WMO weather codes to descriptions
    getWeatherDescription(code) {
        const weatherCodes = {
            0: 'Clear sky',
            1: 'Mainly clear',
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Foggy',
            48: 'Foggy',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            71: 'Slight snow',
            73: 'Moderate snow',
            75: 'Heavy snow',
            77: 'Snow grains',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers',
            85: 'Slight snow showers',
            86: 'Heavy snow showers',
            95: 'Thunderstorm',
            96: 'Thunderstorm with hail',
            99: 'Thunderstorm with hail'
        };
        
        return weatherCodes[code] || 'Unknown';
    }
};

// Weather UI Manager
const WeatherUI = {
    // Update current weather display
    updateCurrentWeather(data) {
        document.getElementById('cityName').textContent = data.name;
        document.getElementById('currentTemp').textContent = `${Math.round(data.main.temp)}°C`;
        document.getElementById('weatherDesc').textContent = data.weather[0].description;
        document.getElementById('feelsLike').textContent = `${Math.round(data.main.feels_like)}°C`;
        document.getElementById('humidity').textContent = `${data.main.humidity}%`;
        document.getElementById('windSpeed').textContent = `${Math.round(data.wind.speed * 3.6)} km/h`;
        document.getElementById('pressure').textContent = `${data.main.pressure} hPa`;
    },

    // Update 5-day forecast
    updateForecast(data) {
        const forecastContainer = document.getElementById('forecastContainer');
        
        // Get one forecast per day (at 12:00)
        const dailyForecasts = data.list.filter(item => 
            item.dt_txt.includes('12:00:00')
        ).slice(0, 5);

        const forecastHTML = dailyForecasts.map(day => {
            const date = new Date(day.dt * 1000);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            const temp = Math.round(day.main.temp);
            const tempMin = Math.round(day.main.temp_min);
            const tempMax = Math.round(day.main.temp_max);
            
            return `
                <div class="forecast-item">
                    ${dayName}<br>
                    ${tempMax}° / ${tempMin}°<br>
                    <small style="font-size: 0.8rem;">${day.weather[0].main}</small>
                </div>
            `;
        }).join('');

        forecastContainer.innerHTML = forecastHTML;
    },

    // Generate agricultural alerts based on weather
    generateAgricAlerts(currentWeather, forecast) {
        const alerts = [];
        const temp = currentWeather.main.temp;
        const humidity = currentWeather.main.humidity;
        const windSpeed = currentWeather.wind.speed * 3.6; // Convert to km/h

        // Check for rain in forecast
        const rainForecast = forecast.list.slice(0, 8).some(item => 
            item.weather[0].main.toLowerCase().includes('rain')
        );

        if (rainForecast) {
            alerts.push({
                level: 'medium',
                title: 'Rainfall Expected',
                message: 'Rain forecasted in the next 24 hours. Plan irrigation accordingly.'
            });
        }

        // Temperature alerts
        if (temp > 35) {
            alerts.push({
                level: 'high',
                title: 'High Temperature Alert',
                message: 'Extreme heat detected. Ensure adequate irrigation and crop protection.'
            });
        } else if (temp < 10) {
            alerts.push({
                level: 'high',
                title: 'Frost Warning',
                message: 'Low temperatures may cause frost. Protect sensitive crops.'
            });
        }

        // Humidity alerts
        if (humidity > 80) {
            alerts.push({
                level: 'medium',
                title: 'High Humidity',
                message: 'High humidity may increase disease risk. Monitor crops closely.'
            });
        } else if (humidity < 30) {
            alerts.push({
                level: 'medium',
                title: 'Low Humidity',
                message: 'Dry conditions detected. Consider increasing irrigation frequency.'
            });
        }

        // Wind alerts
        if (windSpeed > 40) {
            alerts.push({
                level: 'high',
                title: 'Strong Winds',
                message: 'High wind speeds. Avoid spraying pesticides and secure crops.'
            });
        }

        // Pest activity (based on temperature and humidity)
        if (temp > 20 && temp < 30 && humidity > 60) {
            alerts.push({
                level: 'medium',
                title: 'Pest Activity Risk',
                message: 'Favorable conditions for pest activity. Monitor crops regularly.'
            });
        }

        // Default alert if no specific alerts
        if (alerts.length === 0) {
            alerts.push({
                level: 'low',
                title: 'Favorable Conditions',
                message: 'Weather conditions are favorable for farming activities.'
            });
        }

        return alerts;
    },

    // Display agricultural alerts
    displayAgricAlerts(alerts) {
        const alertsContainer = document.getElementById('agricAlerts');
        
        const alertsHTML = alerts.map(alert => `
            <div class="alert ${alert.level}">
                <strong>${alert.title}</strong><br>
                ${alert.message}
            </div>
        `).join('');

        alertsContainer.innerHTML = alertsHTML;
    },

    // Show loading state
    showLoading() {
        document.getElementById('weatherLoading').style.display = 'block';
        document.getElementById('weatherContent').style.display = 'none';
        document.getElementById('weatherError').style.display = 'none';
    },

    // Show content
    showContent() {
        document.getElementById('weatherLoading').style.display = 'none';
        document.getElementById('weatherContent').style.display = 'grid';
        document.getElementById('weatherError').style.display = 'none';
    },

    // Show error
    showError() {
        document.getElementById('weatherLoading').style.display = 'none';
        document.getElementById('weatherContent').style.display = 'none';
        document.getElementById('weatherError').style.display = 'block';
    }
};

// Weather Controller
const WeatherController = {
    // Load weather for a city
    async loadWeather(city) {
        WeatherUI.showLoading();

        try {
            // Fetch current weather and forecast
            const [currentWeather, forecast] = await Promise.all([
                WeatherAPI.getCurrentWeather(city),
                WeatherAPI.getForecast(city)
            ]);

            // Update UI
            WeatherUI.updateCurrentWeather(currentWeather);
            WeatherUI.updateForecast(forecast);

            // Generate and display agricultural alerts
            const alerts = WeatherUI.generateAgricAlerts(currentWeather, forecast);
            WeatherUI.displayAgricAlerts(alerts);

            WeatherUI.showContent();

            // Save last searched city
            localStorage.setItem('lastWeatherCity', city);
        } catch (error) {
            console.error('Error loading weather:', error);
            WeatherUI.showError();
        }
    },

    // Load weather by coordinates
    async loadWeatherByCoords(lat, lon) {
        WeatherUI.showLoading();

        try {
            const [currentWeather, forecast] = await Promise.all([
                WeatherAPI.getWeatherByCoords(lat, lon),
                WeatherAPI.getForecastByCoords(lat, lon)
            ]);

            WeatherUI.updateCurrentWeather(currentWeather);
            WeatherUI.updateForecast(forecast);

            const alerts = WeatherUI.generateAgricAlerts(currentWeather, forecast);
            WeatherUI.displayAgricAlerts(alerts);

            WeatherUI.showContent();

            // Save city name
            localStorage.setItem('lastWeatherCity', currentWeather.name);
        } catch (error) {
            console.error('Error loading weather:', error);
            WeatherUI.showError();
        }
    },

    // Get user's current location
    getCurrentLocation() {
        if (navigator.geolocation) {
            WeatherUI.showLoading();
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.loadWeatherByCoords(
                        position.coords.latitude,
                        position.coords.longitude
                    );
                },
                (error) => {
                    console.error('Geolocation error:', error);
                    alert('Unable to get your location. Please enter a city name.');
                    WeatherUI.showContent();
                }
            );
        } else {
            alert('Geolocation is not supported by your browser.');
        }
    },

    // Initialize weather page
    init() {
        // Load last searched city or default to Delhi
        const lastCity = localStorage.getItem('lastWeatherCity') || 'Delhi';
        this.loadWeather(lastCity);
    }
};

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WeatherAPI, WeatherUI, WeatherController };
}
