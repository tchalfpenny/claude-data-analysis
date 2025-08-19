"""
Business metrics calculation module for e-commerce analysis.

This module contains functions to calculate key business metrics such as revenue,
growth rates, customer satisfaction, and operational performance indicators.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class EcommerceMetrics:
    """
    A class to calculate and visualize e-commerce business metrics.
    
    This class provides methods to compute key performance indicators (KPIs)
    and create visualizations for business analysis.
    """
    
    def __init__(self):
        """Initialize the metrics calculator."""
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'neutral': '#6c757d'
        }
    
    def calculate_revenue_metrics(self, sales_data: pd.DataFrame, 
                                comparison_data: pd.DataFrame = None) -> Dict:
        """
        Calculate revenue-related metrics.
        
        Args:
            sales_data (pd.DataFrame): Current period sales data
            comparison_data (pd.DataFrame, optional): Previous period for comparison
            
        Returns:
            Dict: Revenue metrics including total revenue, growth rate, etc.
        """
        metrics = {}
        
        # Current period metrics
        metrics['total_revenue'] = sales_data['price'].sum()
        metrics['total_orders'] = sales_data['order_id'].nunique()
        metrics['total_items'] = len(sales_data)
        metrics['average_order_value'] = sales_data.groupby('order_id')['price'].sum().mean()
        metrics['average_item_price'] = sales_data['price'].mean()
        
        # Comparison metrics if previous period data provided
        if comparison_data is not None:
            prev_revenue = comparison_data['price'].sum()
            prev_orders = comparison_data['order_id'].nunique()
            prev_aov = comparison_data.groupby('order_id')['price'].sum().mean()
            
            metrics['revenue_growth_rate'] = ((metrics['total_revenue'] - prev_revenue) / prev_revenue) * 100
            metrics['order_growth_rate'] = ((metrics['total_orders'] - prev_orders) / prev_orders) * 100
            metrics['aov_growth_rate'] = ((metrics['average_order_value'] - prev_aov) / prev_aov) * 100
            
            metrics['previous_revenue'] = prev_revenue
            metrics['previous_orders'] = prev_orders
            metrics['previous_aov'] = prev_aov
        
        return metrics
    
    def calculate_monthly_trends(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate monthly revenue trends and growth rates.
        
        Args:
            sales_data (pd.DataFrame): Sales data with month column
            
        Returns:
            pd.DataFrame: Monthly metrics with growth rates
        """
        monthly_metrics = sales_data.groupby('month').agg({
            'price': 'sum',
            'order_id': 'nunique'
        }).reset_index()
        
        monthly_metrics.columns = ['month', 'revenue', 'orders']
        monthly_metrics['aov'] = sales_data.groupby('month')['price'].sum() / sales_data.groupby('month')['order_id'].nunique()
        
        # Calculate month-over-month growth rates
        monthly_metrics['revenue_growth'] = monthly_metrics['revenue'].pct_change() * 100
        monthly_metrics['order_growth'] = monthly_metrics['orders'].pct_change() * 100
        monthly_metrics['aov_growth'] = monthly_metrics['aov'].pct_change() * 100
        
        return monthly_metrics
    
    def calculate_product_performance(self, sales_with_categories: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate product category performance metrics.
        
        Args:
            sales_with_categories (pd.DataFrame): Sales data with product categories
            
        Returns:
            pd.DataFrame: Product category performance metrics
        """
        category_metrics = sales_with_categories.groupby('product_category_name').agg({
            'price': ['sum', 'mean', 'count'],
            'order_id': 'nunique'
        }).round(2)
        
        # Flatten column names
        category_metrics.columns = ['total_revenue', 'avg_price', 'total_items', 'unique_orders']
        category_metrics = category_metrics.reset_index()
        
        # Calculate additional metrics
        category_metrics['revenue_share'] = (category_metrics['total_revenue'] / 
                                           category_metrics['total_revenue'].sum() * 100).round(2)
        
        category_metrics['items_per_order'] = (category_metrics['total_items'] / 
                                             category_metrics['unique_orders']).round(2)
        
        return category_metrics.sort_values('total_revenue', ascending=False)
    
    def calculate_geographic_performance(self, sales_with_states: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate performance metrics by geographic region (state).
        
        Args:
            sales_with_states (pd.DataFrame): Sales data with customer state information
            
        Returns:
            pd.DataFrame: Geographic performance metrics
        """
        state_metrics = sales_with_states.groupby('customer_state').agg({
            'price': 'sum',
            'order_id': 'nunique',
            'customer_id': 'nunique'
        }).reset_index()
        
        state_metrics.columns = ['state', 'total_revenue', 'total_orders', 'unique_customers']
        
        # Calculate additional metrics
        state_metrics['revenue_per_customer'] = (state_metrics['total_revenue'] / 
                                               state_metrics['unique_customers']).round(2)
        
        state_metrics['orders_per_customer'] = (state_metrics['total_orders'] / 
                                              state_metrics['unique_customers']).round(2)
        
        state_metrics['revenue_share'] = (state_metrics['total_revenue'] / 
                                        state_metrics['total_revenue'].sum() * 100).round(2)
        
        return state_metrics.sort_values('total_revenue', ascending=False)
    
    def calculate_customer_satisfaction(self, sales_with_reviews: pd.DataFrame) -> Dict:
        """
        Calculate customer satisfaction metrics based on review scores.
        
        Args:
            sales_with_reviews (pd.DataFrame): Sales data with review scores
            
        Returns:
            Dict: Customer satisfaction metrics
        """
        # Remove duplicates to get unique orders
        unique_orders = sales_with_reviews[['order_id', 'review_score']].drop_duplicates()
        
        metrics = {
            'average_rating': unique_orders['review_score'].mean(),
            'total_reviews': len(unique_orders),
            'rating_distribution': unique_orders['review_score'].value_counts().sort_index(),
            'satisfaction_rate': (unique_orders['review_score'] >= 4).mean() * 100,  # 4-5 stars
            'nps_score': self._calculate_nps(unique_orders['review_score'])
        }
        
        return metrics
    
    def calculate_delivery_performance(self, sales_with_delivery: pd.DataFrame) -> Dict:
        """
        Calculate delivery performance metrics.
        
        Args:
            sales_with_delivery (pd.DataFrame): Sales data with delivery information
            
        Returns:
            Dict: Delivery performance metrics
        """
        # Remove duplicates to get unique orders
        unique_orders = sales_with_delivery[['order_id', 'delivery_speed', 'delivery_category']].drop_duplicates()
        
        metrics = {
            'average_delivery_days': unique_orders['delivery_speed'].mean(),
            'median_delivery_days': unique_orders['delivery_speed'].median(),
            'delivery_distribution': unique_orders['delivery_category'].value_counts(),
            'fast_delivery_rate': (unique_orders['delivery_speed'] <= 3).mean() * 100,  # Within 3 days
            'slow_delivery_rate': (unique_orders['delivery_speed'] > 7).mean() * 100   # More than 7 days
        }
        
        return metrics
    
    def analyze_satisfaction_vs_delivery(self, sales_with_reviews_delivery: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze relationship between delivery speed and customer satisfaction.
        
        Args:
            sales_with_reviews_delivery (pd.DataFrame): Sales data with reviews and delivery info
            
        Returns:
            pd.DataFrame: Analysis of satisfaction vs delivery speed
        """
        # Remove duplicates to get unique orders
        unique_orders = sales_with_reviews_delivery[[
            'order_id', 'delivery_speed', 'delivery_category', 'review_score'
        ]].drop_duplicates()
        
        # Group by delivery category
        satisfaction_by_delivery = unique_orders.groupby('delivery_category').agg({
            'review_score': ['mean', 'count', 'std']
        }).round(3)
        
        # Flatten column names
        satisfaction_by_delivery.columns = ['avg_rating', 'review_count', 'rating_std']
        satisfaction_by_delivery = satisfaction_by_delivery.reset_index()
        
        # Calculate satisfaction rate (4-5 stars)
        for category in unique_orders['delivery_category'].unique():
            category_data = unique_orders[unique_orders['delivery_category'] == category]
            satisfaction_rate = (category_data['review_score'] >= 4).mean() * 100
            satisfaction_by_delivery.loc[
                satisfaction_by_delivery['delivery_category'] == category, 'satisfaction_rate'
            ] = satisfaction_rate
        
        return satisfaction_by_delivery
    
    def _calculate_nps(self, scores: pd.Series) -> float:
        """
        Calculate Net Promoter Score (NPS) based on review scores.
        Maps 5-star ratings to NPS scale (1-5 -> 0-10 scale).
        
        Args:
            scores (pd.Series): Review scores (1-5 scale)
            
        Returns:
            float: NPS score
        """
        # Map 5-star scale to 10-point scale for NPS calculation
        nps_scores = scores * 2  # 1->2, 2->4, 3->6, 4->8, 5->10
        
        promoters = (nps_scores >= 9).sum()  # 9-10 (originally 4.5-5)
        detractors = (nps_scores <= 6).sum()  # 0-6 (originally 0-3)
        total = len(nps_scores)
        
        nps = ((promoters - detractors) / total) * 100
        return round(nps, 2)
    
    def plot_revenue_trend(self, monthly_data: pd.DataFrame, title_suffix: str = "") -> go.Figure:
        """
        Create revenue trend visualization.
        
        Args:
            monthly_data (pd.DataFrame): Monthly metrics data
            title_suffix (str): Additional text for title
            
        Returns:
            plotly.graph_objects.Figure: Revenue trend plot
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly_data['month'],
            y=monthly_data['revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color=self.color_scheme['primary'], width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f'Monthly Revenue Trend {title_suffix}',
            xaxis_title='Month',
            yaxis_title='Revenue ($)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig
    
    def plot_category_performance(self, category_data: pd.DataFrame, 
                                title_suffix: str = "") -> go.Figure:
        """
        Create product category performance visualization.
        
        Args:
            category_data (pd.DataFrame): Category performance data
            title_suffix (str): Additional text for title
            
        Returns:
            plotly.graph_objects.Figure: Category performance plot
        """
        fig = go.Figure(data=[
            go.Bar(
                x=category_data['product_category_name'],
                y=category_data['total_revenue'],
                marker_color=self.color_scheme['primary'],
                text=category_data['revenue_share'].apply(lambda x: f'{x}%'),
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title=f'Revenue by Product Category {title_suffix}',
            xaxis_title='Product Category',
            yaxis_title='Total Revenue ($)',
            template='plotly_white',
            xaxis_tickangle=-45
        )
        
        return fig
    
    def plot_geographic_distribution(self, state_data: pd.DataFrame, 
                                   title_suffix: str = "") -> go.Figure:
        """
        Create geographic revenue distribution map.
        
        Args:
            state_data (pd.DataFrame): State-level performance data
            title_suffix (str): Additional text for title
            
        Returns:
            plotly.graph_objects.Figure: Choropleth map
        """
        fig = px.choropleth(
            state_data,
            locations='state',
            color='total_revenue',
            locationmode='USA-states',
            scope='usa',
            title=f'Revenue Distribution by State {title_suffix}',
            color_continuous_scale='Reds',
            labels={'total_revenue': 'Total Revenue ($)'}
        )
        
        return fig
    
    def plot_satisfaction_metrics(self, satisfaction_data: Dict) -> go.Figure:
        """
        Create customer satisfaction visualization.
        
        Args:
            satisfaction_data (Dict): Customer satisfaction metrics
            
        Returns:
            plotly.graph_objects.Figure: Satisfaction metrics plot
        """
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Rating distribution bar chart
        ratings = satisfaction_data['rating_distribution']
        
        fig.add_trace(
            go.Bar(
                x=ratings.index,
                y=ratings.values,
                name='Review Count',
                marker_color=self.color_scheme['primary']
            ),
            secondary_y=False,
        )
        
        # Average rating line
        fig.add_hline(
            y=satisfaction_data['average_rating'],
            line_dash="dash",
            line_color=self.color_scheme['danger'],
            annotation_text=f"Avg: {satisfaction_data['average_rating']:.2f}"
        )
        
        fig.update_layout(
            title='Customer Satisfaction Distribution',
            template='plotly_white'
        )
        
        fig.update_xaxes(title_text="Rating Score")
        fig.update_yaxes(title_text="Number of Reviews", secondary_y=False)
        
        return fig
    
    def plot_delivery_analysis(self, delivery_satisfaction: pd.DataFrame) -> go.Figure:
        """
        Create delivery speed vs satisfaction analysis plot.
        
        Args:
            delivery_satisfaction (pd.DataFrame): Delivery vs satisfaction data
            
        Returns:
            plotly.graph_objects.Figure: Delivery analysis plot
        """
        fig = go.Figure()
        
        # Bar chart for average rating by delivery category
        fig.add_trace(go.Bar(
            x=delivery_satisfaction['delivery_category'],
            y=delivery_satisfaction['avg_rating'],
            name='Average Rating',
            marker_color=self.color_scheme['primary'],
            text=delivery_satisfaction['avg_rating'].round(3),
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Customer Satisfaction by Delivery Speed',
            xaxis_title='Delivery Time Category',
            yaxis_title='Average Rating (1-5)',
            template='plotly_white',
            yaxis=dict(range=[0, 5])
        )
        
        return fig
    
    def generate_summary_report(self, revenue_metrics: Dict, 
                              satisfaction_metrics: Dict,
                              delivery_metrics: Dict) -> str:
        """
        Generate a text summary report of key metrics.
        
        Args:
            revenue_metrics (Dict): Revenue-related metrics
            satisfaction_metrics (Dict): Customer satisfaction metrics
            delivery_metrics (Dict): Delivery performance metrics
            
        Returns:
            str: Formatted summary report
        """
        report = f"""
BUSINESS METRICS SUMMARY REPORT
================================

REVENUE PERFORMANCE
-------------------
Total Revenue: ${revenue_metrics['total_revenue']:,.2f}
Total Orders: {revenue_metrics['total_orders']:,}
Average Order Value: ${revenue_metrics['average_order_value']:.2f}
Average Item Price: ${revenue_metrics['average_item_price']:.2f}
"""
        
        if 'revenue_growth_rate' in revenue_metrics:
            report += f"""
YEAR-over-YEAR COMPARISON
------------------------
Revenue Growth: {revenue_metrics['revenue_growth_rate']:.2f}%
Order Growth: {revenue_metrics['order_growth_rate']:.2f}%
AOV Growth: {revenue_metrics['aov_growth_rate']:.2f}%
"""
        
        report += f"""
CUSTOMER SATISFACTION
--------------------
Average Rating: {satisfaction_metrics['average_rating']:.2f}/5.0
Total Reviews: {satisfaction_metrics['total_reviews']:,}
Satisfaction Rate: {satisfaction_metrics['satisfaction_rate']:.1f}% (4+ stars)
Net Promoter Score: {satisfaction_metrics['nps_score']:.1f}

DELIVERY PERFORMANCE
-------------------
Average Delivery Time: {delivery_metrics['average_delivery_days']:.1f} days
Fast Delivery Rate: {delivery_metrics['fast_delivery_rate']:.1f}% (≤3 days)
Slow Delivery Rate: {delivery_metrics['slow_delivery_rate']:.1f}% (>7 days)
"""
        
        return report