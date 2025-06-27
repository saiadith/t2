# 🛍️ E-commerce Customer Analytics System

A comprehensive real-time analytics platform for analyzing customer purchasing patterns, seasonal trends, and abandoned cart characteristics to improve conversion rates.

## 📋 Problem Statement

Using e-commerce transaction data, identify customer purchasing patterns, seasonal trends, and abandoned cart characteristics to generate insights for improving conversion rates.

## 🚀 Quick Start with Docker (Recommended)

The easiest way to run this system on any PC is using Docker:

### Prerequisites
- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **At least 4GB RAM** available

### 1. Clone and Start
```bash
git clone <repository-url>
cd customer-stream-project/docker

# On Windows:
start.bat

# On Linux/macOS:
chmod +x start.sh
./start.sh
```

### 2. Access the Dashboard
Open your browser and go to: **http://localhost:8501**

### 3. Stop the System
```bash
# On Windows:
stop.bat

# On Linux/macOS:
./stop.sh
```

**That's it!** The entire system will be running with:
- 📈 **Dashboard** at http://localhost:8501
- 🔌 **WebSocket Server** at ws://localhost:8765
- 🗄️ **Database** at localhost:5432

For detailed Docker documentation, see [docker/README.md](docker/README.md).

## 🏗️ System Architecture

The system consists of several interconnected components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Event         │    │   WebSocket     │    │   PostgreSQL    │
│   Simulator     │───▶│   Server        │───▶│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Streamlit     │
                       │   Dashboard     │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   ML Analytics  │
                       │   Engine        │
                       └─────────────────┘
```

## 🚀 Features

### Real-time Data Streaming
- **Event Simulator**: Generates realistic e-commerce events (add to cart, remove from cart, purchase, abandon)
- **WebSocket Server**: Handles real-time event streaming and database storage
- **Customer Generation**: Creates 100 fake customers with realistic profiles

### Analytics Dashboard
- **Live Updates**: Auto-refreshes every 5 seconds
- **Conversion Funnel**: Visualizes customer journey from cart to purchase
- **Seasonal Trends**: Analyzes hourly, daily, and monthly patterns
- **Customer Behavior**: Age group analysis and top customer identification
- **Product Performance**: Most viewed and highest revenue products
- **Abandoned Cart Analysis**: Identifies abandonment patterns and rates

### Machine Learning Analytics
- **Customer Prediction Model**: Predicts purchase likelihood using Random Forest
- **Pattern Recognition**: Identifies customer behavior patterns
- **Conversion Rate Analysis**: Calculates and tracks conversion metrics
- **Abandonment Insights**: Provides recommendations to reduce cart abandonment

## 📊 Key Metrics Tracked

- **Conversion Rate**: Cart to purchase conversion percentage
- **Abandonment Rate**: Percentage of abandoned carts
- **Average Order Value**: Mean transaction value
- **Customer Lifetime Value**: Total revenue per customer
- **Seasonal Patterns**: Peak activity hours, days, and months
- **Product Performance**: Most popular and profitable products

## 🛠️ Technology Stack

- **Backend**: Python, WebSocket, PostgreSQL
- **Frontend**: Streamlit, Plotly
- **ML/Analytics**: Scikit-learn, Pandas, NumPy
- **Data Generation**: Faker, FakeStore API
- **Real-time**: WebSocket, Auto-refresh
- **Containerization**: Docker, Docker Compose

## 📦 Manual Installation & Setup

If you prefer to run without Docker:

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### 1. Clone the Repository
```bash
git clone <repository-url>
cd customer-stream-project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb customer_events

# Initialize database schema
psql -d customer_events -f db/init_postgres.sql
```

### 4. Generate Sample Data
```bash
# Generate customers
python streaming/generate_customers.py

