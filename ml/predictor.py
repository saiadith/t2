import pandas as pd
import numpy as np
import psycopg2
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import os
warnings.filterwarnings('ignore')

class CustomerAnalytics:
    def __init__(self, db_config=None):
        if db_config is None:
            # Use environment variables for Docker
            db_config = {
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASS", "Rp123456"),
                "host": os.getenv("DB_HOST", "localhost"),
                "port": os.getenv("DB_PORT", "5432"),
                "dbname": os.getenv("DB_NAME", "customer_events"),
            }
        self.db_config = db_config
        self.conn = None
        self.customer_model = None
        self.conversion_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def load_data(self):
        """Load all relevant data from database"""
        if not self.connect_db():
            return None
            
        query = """
        SELECT 
            e.event_id,
            e.customer_id,
            e.product_id,
            e.product_title,
            e.product_price,
            e.action,
            e.timestamp,
            c.name as customer_name,
            c.age as customer_age,
            c.email as customer_email,
            p.category as product_category
        FROM events e
        LEFT JOIN customers c ON e.customer_id = c.customer_id
        LEFT JOIN products p ON e.product_id = p.product_id
        ORDER BY e.timestamp
        """
        
        df = pd.read_sql(query, self.conn)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def analyze_customer_patterns(self, df):
        """Analyze customer purchasing patterns"""
        print("=== CUSTOMER PURCHASING PATTERNS ===")
        
        # Customer activity analysis
        customer_activity = df.groupby('customer_id').agg({
            'event_id': 'count',
            'action': lambda x: (x == 'purchase_cart').sum(),
            'product_price': 'sum',
            'timestamp': ['min', 'max']
        }).round(2)
        
        customer_activity.columns = ['total_events', 'purchases', 'total_spent', 'first_activity', 'last_activity']
        customer_activity['avg_order_value'] = customer_activity['total_spent'] / customer_activity['purchases'].replace(0, 1)
        
        print(f"Total customers: {len(customer_activity)}")
        print(f"Active customers (with purchases): {len(customer_activity[customer_activity['purchases'] > 0])}")
        print(f"Average order value: ${customer_activity['avg_order_value'].mean():.2f}")
        print(f"Total revenue: ${customer_activity['total_spent'].sum():.2f}")
        
        return customer_activity
    
    def analyze_seasonal_trends(self, df):
        """Analyze seasonal trends in customer behavior"""
        print("\n=== SEASONAL TRENDS ANALYSIS ===")
        
        # Add time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['day_of_month'] = df['timestamp'].dt.day
        
        # Hourly patterns
        hourly_activity = df.groupby('hour')['event_id'].count()
        peak_hour = hourly_activity.idxmax()
        print(f"Peak activity hour: {peak_hour}:00 ({hourly_activity[peak_hour]} events)")
        
        # Daily patterns
        daily_activity = df.groupby('day_of_week')['event_id'].count()
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        peak_day = day_names[daily_activity.idxmax()]
        print(f"Peak activity day: {peak_day} ({daily_activity.max()} events)")
        
        # Monthly trends
        monthly_activity = df.groupby('month')['event_id'].count()
        peak_month = monthly_activity.idxmax()
        print(f"Peak activity month: {peak_month} ({monthly_activity[peak_month]} events)")
        
        # Purchase patterns by time
        purchase_hourly = df[df['action'] == 'purchase_cart'].groupby('hour')['event_id'].count()
        if not purchase_hourly.empty:
            peak_purchase_hour = purchase_hourly.idxmax()
            print(f"Peak purchase hour: {peak_purchase_hour}:00 ({purchase_hourly[peak_purchase_hour]} purchases)")
        
        return {
            'hourly_activity': hourly_activity,
            'daily_activity': daily_activity,
            'monthly_activity': monthly_activity,
            'purchase_hourly': purchase_hourly
        }
    
    def analyze_abandoned_carts(self, df):
        """Analyze abandoned cart characteristics"""
        print("\n=== ABANDONED CART ANALYSIS ===")
        
        # Identify customers with cart activity but no purchases
        cart_activity = df[df['action'].isin(['add_to_cart', 'remove_from_cart'])]
        purchase_activity = df[df['action'] == 'purchase_cart']
        
        customers_with_cart = set(cart_activity['customer_id'].unique())
        customers_with_purchase = set(purchase_activity['customer_id'].unique())
        abandoned_cart_customers = customers_with_cart - customers_with_purchase
        
        print(f"Customers with cart activity: {len(customers_with_cart)}")
        print(f"Customers who made purchases: {len(customers_with_purchase)}")
        print(f"Customers who abandoned carts: {len(abandoned_cart_customers)}")
        print(f"Cart abandonment rate: {len(abandoned_cart_customers)/len(customers_with_cart)*100:.1f}%")
        
        # Analyze abandoned cart characteristics
        abandoned_cart_data = df[df['customer_id'].isin(abandoned_cart_customers)]
        
        if not abandoned_cart_data.empty:
            # Products most abandoned
            abandoned_products = abandoned_cart_data[abandoned_cart_data['action'] == 'add_to_cart'].groupby('product_title')['event_id'].count().sort_values(ascending=False)
            print(f"\nTop 5 most abandoned products:")
            for i, (product, count) in enumerate(abandoned_products.head().items(), 1):
                print(f"{i}. {product}: {count} times")
            
            # Average cart value of abandoned carts
            abandoned_cart_values = abandoned_cart_data[abandoned_cart_data['action'] == 'add_to_cart']['product_price'].sum()
            print(f"\nTotal value of abandoned carts: ${abandoned_cart_values:.2f}")
        
        return {
            'abandoned_cart_customers': abandoned_cart_customers,
            'abandonment_rate': len(abandoned_cart_customers)/len(customers_with_cart)*100 if customers_with_cart else 0,
            'abandoned_products': abandoned_products if not abandoned_cart_data.empty else pd.Series(),
            'abandoned_cart_value': abandoned_cart_values if not abandoned_cart_data.empty else 0
        }
    
    def analyze_conversion_funnel(self, df):
        """Analyze conversion funnel and rates"""
        print("\n=== CONVERSION FUNNEL ANALYSIS ===")
        
        # Count events by type
        funnel_data = df.groupby('action')['event_id'].count().sort_values(ascending=False)
        
        print("Event counts by type:")
        for action, count in funnel_data.items():
            print(f"{action}: {count}")
        
        # Calculate conversion rates
        add_to_cart_count = funnel_data.get('add_to_cart', 0)
        purchase_count = funnel_data.get('purchase_cart', 0)
        
        if add_to_cart_count > 0:
            cart_to_purchase_rate = (purchase_count / add_to_cart_count) * 100
            print(f"\nCart to Purchase conversion rate: {cart_to_purchase_rate:.1f}%")
        
        # Customer-level conversion analysis
        customer_conversions = df.groupby('customer_id').agg({
            'action': lambda x: (x == 'add_to_cart').sum(),
            'purchase_cart': lambda x: (x == 'purchase_cart').sum()
        })
        
        customers_with_cart = len(customer_conversions[customer_conversions['action'] > 0])
        customers_with_purchase = len(customer_conversions[customer_conversions['purchase_cart'] > 0])
        
        if customers_with_cart > 0:
            customer_conversion_rate = (customers_with_purchase / customers_with_cart) * 100
            print(f"Customer conversion rate: {customer_conversion_rate:.1f}%")
        
        return {
            'funnel_data': funnel_data,
            'cart_to_purchase_rate': cart_to_purchase_rate if add_to_cart_count > 0 else 0,
            'customer_conversion_rate': customer_conversion_rate if customers_with_cart > 0 else 0
        }
    
    def build_customer_prediction_model(self, df):
        """Build ML model to predict customer purchase likelihood"""
        print("\n=== BUILDING CUSTOMER PREDICTION MODEL ===")
        
        # Prepare features
        customer_features = df.groupby('customer_id').agg({
            'event_id': 'count',
            'action': lambda x: (x == 'add_to_cart').sum(),
            'action_remove': lambda x: (x == 'remove_from_cart').sum(),
            'action_purchase': lambda x: (x == 'purchase_cart').sum(),
            'product_price': 'sum',
            'product_id': 'nunique',
            'timestamp': lambda x: (x.max() - x.min()).days
        }).fillna(0)
        
        customer_features.columns = ['total_events', 'add_to_cart_count', 'remove_from_cart_count', 
                                   'purchase_count', 'total_spent', 'unique_products', 'days_active']
        
        # Create target variable (1 if customer made purchase, 0 otherwise)
        customer_features['will_purchase'] = (customer_features['purchase_count'] > 0).astype(int)
        
        # Prepare training data
        X = customer_features.drop(['will_purchase', 'purchase_count'], axis=1)
        y = customer_features['will_purchase']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.customer_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.customer_model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.customer_model.predict(X_test_scaled)
        accuracy = self.customer_model.score(X_test_scaled, y_test)
        
        print(f"Model accuracy: {accuracy:.3f}")
        print("\nFeature importance:")
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.customer_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for _, row in feature_importance.iterrows():
            print(f"{row['feature']}: {row['importance']:.3f}")
        
        return {
            'model': self.customer_model,
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'X_test': X_test,
            'y_test': y_test
        }
    
    def predict_customer_purchase_likelihood(self, customer_id):
        """Predict purchase likelihood for a specific customer"""
        if self.customer_model is None:
            print("Model not trained. Please run build_customer_prediction_model first.")
            return None
        
        # Get customer features
        query = f"""
        SELECT 
            customer_id,
            COUNT(*) as total_events,
            SUM(CASE WHEN action = 'add_to_cart' THEN 1 ELSE 0 END) as add_to_cart_count,
            SUM(CASE WHEN action = 'remove_from_cart' THEN 1 ELSE 0 END) as remove_from_cart_count,
            SUM(CASE WHEN action = 'purchase_cart' THEN 1 ELSE 0 END) as purchase_count,
            SUM(product_price) as total_spent,
            COUNT(DISTINCT product_id) as unique_products,
            EXTRACT(DAY FROM (MAX(timestamp) - MIN(timestamp))) as days_active
        FROM events 
        WHERE customer_id = {customer_id}
        GROUP BY customer_id
        """
        
        customer_data = pd.read_sql(query, self.conn)
        
        if customer_data.empty:
            print(f"No data found for customer {customer_id}")
            return None
        
        # Prepare features
        features = customer_data.drop(['customer_id', 'purchase_count'], axis=1).fillna(0)
        features_scaled = self.scaler.transform(features)
        
        # Predict
        probability = self.customer_model.predict_proba(features_scaled)[0][1]
        
        return {
            'customer_id': customer_id,
            'purchase_probability': probability,
            'prediction': 'Likely to purchase' if probability > 0.5 else 'Unlikely to purchase'
        }
    
    def generate_insights_report(self, df):
        """Generate comprehensive insights report"""
        print("\n" + "="*50)
        print("COMPREHENSIVE CUSTOMER ANALYTICS REPORT")
        print("="*50)
        
        # Run all analyses
        customer_patterns = self.analyze_customer_patterns(df)
        seasonal_trends = self.analyze_seasonal_trends(df)
        abandoned_carts = self.analyze_abandoned_carts(df)
        conversion_funnel = self.analyze_conversion_funnel(df)
        
        # Build prediction model
        prediction_model = self.build_customer_prediction_model(df)
        
        # Generate recommendations
        print("\n=== RECOMMENDATIONS FOR IMPROVING CONVERSION RATES ===")
        
        if abandoned_carts['abandonment_rate'] > 20:
            print("⚠️  HIGH CART ABANDONMENT RATE DETECTED")
            print("Recommendations:")
            print("- Implement abandoned cart recovery emails")
            print("- Add exit-intent popups with discounts")
            print("- Simplify checkout process")
            print("- Add trust signals (security badges, reviews)")
        
        if conversion_funnel['cart_to_purchase_rate'] < 30:
            print("⚠️  LOW CART-TO-PURCHASE CONVERSION RATE")
            print("Recommendations:")
            print("- Offer free shipping threshold")
            print("- Add urgency (limited time offers)")
            print("- Implement guest checkout option")
            print("- Show social proof (recent purchases)")
        
        # Product recommendations
        if not abandoned_carts['abandoned_products'].empty:
            print("\n📦 PRODUCT OPTIMIZATION OPPORTUNITIES:")
            top_abandoned = abandoned_carts['abandoned_products'].head(3)
            for product, count in top_abandoned.items():
                print(f"- Review pricing/description for: {product}")
        
        return {
            'customer_patterns': customer_patterns,
            'seasonal_trends': seasonal_trends,
            'abandoned_carts': abandoned_carts,
            'conversion_funnel': conversion_funnel,
            'prediction_model': prediction_model
        }

# Example usage
if __name__ == "__main__":
    db_config = {
        "user": "postgres",
        "password": "Rp123456",
        "host": "localhost",
        "port": "5432",
        "dbname": "customer_events",
    }
    
    analytics = CustomerAnalytics(db_config)
    df = analytics.load_data()
    
    if df is not None and not df.empty:
        insights = analytics.generate_insights_report(df)
        print("\n✅ Analytics completed successfully!")
    else:
        print("❌ No data available for analysis. Please ensure the database is populated.")
