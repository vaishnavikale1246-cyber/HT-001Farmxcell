// Weather API Integration
// Using Open-Meteo API (free, no API key required)

const weatherText = (key) => window.AgriI18n?.t(key) || key;

const WeatherAPI = {
    baseUrl: 'https://api.open-meteo.com/v1',
    geocodingUrl: 'https://geocoding-api.open-meteo.com/v1',

    // Get coordinates for a city
    async getCoordinates(city) {
        try {
            const language = window.AgriI18n?.current || 'en';
            const response = await fetch(
                `${this.geocodingUrl}/search?name=${encodeURIComponent(city)}&count=1&language=${encodeURIComponent(language)}&format=json`
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
                    code: data.current.weather_code,
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
                        code: weather.daily.weather_code[i],
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
                        code: weather.daily.weather_code[i],
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
            0: 'clear', 1: 'mainlyClear', 2: 'partlyCloudy', 3: 'overcast',
            45: 'foggy', 48: 'foggy', 51: 'lightDrizzle', 53: 'moderateDrizzle',
            55: 'denseDrizzle', 61: 'slightRain', 63: 'moderateRain', 65: 'heavyRain',
            71: 'slightSnow', 73: 'moderateSnow', 75: 'heavySnow', 77: 'snowGrains',
            80: 'slightRainShowers', 81: 'moderateRainShowers', 82: 'violentRainShowers',
            85: 'slightSnowShowers', 86: 'heavySnowShowers', 95: 'thunderstorm',
            96: 'thunderstormHail', 99: 'thunderstormHail'
        };

        return weatherText(`weather.code.${weatherCodes[code] || 'unknown'}`);
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
            const locales = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' };
            const dayName = date.toLocaleDateString(
                locales[window.AgriI18n?.current] || 'en-IN',
                { weekday: 'short' }
            );
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
        const rainCodes = new Set([51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]);
        const rainForecast = forecast.list.slice(0, 8).some(item =>
            rainCodes.has(item.weather[0].code)
        );

        if (rainForecast) {
            alerts.push({
                level: 'medium',
                title: weatherText('weather.alert.rainTitle'),
                message: weatherText('weather.alert.rainMessage')
            });
        }

        // Temperature alerts
        if (temp > 35) {
            alerts.push({
                level: 'high',
                title: weatherText('weather.alert.heatTitle'),
                message: weatherText('weather.alert.heatMessage')
            });
        } else if (temp < 10) {
            alerts.push({
                level: 'high',
                title: weatherText('weather.alert.frostTitle'),
                message: weatherText('weather.alert.frostMessage')
            });
        }

        // Humidity alerts
        if (humidity > 80) {
            alerts.push({
                level: 'medium',
                title: weatherText('weather.alert.highHumidityTitle'),
                message: weatherText('weather.alert.highHumidityMessage')
            });
        } else if (humidity < 30) {
            alerts.push({
                level: 'medium',
                title: weatherText('weather.alert.lowHumidityTitle'),
                message: weatherText('weather.alert.lowHumidityMessage')
            });
        }

        // Wind alerts
        if (windSpeed > 40) {
            alerts.push({
                level: 'high',
                title: weatherText('weather.alert.windTitle'),
                message: weatherText('weather.alert.windMessage')
            });
        }

        // Pest activity (based on temperature and humidity)
        if (temp > 20 && temp < 30 && humidity > 60) {
            alerts.push({
                level: 'medium',
                title: weatherText('weather.alert.pestTitle'),
                message: weatherText('weather.alert.pestMessage')
            });
        }

        // Default alert if no specific alerts
        if (alerts.length === 0) {
            alerts.push({
                level: 'low',
                title: weatherText('weather.alert.goodTitle'),
                message: weatherText('weather.alert.goodMessage')
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
                    alert(weatherText('weather.locationFailed'));
                    WeatherUI.showContent();
                }
            );
        } else {
            alert(weatherText('weather.locationUnsupported'));
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