# Fetch products (optional - uses FakeStore API)
python streaming/fetch_products.py
```

## 🚀 Running the System

### 1. Start the WebSocket Server
```bash
python streaming/server.py
```

### 2. Start the Event Simulator (in a new terminal)
```bash
python streaming/event_simulator.py
```

### 3. Launch the Dashboard
```bash
streamlit run dashboard/app_live.py
```

### 4. Run ML Analytics (optional)
```bash
python ml/predictor.py
```

## 📈 Dashboard Features

### Real-time Analytics
- **Live Data Updates**: Dashboard refreshes automatically every 5 seconds
- **Interactive Filters**: Filter by date range and action types
- **Customer Drill-down**: Select individual customers for detailed analysis

### Key Performance Indicators
- Total events and unique customers
- Revenue and average order value
- Conversion and abandonment rates

### Advanced Visualizations
- **Conversion Funnel**: Customer journey visualization
- **Seasonal Trends**: Multi-panel time-based analysis
- **Customer Behavior**: Age group and activity analysis
- **Product Performance**: Top products by views and revenue
- **Abandoned Cart Analysis**: Abandonment patterns and recommendations

## 🔍 Analytics Insights

### Customer Purchasing Patterns
- Identifies high-value customers
- Tracks customer activity over time
- Analyzes age group preferences
- Monitors customer lifetime value

### Seasonal Trends
- Peak activity hours and days
- Monthly purchasing patterns
- Time-based conversion rates
- Seasonal product preferences

### Abandoned Cart Characteristics
- Products most frequently abandoned
- Abandonment rate by customer segment
- Cart value analysis
- Recovery opportunity identification

### Conversion Rate Optimization
- Funnel analysis and bottlenecks
- A/B testing recommendations
- Customer segment targeting
- Product optimization suggestions

## 📊 Sample Insights

The system provides actionable insights such as:

- **"Peak activity occurs at 2 PM on Wednesdays"**
- **"Cart abandonment rate is 35% - implement recovery emails"**
- **"Product X has highest abandonment rate - review pricing"**
- **"Customers aged 26-35 have highest conversion rate"**

## 🔧 Configuration

### Database Configuration
Update database settings in:
- `streaming/server.py`
- `streaming/event_simulator.py`
- `streaming/generate_customers.py`
- `dashboard/app_live.py`
- `ml/predictor.py`

### Event Simulation
Modify simulation parameters in `streaming/event_simulator.py`:
- Event frequency
- Customer behavior patterns
- Product selection logic
- Historical data generation

## 📝 API Endpoints

### WebSocket Server
- **URL**: `ws://localhost:8765`
- **Protocol**: WebSocket
- **Events**: JSON formatted customer events

### Event Format
```json
{
  "event_id": "uuid",
  "customer_id": "123",
  "action": "add_to_cart",
  "product_title": "Product Name",
  "product_price": 29.99,
  "product_image": "image_url",
  "description": "Added Product Name to cart",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🧪 Testing

### Manual Testing
1. Start all components
2. Monitor dashboard for live updates
3. Verify data consistency across components
4. Test customer selection and filtering

### Data Validation
- Check event counts match across components
- Verify customer and product relationships
- Validate timestamp consistency
- Confirm conversion rate calculations

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database exists

2. **No Data in Dashboard**
   - Confirm event simulator is running
   - Check WebSocket server status
   - Verify database schema is initialized

3. **Dashboard Not Updating**
   - Check auto-refresh settings
   - Verify data cache settings
   - Monitor for errors in console

### Logs and Debugging
- WebSocket server logs connection events
- Event simulator shows event generation
- Dashboard displays data loading status
- ML analytics provides detailed output

## 🔮 Future Enhancements

- **Advanced ML Models**: Deep learning for better predictions
- **Real-time Alerts**: Notification system for anomalies
- **A/B Testing**: Built-in experimentation framework
- **API Integration**: Connect to real e-commerce platforms
- **Mobile Dashboard**: Responsive design for mobile devices
- **Export Features**: PDF reports and data export
- **User Authentication**: Multi-user support with roles

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Built with ❤️ for e-commerce analytics**
