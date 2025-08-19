"""
Data loading and processing module for e-commerce analysis.

This module provides functions to load, clean, and prepare e-commerce datasets
for analysis. It handles data type conversions, filtering, and basic transformations.
"""

import pandas as pd
from typing import Dict
import warnings
warnings.filterwarnings('ignore')


class EcommerceDataLoader:
    """
    A class to handle loading and processing of e-commerce data.
    
    This class provides methods to load multiple related datasets and perform
    common preprocessing tasks like date parsing and filtering.
    """
    
    def __init__(self, data_path: str = "ecommerce_data"):
        """
        Initialize the data loader.
        
        Args:
            data_path (str): Path to the directory containing CSV files
        """
        self.data_path = data_path
        self.datasets = {}
    
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all e-commerce datasets from CSV files.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all loaded datasets
        """
        dataset_files = {
            'orders': 'orders_dataset.csv',
            'order_items': 'order_items_dataset.csv', 
            'products': 'products_dataset.csv',
            'customers': 'customers_dataset.csv',
            'reviews': 'order_reviews_dataset.csv',
            'payments': 'order_payments_dataset.csv'
        }
        
        for name, filename in dataset_files.items():
            try:
                file_path = f"{self.data_path}/{filename}"
                self.datasets[name] = pd.read_csv(file_path)
                print(f"Loaded {name}: {self.datasets[name].shape[0]} rows, {self.datasets[name].shape[1]} columns")
            except FileNotFoundError:
                print(f"Warning: {filename} not found, skipping...")
                continue
        
        return self.datasets
    
    def prepare_orders_data(self) -> pd.DataFrame:
        """
        Prepare orders data with proper date parsing and additional columns.
        
        Returns:
            pd.DataFrame: Processed orders dataframe with date columns and year/month
        """
        if 'orders' not in self.datasets:
            raise ValueError("Orders dataset not loaded. Call load_all_datasets() first.")
        
        orders = self.datasets['orders'].copy()
        
        # Convert date columns to datetime
        date_columns = [
            'order_purchase_timestamp',
            'order_approved_at', 
            'order_delivered_carrier_date',
            'order_delivered_customer_date',
            'order_estimated_delivery_date'
        ]
        
        for col in date_columns:
            if col in orders.columns:
                orders[col] = pd.to_datetime(orders[col])
        
        # Add year and month columns for analysis
        orders['year'] = orders['order_purchase_timestamp'].dt.year
        orders['month'] = orders['order_purchase_timestamp'].dt.month
        
        return orders
    
    def create_sales_dataset(self, target_year: int = None, 
                           target_month: int = None,
                           order_status: str = 'delivered') -> pd.DataFrame:
        """
        Create a comprehensive sales dataset by merging orders and order_items.
        
        Args:
            target_year (int, optional): Filter by specific year
            target_month (int, optional): Filter by specific month  
            order_status (str): Filter by order status (default: 'delivered')
            
        Returns:
            pd.DataFrame: Merged sales dataset with filtering applied
        """
        if 'orders' not in self.datasets or 'order_items' not in self.datasets:
            raise ValueError("Orders and order_items datasets required.")
        
        # Prepare orders data
        orders = self.prepare_orders_data()
        order_items = self.datasets['order_items'].copy()
        
        # Merge orders and order items
        sales_data = pd.merge(
            left=order_items[['order_id', 'order_item_id', 'product_id', 'price']],
            right=orders[['order_id', 'order_status', 'order_purchase_timestamp', 
                         'order_delivered_customer_date', 'year', 'month']],
            on='order_id',
            how='inner'
        )
        
        # Filter by order status
        if order_status:
            sales_data = sales_data[sales_data['order_status'] == order_status].copy()
        
        # Filter by year
        if target_year:
            sales_data = sales_data[sales_data['year'] == target_year].copy()
            
        # Filter by month
        if target_month:
            sales_data = sales_data[sales_data['month'] == target_month].copy()
        
        return sales_data
    
    def add_delivery_metrics(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Add delivery speed metrics to sales data.
        
        Args:
            sales_data (pd.DataFrame): Sales dataset with date columns
            
        Returns:
            pd.DataFrame: Sales data with delivery speed metrics
        """
        sales_with_delivery = sales_data.copy()
        
        # Calculate delivery speed in days
        sales_with_delivery['delivery_speed'] = (
            sales_with_delivery['order_delivered_customer_date'] - 
            sales_with_delivery['order_purchase_timestamp']
        ).dt.days
        
        # Categorize delivery speed
        def categorize_delivery_speed(days):
            if pd.isna(days):
                return 'Unknown'
            elif days <= 3:
                return '1-3 days'
            elif days <= 7:
                return '4-7 days'
            else:
                return '8+ days'
        
        sales_with_delivery['delivery_category'] = sales_with_delivery['delivery_speed'].apply(
            categorize_delivery_speed
        )
        
        return sales_with_delivery
    
    def get_product_categories_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sales data with product categories.
        
        Args:
            sales_data (pd.DataFrame): Sales dataset
            
        Returns:
            pd.DataFrame: Sales data with product category information
        """
        if 'products' not in self.datasets:
            raise ValueError("Products dataset required.")
        
        products = self.datasets['products'][['product_id', 'product_category_name']].copy()
        
        return pd.merge(
            left=products,
            right=sales_data[['product_id', 'price', 'order_id']],
            on='product_id',
            how='inner'
        )
    
    def get_customer_geographic_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sales data with customer geographic information.
        
        Args:
            sales_data (pd.DataFrame): Sales dataset
            
        Returns:
            pd.DataFrame: Sales data with customer state information
        """
        if 'orders' not in self.datasets or 'customers' not in self.datasets:
            raise ValueError("Orders and customers datasets required.")
        
        # Get orders with customer IDs
        orders = self.datasets['orders'][['order_id', 'customer_id']].copy()
        customers = self.datasets['customers'][['customer_id', 'customer_state']].copy()
        
        # Merge sales data with customer info
        sales_with_customers = pd.merge(
            left=sales_data[['order_id', 'price']],
            right=orders,
            on='order_id',
            how='inner'
        )
        
        return pd.merge(
            left=sales_with_customers,
            right=customers,
            on='customer_id',
            how='inner'
        )
    
    def get_review_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sales data with review information.
        
        Args:
            sales_data (pd.DataFrame): Sales dataset
            
        Returns:
            pd.DataFrame: Sales data with review scores
        """
        if 'reviews' not in self.datasets:
            raise ValueError("Reviews dataset required.")
        
        reviews = self.datasets['reviews'][['order_id', 'review_score']].copy()
        
        return pd.merge(
            left=sales_data,
            right=reviews,
            on='order_id',
            how='inner'
        )
    
    def get_dataset_info(self) -> Dict[str, Dict]:
        """
        Get summary information about all loaded datasets.
        
        Returns:
            Dict[str, Dict]: Summary information for each dataset
        """
        info = {}
        for name, df in self.datasets.items():
            info[name] = {
                'rows': df.shape[0],
                'columns': df.shape[1],
                'missing_values': df.isnull().sum().sum(),
                'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
            }
        return info


def load_ecommerce_data(data_path: str = "ecommerce_data") -> EcommerceDataLoader:
    """
    Convenience function to create and initialize data loader.
    
    Args:
        data_path (str): Path to the data directory
        
    Returns:
        EcommerceDataLoader: Initialized data loader with all datasets loaded
    """
    loader = EcommerceDataLoader(data_path)
    loader.load_all_datasets()
    return loader