# 🐳 E-commerce Customer Analytics - Docker Setup

This directory contains all the Docker configuration files needed to run the entire e-commerce analytics system on any PC with Docker installed.

## 🚀 Quick Start

### Prerequisites
- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **At least 4GB RAM** available for the containers

### 1. Clone the Repository
```bash
git clone <repository-url>
cd customer-stream-project
```

### 2. Start the Entire System
```bash
cd docker
docker-compose up -d
```

### 3. Access the Dashboard
Open your browser and go to: **http://localhost:8501**

## 📊 System Components

The Docker setup includes:

### 🗄️ **PostgreSQL Database** (`postgres`)
- **Port:** 5432
- **Database:** customer_events
- **Auto-initialized** with schema and sample data
- **Persistent storage** with Docker volumes

### 🔌 **WebSocket Server** (`websocket_server`)
- **Port:** 8765
- **Handles** real-time event streaming
- **Stores** events in PostgreSQL
- **Broadcasts** events to connected clients

### 🎲 **Event Simulator** (`event_simulator`)
- **Generates** realistic customer events
- **Actions:** add_to_cart, remove_from_cart, purchase_cart
- **Connects** to WebSocket server
- **Uses** FakeStore API for product data

### 📈 **Streamlit Dashboard** (`dashboard`)
- **Port:** 8501
- **Real-time analytics** with 5-second refresh
- **Advanced visualizations** and insights
- **ML-ready** architecture

### 🔧 **Database Initialization** (`db_init`)
- **Runs once** to set up database schema
- **Generates** 100 fake customers
- **Populates** product catalog

## 🔧 Configuration

### Environment Variables
All services use environment variables for configuration:

```yaml
DB_HOST: postgres          # Database host
DB_PORT: 5432             # Database port
DB_NAME: customer_events  # Database name
DB_USER: postgres         # Database user
DB_PASS: Rp123456         # Database password
WS_URL: ws://websocket_server:8765  # WebSocket URL
```

### Custom Configuration
Create a `.env` file in the docker directory to override defaults:

```env
DB_PASS=your_secure_password
WS_PORT=8765
```

## 📋 Available Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d postgres
docker-compose up -d dashboard
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f dashboard
docker-compose logs -f event_simulator
docker-compose logs -f websocket_server
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Rebuild Services
```bash
# Rebuild all services
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache dashboard
```

## 🔍 Monitoring

### Service Status
```bash
docker-compose ps
```

### Database Connection
```bash
# Connect to PostgreSQL
docker exec -it customer_events_db psql -U postgres -d customer_events

# View tables
\dt

# Check data
SELECT COUNT(*) FROM events;
SELECT COUNT(*) FROM customers;
```

### Health Checks
- **PostgreSQL:** Automatic health check every 10s
- **Services:** Dependencies ensure proper startup order
- **Dashboard:** Auto-refresh every 5 seconds

## 🛠️ Development

### Adding New Features
1. **Modify code** in the appropriate directory
2. **Rebuild** the service: `docker-compose build service_name`
3. **Restart** the service: `docker-compose restart service_name`

### Database Changes
1. **Update** `../db/init_postgres.sql`
2. **Rebuild** and restart: `docker-compose down && docker-compose up -d`

### Adding Dependencies
1. **Update** `../requirements.txt`
2. **Rebuild** services: `docker-compose build --no-cache`

## 📊 Dashboard Features

### Real-time Analytics
- **Key Metrics:** Total events, unique customers, revenue, conversion rates
- **Product Analysis:** Event frequency, performance, revenue analysis
- **Customer Behavior:** Age groups, top customers, activity patterns
- **Seasonal Trends:** Hourly, daily, monthly patterns
- **Abandoned Cart Analysis:** Removal patterns and insights

### Advanced Features
- **Net Purchase Logic:** `add_to_cart - remove_from_cart`
- **Accurate Conversion Rates:** Based on net purchases
- **Product Journey Tracking:** Complete lifecycle visualization
- **Real-time Updates:** 5-second refresh intervals

## 🔒 Security Notes

### Production Deployment
- **Change default passwords** in docker-compose.yml
- **Use secrets management** for sensitive data
- **Enable SSL/TLS** for database connections
- **Restrict network access** as needed

### Data Persistence
- **PostgreSQL data** is stored in Docker volumes
- **Backup strategy** should be implemented for production
- **Data retention** policies should be considered

## 🐛 Troubleshooting

### Common Issues

#### Dashboard Not Loading
```bash
# Check dashboard logs
docker-compose logs dashboard

# Restart dashboard
docker-compose restart dashboard
```

#### Database Connection Issues
```bash
# Check database status
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

#### No Data in Dashboard
```bash
# Check event simulator
docker-compose logs event_simulator

# Check WebSocket server
docker-compose logs websocket_server
```

#### Port Already in Use
```bash
# Check what's using the port
netstat -tulpn | grep :8501
netstat -tulpn | grep :8765
netstat -tulpn | grep :5432

# Stop conflicting services or change ports in docker-compose.yml
```

### Reset Everything
```bash
# Complete reset
docker-compose down -v
docker-compose up -d
```

## 📈 Performance

### Resource Requirements
- **Minimum:** 2GB RAM, 2 CPU cores
- **Recommended:** 4GB RAM, 4 CPU cores
- **Storage:** 10GB+ for database and logs

### Scaling
- **Horizontal scaling** possible for WebSocket server
- **Database clustering** for high availability
- **Load balancing** for dashboard access

## 🚀 Running on Different PCs

### Windows
1. Install Docker Desktop for Windows
2. Enable WSL2 backend (recommended)
3. Run the commands above

### macOS
1. Install Docker Desktop for Mac
2. Allocate at least 4GB RAM to Docker
3. Run the commands above

### Linux
1. Install Docker Engine and Docker Compose
2. Add your user to the docker group
3. Run the commands above

### Cloud Deployment
The same Docker setup can be deployed to:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** with Docker setup
5. **Submit** a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Analyzing! 🎉** 