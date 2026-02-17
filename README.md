# AgriHelper – Smart Crop & Farming Assistant

A comprehensive digital platform designed to empower farmers with data-driven agricultural decision-making tools.

## 🌟 Problem Statement

Farmers face multiple challenges in making informed agricultural decisions:

- **Lack of accurate crop information** – Uncertainty about which crops are suitable for their soil and season
- **Difficulty in fertilizer selection** – Improper usage reduces crop yield or increases costs
- **Unpredictable weather conditions** – Rain, drought, or temperature changes affecting crop health
- **Limited access to financial assistance** – Difficulty investing in seeds, equipment, or fertilizers

Most farmers rely on traditional methods or scattered information sources, leading to inefficiencies, low productivity, and financial loss. There is a need for a single, easy-to-use digital platform that provides reliable guidance.

## Proposed Solution

AgriHelper is a comprehensive web-based platform that assists farmers with:

### 1. Crop Information Module
- Detailed crop database with growing conditions, seasons, and soil requirements
- Search and filter functionality by crop type (Cereal, Vegetable, Pulse)
- Growth duration, water requirements, and expected yield information
- Common diseases and best practices for each crop
- Crop-specific guides for wheat, maize, soybean, sugarcane, and tomato

### 2. Fertilizer Guidance Module
- Recommendations for common fertilizers (Urea, DAP)
- Nutrient composition and dosage guidelines
- Application timing and methods (broadcasting, band placement, fertigation, foliar spray)
- Crop-specific fertilizer pairing suggestions
- Interactive accordion-based learning interface

### 3. Weather Update Module
- **Live weather data** powered by OpenWeatherMap API
- Real-time current conditions (temperature, humidity, wind, pressure)
- 5-day forecast for planning agricultural activities
- Hourly weather updates
- **Smart agricultural alerts** based on weather conditions:
  - Rainfall warnings for irrigation planning
  - Temperature alerts for crop protection
  - Humidity monitoring for disease risk
  - Wind speed alerts for spraying activities
  - Pest activity predictions
- Location-based weather search
- GPS location support (use current location)
- Weather tips for farmers
- Remembers last searched location

### 4. Loan & Financial Support Module
- Government loan schemes database (KCC, PMFBY)
- Search and filter by loan type and region
- Interest rates, maximum loan amounts, and benefits
- Helps farmers plan investments for seeds, fertilizers, and equipment

## Expected Impact

- ✅ Improved crop productivity and yield
- ✅ Reduced crop loss due to incorrect fertilizer use or weather surprises
- ✅ Empowerment of farmers through digital knowledge
- ✅ Easier access to financial support for sustainable farming
- ✅ Data-driven and reliable agricultural decision-making

## Technology Stack

- **Architecture**: Single Page Application (SPA)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **APIs**: OpenWeatherMap API for live weather data
- **Routing**: Client-side router
- **Storage**: LocalStorage (for user authentication)
- **Design**: Responsive, mobile-first approach
- **No Dependencies**: Pure vanilla JS, no frameworks required

## Features

### User Authentication
- Login and registration system
- Password recovery functionality
- Session management with localStorage

### Responsive Design
- Mobile-friendly interface
- Consistent green-themed design system
- Card-based layouts for easy navigation
- Sticky navigation bars

### Interactive Elements
- Search functionality across all modules
- Category filtering for crops and loans
- Accordion-based information display
- Dynamic content filtering

## Architecture

### Professional SPA Design
AgriHelper is built as a modern Single Page Application with:
- **One HTML file** - Professional entry point
- **Modular JavaScript** - Organized, maintainable code
- **Client-side routing** - Smooth navigation without page reloads
- **Component-based** - Reusable templates and logic

### Key Modules
- **Router** - Handles navigation and URL management
- **Auth Manager** - User authentication and session management
- **Content Manager** - Dynamic content rendering and event handling
- **Data Store** - Centralized data management for crops and loans
- **Page Templates** - Modular page components

## Getting Started

### Quick Start
1. Clone the repository:
```bash
git clone https://github.com/yourusername/AgriHelper.git
cd AgriHelper
```

2. Open `app.html` in your web browser
   - Or use a local server for better experience:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve
   ```

3. Navigate to `http://localhost:8000/app.html`

### Project Structure
```
AgriHelper/
├── app.html              # Main application (SPA)
├── css/
│   └── main.css         # Consolidated styles
├── js/
│   ├── app.js           # Core logic & router
│   ├── pages.js         # Page templates
│   └── data.js          # Data store
├── assets/              # Images & media
└── data/                # Additional data
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed architecture information.

## Usage

### For Farmers
1. **Register/Login** to access personalized features
2. **Browse Crops** to find suitable options for your region
3. **Check Fertilizers** for proper application guidance
4. **Monitor Weather** to plan farming activities
5. **Explore Loans** to find financial support options

### Navigation
- Home: Overview of all features
- Crop Info: Detailed crop database
- Fertilizer: Application guides and recommendations
- Gov Loans: Financial assistance schemes
- Weather: Real-time updates and forecasts

## Future Enhancements

- Backend integration for dynamic data
- ~~Real-time weather API integration~~ ✅ **DONE!**
- Soil testing recommendations
- Pest and disease detection using AI
- Multi-language support for regional farmers
- Mobile app version
- Community forum for farmer discussions
- Expert consultation booking system
- SMS alerts for weather warnings
- Offline mode with Progressive Web App (PWA)

## 📚 Documentation

This project includes comprehensive documentation:

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 2 minutes
- **[WEATHER_API_SETUP.md](WEATHER_API_SETUP.md)** - Setup live weather API
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Architecture and code organization
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Old vs new structure comparison
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to production
- **[HACKATHON_GUIDE.md](HACKATHON_GUIDE.md)** - Presentation and demo guide
- **[SUMMARY.md](SUMMARY.md)** - Project transformation overview
- **[DOCS_INDEX.md](DOCS_INDEX.md)** - Complete documentation index

## Contributing

This is a hackathon project. Contributions and suggestions are welcome!

## Team

Project developed for hackathon: HT-001Farmxcell

## License

This project is open source and available for educational purposes.

---

**AgriHelper** – Cultivating Tomorrow, Today 🌱
