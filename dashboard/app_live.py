import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
from streamlit_autorefresh import st_autorefresh
import numpy as np
from datetime import datetime, timedelta
import psycopg2
import os

st_autorefresh(interval=5000, key="datarefresh")  # refresh every 5 seconds

# ---------------------- CONFIG ----------------------
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "Rp123456")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "customer_events")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# ---------------------- DATABASE CLEAR FUNCTION ----------------------
def clear_database():
    """Clear all events from the database"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("DELETE FROM events")
        conn.commit()
        cur.close()
        conn.close()
        st.success("✅ Database cleared successfully! All events have been reset to 0.")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error clearing database: {e}")

# ---------------------- APP TITLE ----------------------
st.set_page_config(page_title="E-commerce Customer Analytics Dashboard", layout="wide")
st.title("🛍️ E-commerce Customer Analytics Dashboard")
st.markdown("**Real-time analysis of customer purchasing patterns, seasonal trends, and abandoned cart characteristics**")

# ---------------------- LOAD DATA ----------------------
@st.cache_data(ttl=5)  # Cache for 5 seconds for better real-time updates
def load_data():
    query = """
        SELECT 
            e.event_id,
            e.customer_id, 
            e.product_id,
            COALESCE(e.product_title, p.title) as product_title, 
            COALESCE(e.product_price, p.price) as product_price,
            e.action, 
            e.timestamp,
            c.name as customer_name,
            c.age as customer_age,
            c.email as customer_email,
            p.category as product_category
        FROM events e
        LEFT JOIN customers c ON e.customer_id = c.customer_id
        LEFT JOIN products p ON e.product_id = p.product_id
        ORDER BY e.timestamp DESC
    """
    try:
        df = pd.read_sql(query, engine)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Fill missing customer names
            df['customer_name'] = df['customer_name'].fillna(f'Customer {df["customer_id"]}')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

with st.spinner("Loading data..."):
    df = load_data()

if df.empty:
    st.warning("No data available. Please ensure the database is populated and the streaming system is running.")
    st.stop()

# ---------------------- SIDEBAR FILTERS ----------------------
st.sidebar.header("📊 Filters")

# Database Clear Button
st.sidebar.markdown("---")
st.sidebar.subheader("🗄️ Database Management")
if st.sidebar.button("🗑️ Clear All Events", type="primary"):
    clear_database()

# Date range filter
if not df.empty:
    min_date = df['timestamp'].min()
    max_date = df['timestamp'].max()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date()
    )
    
    # Filter data by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[
            (df['timestamp'].dt.date >= start_date) & 
            (df['timestamp'].dt.date <= end_date)
        ]
    else:
        df_filtered = df
else:
    df_filtered = df

# Action type filter
if not df_filtered.empty:
    action_types = df_filtered['action'].unique()
    selected_actions = st.sidebar.multiselect(
        "Action Types",
        options=action_types,
        default=action_types
    )
    
    if selected_actions:
        df_filtered = df_filtered[df_filtered['action'].isin(selected_actions)]

# ---------------------- KEY METRICS ----------------------
st.header("📈 Key Performance Metrics")

if not df_filtered.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(df_filtered)
        st.metric("Total Events", f"{total_events:,}")
    
    with col2:
        unique_customers = df_filtered['customer_id'].nunique()
        st.metric("Unique Customers", f"{unique_customers:,}")
    
    with col3:
        # Fix revenue calculation - sum product prices from add_to_cart events for customers who purchased
        purchase_customers = df_filtered[df_filtered['action'] == 'purchase_cart']['customer_id'].unique()
        if len(purchase_customers) > 0:
            # Get all add_to_cart events for customers who made purchases
            purchase_events = df_filtered[
                (df_filtered['action'] == 'add_to_cart') & 
                (df_filtered['customer_id'].isin(purchase_customers))
            ]
            total_revenue = purchase_events['product_price'].sum()
        else:
            total_revenue = 0
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with col4:
        # Fix average order value calculation
        if len(purchase_customers) > 0:
            avg_order_value = total_revenue / len(purchase_customers)
        else:
            avg_order_value = 0
        st.metric("Avg Order Value", f"${avg_order_value:.2f}")

# ---------------------- NEW ANALYTICS GRAPHS ----------------------
st.header("📊 Advanced Analytics")

if not df_filtered.empty:
    # 1. Product Event Frequency Chart
    st.subheader("1. Product Event Frequency Analysis")
    
    # Event type selector
    event_type = st.selectbox(
        "Select Event Type",
        options=df_filtered['action'].unique(),
        key="event_type_selector"
    )
    
    # Filter data for selected event type
    if event_type == 'purchase_cart':
        # For purchase_cart, show net purchased products (add_to_cart - remove_from_cart)
        product_net_purchases = df_filtered.groupby('product_title').apply(
            lambda x: len(x[x['action'] == 'add_to_cart']) - len(x[x['action'] == 'remove_from_cart'])
        ).reset_index(name='frequency')
        product_net_purchases = product_net_purchases[product_net_purchases['frequency'] > 0].sort_values('frequency', ascending=False)
        event_data = product_net_purchases
    else:
        # For other actions, use normal filtering
        event_data = df_filtered[df_filtered['action'] == event_type]
        if not event_data.empty:
            # Count events per product
            product_counts = event_data.groupby('product_title').size().reset_index(name='frequency')
            product_counts = product_counts.sort_values('frequency', ascending=False)
            event_data = product_counts
    
    if not event_data.empty:
        # Update title based on action type
        if event_type == 'purchase_cart':
            title = "Net Purchased Products (add_to_cart - remove_from_cart)"
        else:
            title = f"Frequency of '{event_type}' Events by Product"
        
        fig_product_events = px.bar(
            event_data,
            x='product_title',
            y='frequency',
            title=title,
            labels={'product_title': 'Product', 'frequency': 'Frequency Count'}
        )
        fig_product_events.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_product_events, use_container_width=True)
    else:
        if event_type == 'purchase_cart':
            st.info("No net purchased products found (add_to_cart - remove_from_cart <= 0 for all products)")
        else:
            st.info(f"No data available for '{event_type}' events")

    # 2. Product-specific Event Analysis
    st.subheader("2. Product-specific Event Analysis")
    
    # Product selector
    available_products = df_filtered['product_title'].unique()
    selected_product = st.selectbox(
        "Select Product",
        options=available_products,
        key="product_selector"
    )
    
    # Filter data for selected product
    product_data = df_filtered[df_filtered['product_title'] == selected_product]
    
    if not product_data.empty:
        # Count events per action type for selected product
        action_counts = product_data.groupby('action').size().reset_index(name='frequency')
        
        # Calculate net purchased count for this specific product (add_to_cart - remove_from_cart)
        add_to_cart_count = len(product_data[product_data['action'] == 'add_to_cart'])
        remove_from_cart_count = len(product_data[product_data['action'] == 'remove_from_cart'])
        net_purchased_count = add_to_cart_count - remove_from_cart_count
        
        # Add net purchased count to the action counts
        if net_purchased_count > 0:
            purchased_row = pd.DataFrame({
                'action': ['purchased'],
                'frequency': [net_purchased_count]
            })
            action_counts = pd.concat([action_counts, purchased_row], ignore_index=True)
        
        fig_product_actions = px.bar(
            action_counts,
            x='action',
            y='frequency',
            title=f"Event Frequency for '{selected_product}'",
            labels={'action': 'Event Type', 'frequency': 'Frequency Count'}
        )
        st.plotly_chart(fig_product_actions, use_container_width=True)
    else:
        st.info(f"No data available for '{selected_product}'")

    # 3. Customer Top Products Analysis
    st.subheader("3. Customer Top Products Analysis")
    
    # Customer selector - use customer names for clarity
    customer_data_products = df_filtered[['customer_id', 'customer_name']].drop_duplicates()
    customer_data_products = customer_data_products.dropna()
    
    if len(customer_data_products) > 0:
        # Create a mapping of customer names to IDs for the dropdown
        customer_options_products = {}
        for _, row in customer_data_products.iterrows():
            customer_name = row['customer_name'] if pd.notna(row['customer_name']) else f"Customer {row['customer_id']}"
            customer_options_products[customer_name] = row['customer_id']
        
        # Sort customer names alphabetically for better UX
        sorted_customer_names_products = sorted(customer_options_products.keys())
        
        selected_customer_name_products = st.selectbox(
            "Select Customer",
            options=sorted_customer_names_products,
            key="customer_selector"
        )
        
        selected_customer_id_products = customer_options_products[selected_customer_name_products]
        
        # Get customer's purchase data
        customer_purchases = df_filtered[
            (df_filtered['customer_id'] == selected_customer_id_products) & 
            (df_filtered['action'] == 'add_to_cart')
        ]
        
        if not customer_purchases.empty:
            # Count purchases per product for selected customer
            customer_product_counts = customer_purchases.groupby('product_title').size().reset_index(name='frequency')
            customer_product_counts = customer_product_counts.sort_values('frequency', ascending=False).head(5)
            
            fig_customer_products = px.bar(
                customer_product_counts,
                x='product_title',
                y='frequency',
                title=f"Top 5 Products Purchased by {selected_customer_name_products}",
                labels={'product_title': 'Product', 'frequency': 'Purchase Frequency'}
            )
            fig_customer_products.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig_customer_products, use_container_width=True)
        else:
            st.info(f"No purchase data available for {selected_customer_name_products}")
    else:
        st.info("No customers found in data.")

    # 4. Seasonal Trends Analysis
    st.subheader("4. Seasonal Trends Analysis")
    
    # Define seasons
    def get_season(date):
        month = date.month
        day = date.day
        
        if (month == 12 and day >= 21) or (month == 1) or (month == 2) or (month == 3 and day <= 19):
            return "Winter"
        elif (month == 3 and day >= 20) or (month == 4) or (month == 5) or (month == 6 and day <= 20):
            return "Spring"
        elif (month == 6 and day >= 21) or (month == 7) or (month == 8) or (month == 9 and day <= 21):
            return "Summer"
        else:
            return "Autumn"
    
    # Add season to dataframe
    df_filtered['season'] = df_filtered['timestamp'].apply(get_season)
    
    # Product selector for seasonal analysis
    seasonal_product = st.selectbox(
        "Select Product for Seasonal Analysis",
        options=available_products,
        key="seasonal_product_selector"
    )
    
    # Filter data for selected product and purchases
    seasonal_data = df_filtered[
        (df_filtered['product_title'] == seasonal_product) & 
        (df_filtered['action'] == 'add_to_cart')
    ]
    
    if not seasonal_data.empty:
        # Count purchases per season for selected product
        seasonal_counts = seasonal_data.groupby('season').size().reset_index(name='purchase_count')
        
        # Define season order
        season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
        seasonal_counts['season'] = pd.Categorical(seasonal_counts['season'], categories=season_order, ordered=True)
        seasonal_counts = seasonal_counts.sort_values('season')
        
        fig_seasonal = px.bar(
            seasonal_counts,
            x='season',
            y='purchase_count',
            title=f"Seasonal Purchase Trends for '{seasonal_product}'",
            labels={'season': 'Season', 'purchase_count': 'Number of Purchases'}
        )
        st.plotly_chart(fig_seasonal, use_container_width=True)
    else:
        st.info(f"No purchase data available for '{seasonal_product}'")

# ---------------------- PRODUCT PURCHASE TIMELINE ----------------------
st.header("📈 Product Purchase Timeline")

if not df_filtered.empty:
    # Product selector for timeline analysis
    available_products = df_filtered['product_title'].unique()
    selected_product_timeline = st.selectbox(
        "Select Product for Purchase Timeline",
        options=available_products,
        key="timeline_product_selector"
    )
    
    # Filter data for selected product
    product_timeline_data = df_filtered[df_filtered['product_title'] == selected_product_timeline]
    
    if not product_timeline_data.empty:
        # Calculate cumulative purchases over time
        # Group by timestamp and calculate net purchases (add_to_cart - remove_from_cart)
        timeline_data = []
        cumulative_purchases = 0
        
        # Sort by timestamp
        sorted_data = product_timeline_data.sort_values('timestamp')
        
        for _, row in sorted_data.iterrows():
            if row['action'] == 'add_to_cart':
                cumulative_purchases += 1
            elif row['action'] == 'remove_from_cart':
                cumulative_purchases -= 1
            
            timeline_data.append({
                'timestamp': row['timestamp'],
                'purchases': cumulative_purchases
            })
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            
            fig_timeline = px.line(
                timeline_df,
                x='timestamp',
                y='purchases',
                title=f"Purchase Timeline for '{selected_product_timeline}'",
                labels={'timestamp': 'Time', 'purchases': 'Purchases'},
                markers=True
            )
            
            # Update layout for better readability
            fig_timeline.update_layout(
                xaxis_title="Time",
                yaxis_title="Purchases",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Show summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                final_purchases = timeline_df['purchases'].iloc[-1] if not timeline_df.empty else 0
                st.metric("Final Purchase Count", final_purchases)
            
            with col2:
                max_purchases = timeline_df['purchases'].max() if not timeline_df.empty else 0
                st.metric("Peak Purchase Count", max_purchases)
            
            with col3:
                total_adds = len(product_timeline_data[product_timeline_data['action'] == 'add_to_cart'])
                total_removes = len(product_timeline_data[product_timeline_data['action'] == 'remove_from_cart'])
                st.metric("Add to Cart Events", total_adds)
        else:
            st.info(f"No timeline data available for '{selected_product_timeline}'")
    else:
        st.info(f"No data available for '{selected_product_timeline}'")

# ---------------------- CUSTOMER BEHAVIOR ANALYSIS ----------------------
st.header("👥 Customer Behavior Analysis")

if not df_filtered.empty:
    # Customer activity by age group
    df_filtered['age_group'] = pd.cut(df_filtered['customer_age'], 
                                     bins=[0, 25, 35, 45, 55, 100], 
                                     labels=['18-25', '26-35', '36-45', '46-55', '55+'])
    
    age_activity = df_filtered.groupby('age_group', observed=True)['event_id'].count().reset_index()
    
    fig_age = px.bar(age_activity, x='age_group', y='event_id', 
                     title="Customer Activity by Age Group",
                     labels={'event_id': 'Number of Events', 'age_group': 'Age Group'})
    st.plotly_chart(fig_age, use_container_width=True)
    
    # Top customers by activity
    top_customers = df_filtered.groupby(['customer_id', 'customer_name']).agg({
        'event_id': 'count',
        'action': lambda x: (x == 'purchase_cart').sum()
    }).reset_index()
    
    # Calculate total spent for each customer
    customer_spending = df_filtered[df_filtered['action'] == 'add_to_cart'].groupby('customer_id')['product_price'].sum().reset_index()
    customer_spending.columns = ['customer_id', 'total_spent']
    
    # Merge with top customers
    top_customers = top_customers.merge(customer_spending, on='customer_id', how='left')
    top_customers['total_spent'] = top_customers['total_spent'].fillna(0)
    
    top_customers.columns = ['Customer ID', 'Customer Name', 'Total Events', 'Purchases', 'Total Spent']
    top_customers = top_customers.sort_values('Total Events', ascending=False).head(10)
    
    st.subheader("Top 10 Most Active Customers")
    st.dataframe(top_customers, use_container_width=True)

# ---------------------- PRODUCT ANALYSIS ----------------------
st.header("📦 Product Performance Analysis")

if not df_filtered.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        # Most viewed products
        product_views = df_filtered.groupby('product_title')['event_id'].count().sort_values(ascending=False).head(10)
        
        fig_products = px.bar(x=product_views.values, y=product_views.index, orientation='h',
                             title="Top 10 Most Viewed Products",
                             labels={'x': 'Number of Events', 'y': 'Product'})
        st.plotly_chart(fig_products, use_container_width=True)
    
    with col2:
        # Products with highest revenue - calculate based on add_to_cart events for customers who purchased
        purchase_customers = df_filtered[df_filtered['action'] == 'purchase_cart']['customer_id'].unique()
        if len(purchase_customers) > 0:
            # Get add_to_cart events for customers who made purchases
            purchased_products = df_filtered[
                (df_filtered['action'] == 'add_to_cart') & 
                (df_filtered['customer_id'].isin(purchase_customers))
            ]
            product_revenue = purchased_products.groupby('product_title')['product_price'].sum().sort_values(ascending=False).head(10)
            
            if not product_revenue.empty:
                fig_revenue = px.bar(x=product_revenue.values, y=product_revenue.index, orientation='h',
                                    title="Top 10 Products by Revenue",
                                    labels={'x': 'Revenue ($)', 'y': 'Product'})
                st.plotly_chart(fig_revenue, use_container_width=True)
            else:
                st.info("No purchase data available for revenue analysis")
        else:
            st.info("No purchase data available for revenue analysis")

# ---------------------- ABANDONED CART ANALYSIS ----------------------
st.header("🛒 Abandoned Cart Analysis")

if not df_filtered.empty:
    # Identify abandoned cart customers (customers with cart activity but no purchases)
    cart_activity = df_filtered[df_filtered['action'].isin(['add_to_cart', 'remove_from_cart'])]
    purchase_activity = df_filtered[df_filtered['action'] == 'purchase_cart']
    
    customers_with_cart = set(cart_activity['customer_id'].unique())
    customers_with_purchase = set(purchase_activity['customer_id'].unique())
    abandoned_cart_customers = customers_with_cart - customers_with_purchase
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Customers with Cart Activity", len(customers_with_cart))
        st.metric("Customers who Purchased", len(customers_with_purchase))
        # Only show abandoned customers if there are any
        if len(abandoned_cart_customers) > 0:
            st.metric("Customers who Abandoned", len(abandoned_cart_customers))
    
    with col2:
        # Top 10 removed products analysis
        removed_products = df_filtered[df_filtered['action'] == 'remove_from_cart'].groupby('product_title').size().sort_values(ascending=False).head(10)
        
        if not removed_products.empty:
            # Calculate percentage of removed products of total events (fixed calculation)
            total_events = len(df_filtered)
            removed_events = len(df_filtered[df_filtered['action'] == 'remove_from_cart'])
            removed_percentage = (removed_events / total_events) * 100 if total_events > 0 else 0
            
            # Cap the percentage at 100% to avoid unrealistic values
            removed_percentage = min(removed_percentage, 100.0)
            
            st.metric("Removed Products % of Total Events", f"{removed_percentage:.1f}%")
            
            fig_removed = px.bar(x=removed_products.values, y=removed_products.index, orientation='h',
                                title="Top 10 Most Removed Products",
                                labels={'x': 'Times Removed', 'y': 'Product'})
            st.plotly_chart(fig_removed, use_container_width=True)
        else:
            st.info("No removed products data available")

# ---------------------- REAL-TIME CUSTOMER ACTIVITY ----------------------
st.header("⚡ Real-Time Customer Activity")

if not df_filtered.empty:
    # Get unique customers with their names
    customer_data = df_filtered[['customer_id', 'customer_name']].drop_duplicates()
    customer_data = customer_data.dropna()
    
    if len(customer_data) > 0:
        # Create a mapping of customer names to IDs for the dropdown
        customer_options = {}
        for _, row in customer_data.iterrows():
            customer_name = row['customer_name'] if pd.notna(row['customer_name']) else f"Customer {row['customer_id']}"
            customer_options[customer_name] = row['customer_id']
        
        # Sort customer names alphabetically for better UX
        sorted_customer_names = sorted(customer_options.keys())
        
        selected_customer_name = st.selectbox("Select Customer for Detailed View", sorted_customer_names)
        selected_customer_id = customer_options[selected_customer_name]
        
        # Filter for selected customer
        cust_df = df_filtered[df_filtered["customer_id"] == selected_customer_id]
        
        if not cust_df.empty:
            # Customer summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Customer", selected_customer_name)
            
            with col2:
                total_events = len(cust_df)
                st.metric("Total Events", total_events)
            
            with col3:
                # Calculate total spent for this customer from add_to_cart events
                customer_add_to_cart = cust_df[cust_df['action'] == 'add_to_cart']
                total_spent = customer_add_to_cart['product_price'].sum()
                st.metric("Total Spent", f"${total_spent:.2f}")
            
            # Customer activity timeline
            agg = cust_df.groupby(["product_title", "action"]).size().reset_index(name="count")
            
            if not agg.empty:
                # Sort products by total actions descending for better graph ordering
                total_actions = agg.groupby("product_title")["count"].sum().sort_values(ascending=False)
                agg["product_title"] = pd.Categorical(agg["product_title"], categories=total_actions.index, ordered=True)
                
                fig_customer = px.bar(
                    agg,
                    x="product_title",
                    y="count",
                    color="action",
                    barmode="group",
                    title=f"Actions by {selected_customer_name} on Products",
                    labels={"product_title": "Product", "count": "Number of Actions", "action": "Action Type"}
                )
                fig_customer.update_layout(xaxis_tickangle=45)
                st.plotly_chart(fig_customer, use_container_width=True)
        else:
            st.warning("No activity found for this customer.")
    else:
        st.warning("No customers found in data.")

# ---------------------- RECOMMENDATIONS ----------------------
st.header("💡 Insights & Recommendations")

if not df_filtered.empty:
    # Calculate key metrics for recommendations
    add_to_cart_count = len(df_filtered[df_filtered['action'] == 'add_to_cart'])
    purchase_count = len(df_filtered[df_filtered['action'] == 'purchase_cart'])
    remove_count = len(df_filtered[df_filtered['action'] == 'remove_from_cart'])
    
    # Calculate net purchased products (add_to_cart - remove_from_cart)
    net_purchased_count = add_to_cart_count - remove_count
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Key Insights")
        
        if add_to_cart_count > 0:
            # Updated conversion rate: (add_to_cart - remove_from_cart) / add_to_cart
            conversion_rate = (net_purchased_count / add_to_cart_count) * 100
            st.write(f"**Conversion Rate:** {conversion_rate:.1f}%")
            
            if conversion_rate < 30:
                st.warning("⚠️ Low conversion rate detected")
            elif conversion_rate > 50:
                st.success("✅ Good conversion rate")
        
        # Show net purchased products count
        st.write(f"**Net Products Purchased:** {net_purchased_count:,}")
    
    with col2:
        st.subheader("📋 Recommendations")
        
        if add_to_cart_count > 0 and (net_purchased_count / add_to_cart_count) < 0.3:
            st.write("**To improve conversion rates:**")
            st.write("- Implement abandoned cart recovery emails")
            st.write("- Add exit-intent popups with discounts")
            st.write("- Simplify checkout process")
            st.write("- Offer free shipping threshold")
        
        if remove_count > 0:
            st.write("**To reduce product removals:**")
            st.write("- Improve product descriptions and images")
            st.write("- Add customer reviews and ratings")
            st.write("- Offer better pricing or discounts")
            st.write("- Improve product recommendations")

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown("*Dashboard updates every 5 seconds. Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")
