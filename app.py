import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from data_loader import EcommerceDataLoader
from business_metrics import EcommerceMetrics

# Configure the page
st.set_page_config(
    page_title="E-Commerce Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    
    .kpi-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .trend-positive {
        color: #28a745;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .trend-negative {
        color: #dc3545;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 400px;
    }
    
    .bottom-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .review-stars {
        color: #ffc107;
        font-size: 1.5rem;
    }
    
    .large-number {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

@st.cache_data
def load_data():
    """Load and cache the e-commerce data"""
    try:
        loader = EcommerceDataLoader("ecommerce_data")
        datasets = loader.load_all_datasets()
        
        # Create enhanced datasets
        sales_2023 = loader.create_sales_dataset(target_year=2023, order_status='delivered')
        sales_2022 = loader.create_sales_dataset(target_year=2022, order_status='delivered')
        
        sales_with_delivery = loader.add_delivery_metrics(sales_2023)
        sales_with_reviews = loader.get_review_data(sales_2023)
        sales_with_categories = loader.get_product_categories_data(sales_2023)
        sales_with_states = loader.get_customer_geographic_data(sales_2023)
        
        return {
            'sales_2023': sales_2023,
            'sales_2022': sales_2022,
            'sales_with_delivery': sales_with_delivery,
            'sales_with_reviews': sales_with_reviews,
            'sales_with_categories': sales_with_categories,
            'sales_with_states': sales_with_states
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def filter_data_by_date(data_dict, start_date, end_date):
    """Filter all datasets by date range"""
    filtered_data = {}
    
    for key, df in data_dict.items():
        if 'order_purchase_timestamp' in df.columns:
            # Convert timestamp to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(df['order_purchase_timestamp']):
                df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
            
            # Filter by date range
            mask = (df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) & \
                   (df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
            filtered_data[key] = df[mask].copy()
        else:
            filtered_data[key] = df.copy()
    
    return filtered_data

def format_currency(value):
    """Format currency values for display"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"

def create_kpi_card(title, value, trend_value, is_currency=True):
    """Create a KPI card with trend indicator"""
    if is_currency:
        formatted_value = format_currency(value)
    else:
        formatted_value = f"{value:,.0f}"
    
    trend_color = "trend-positive" if trend_value >= 0 else "trend-negative"
    trend_arrow = "↗" if trend_value >= 0 else "↘"
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-value">{formatted_value}</div>
        <div class="kpi-label">{title}</div>
        <div class="{trend_color}">{trend_arrow} {abs(trend_value):.2f}%</div>
    </div>
    """

def create_revenue_trend_chart(monthly_data, comparison_data=None):
    """Create revenue trend line chart with current and previous period"""
    fig = go.Figure()
    
    # Current period line
    fig.add_trace(go.Scatter(
        x=monthly_data['month'],
        y=monthly_data['revenue'],
        mode='lines+markers',
        name='2023',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    # Previous period line (dashed)
    if comparison_data is not None:
        fig.add_trace(go.Scatter(
            x=comparison_data['month'],
            y=comparison_data['revenue'],
            mode='lines+markers',
            name='2022',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Revenue Trend",
        xaxis_title="Month",
        yaxis_title="Revenue",
        template='plotly_white',
        hovermode='x unified',
        showlegend=True,
        margin=dict(l=0, r=0, t=40, b=0),
        height=350
    )
    
    # Format y-axis
    fig.update_yaxes(tickformat='$,.0s')
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    
    return fig

def create_category_bar_chart(category_data):
    """Create top 10 categories bar chart with blue gradient"""
    top_10 = category_data.head(10)
    
    # Create blue gradient colors
    colors = [f'rgba(31, 119, 180, {0.3 + 0.7 * (i / 9)})' for i in range(len(top_10))]
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_10['total_revenue'],
            y=top_10['product_category_name'],
            orientation='h',
            marker_color=colors,
            text=[format_currency(x) for x in top_10['total_revenue']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Categories by Revenue",
        xaxis_title="Revenue",
        yaxis_title="",
        template='plotly_white',
        margin=dict(l=0, r=0, t=40, b=0),
        height=350
    )
    
    fig.update_xaxes(tickformat='$,.0s')
    
    return fig

def create_us_choropleth_map(state_data):
    """Create US choropleth map for revenue by state"""
    fig = px.choropleth(
        state_data,
        locations='state',
        color='total_revenue',
        locationmode='USA-states',
        scope='usa',
        title='Revenue by State',
        color_continuous_scale='Blues',
        labels={'total_revenue': 'Revenue'}
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='albers usa'
        )
    )
    
    return fig

def create_delivery_satisfaction_chart(delivery_satisfaction):
    """Create delivery time vs satisfaction bar chart"""
    # Order categories properly
    ordered_categories = ['1-3 days', '4-7 days', '8+ days']
    delivery_satisfaction = delivery_satisfaction.set_index('delivery_category').reindex(ordered_categories).reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=delivery_satisfaction['delivery_category'],
            y=delivery_satisfaction['avg_rating'],
            marker_color='#1f77b4',
            text=delivery_satisfaction['avg_rating'].round(2),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        template='plotly_white',
        margin=dict(l=0, r=0, t=40, b=0),
        height=350,
        yaxis=dict(range=[0, 5])
    )
    
    return fig

def main():
    # Header section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="main-header">E-Commerce Business Dashboard</div>', unsafe_allow_html=True)
    
    with col2:
        # Date range filter
        current_year = 2023
        start_date = st.date_input("Start Date", datetime(current_year, 1, 1))
        end_date = st.date_input("End Date", datetime(current_year, 12, 31))
    
    st.markdown("---")
    
    # Load data
    data_dict = load_data()
    if data_dict is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    # Filter data by date range
    filtered_data = filter_data_by_date(data_dict, start_date, end_date)
    
    # Initialize metrics calculator
    metrics = EcommerceMetrics()
    
    # Calculate current period metrics
    current_metrics = metrics.calculate_revenue_metrics(
        filtered_data['sales_2023'], 
        data_dict['sales_2022']
    )
    
    monthly_trends = metrics.calculate_monthly_trends(filtered_data['sales_2023'])
    category_performance = metrics.calculate_product_performance(filtered_data['sales_with_categories'])
    state_performance = metrics.calculate_geographic_performance(filtered_data['sales_with_states'])
    delivery_metrics = metrics.calculate_delivery_performance(filtered_data['sales_with_delivery'])
    satisfaction_metrics = metrics.calculate_customer_satisfaction(filtered_data['sales_with_reviews'])
    
    # Combine delivery and review data for analysis
    combined_data = filtered_data['sales_with_delivery'].merge(
        filtered_data['sales_with_reviews'][['order_id', 'review_score']], 
        on='order_id', how='inner'
    )
    delivery_satisfaction = metrics.analyze_satisfaction_vs_delivery(combined_data)
    
    # KPI Row
    st.subheader("Key Performance Indicators")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(create_kpi_card(
            "Total Revenue",
            current_metrics['total_revenue'],
            current_metrics.get('revenue_growth_rate', 0)
        ), unsafe_allow_html=True)
    
    with kpi_col2:
        # Calculate monthly growth from trends
        avg_monthly_growth = monthly_trends['revenue_growth'].mean() if not monthly_trends['revenue_growth'].isna().all() else 0
        st.markdown(create_kpi_card(
            "Monthly Growth",
            avg_monthly_growth,
            avg_monthly_growth,
            is_currency=False
        ), unsafe_allow_html=True)
    
    with kpi_col3:
        st.markdown(create_kpi_card(
            "Average Order Value",
            current_metrics['average_order_value'],
            current_metrics.get('aov_growth_rate', 0)
        ), unsafe_allow_html=True)
    
    with kpi_col4:
        st.markdown(create_kpi_card(
            "Total Orders",
            current_metrics['total_orders'],
            current_metrics.get('order_growth_rate', 0),
            is_currency=False
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Grid (2x2)
    st.subheader("Performance Analytics")
    chart_row1_col1, chart_row1_col2 = st.columns(2)
    
    with chart_row1_col1:
        # Revenue trend chart
        monthly_2022 = metrics.calculate_monthly_trends(data_dict['sales_2022'])
        revenue_chart = create_revenue_trend_chart(monthly_trends, monthly_2022)
        st.plotly_chart(revenue_chart, use_container_width=True)
    
    with chart_row1_col2:
        # Top 10 categories bar chart
        category_chart = create_category_bar_chart(category_performance)
        st.plotly_chart(category_chart, use_container_width=True)
    
    chart_row2_col1, chart_row2_col2 = st.columns(2)
    
    with chart_row2_col1:
        # US choropleth map
        us_map = create_us_choropleth_map(state_performance)
        st.plotly_chart(us_map, use_container_width=True)
    
    with chart_row2_col2:
        # Delivery satisfaction chart
        delivery_chart = create_delivery_satisfaction_chart(delivery_satisfaction)
        st.plotly_chart(delivery_chart, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bottom Row (2 cards)
    st.subheader("Customer Experience")
    bottom_col1, bottom_col2 = st.columns(2)
    
    with bottom_col1:
        # Average delivery time card
        delivery_trend = 0  # Calculate trend if comparison data available
        avg_delivery = delivery_metrics['average_delivery_days']
        trend_color = "trend-positive" if delivery_trend <= 0 else "trend-negative"
        trend_arrow = "↗" if delivery_trend >= 0 else "↘"
        
        st.markdown(f"""
        <div class="bottom-card">
            <div class="large-number">{avg_delivery:.1f} days</div>
            <div class="kpi-label">Average Delivery Time</div>
            <div class="{trend_color}">{trend_arrow} {abs(delivery_trend):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with bottom_col2:
        # Review score card
        avg_rating = satisfaction_metrics['average_rating']
        full_stars = int(avg_rating)
        half_star = 1 if avg_rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars_html = "★" * full_stars
        if half_star:
            stars_html += "☆"
        stars_html += "☆" * empty_stars
        
        st.markdown(f"""
        <div class="bottom-card">
            <div class="large-number">{avg_rating:.1f}</div>
            <div class="review-stars">{stars_html}</div>
            <div class="subtitle">Average Review Score</div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()