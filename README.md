# E-Commerce Business Analytics

## Overview

This project provides a comprehensive framework for analyzing e-commerce business performance using configurable Python modules and Jupyter notebooks. The analysis covers revenue trends, customer satisfaction, product performance, geographic distribution, and operational metrics.

## Project Structure

```
claude-data-analysis/
├── ecommerce_data/              # Raw CSV datasets
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── products_dataset.csv
│   ├── customers_dataset.csv
│   ├── order_reviews_dataset.csv
│   └── order_payments_dataset.csv
├── data_loader.py               # Data loading and processing module
├── business_metrics.py          # Business metrics calculation module
├── EDA.ipynb                    # Original analysis notebook
├── EDA_Refactored.ipynb         # Refactored analysis notebook
├── uv.lock                      # UV dependency lock file
└── README.md                    # This file
```

## Features

### Data Processing (`data_loader.py`)
- **EcommerceDataLoader**: Centralized data loading and processing
- **Configurable Filtering**: Filter by year, month, and order status
- **Data Enhancement**: Add delivery metrics, geographic data, and product categories
- **Data Validation**: Built-in data quality checks and summary statistics

### Business Metrics (`business_metrics.py`)
- **EcommerceMetrics**: Comprehensive business KPI calculations
- **Revenue Analysis**: Growth rates, trends, and comparative metrics
- **Customer Experience**: Satisfaction scores, NPS, and delivery analysis
- **Product Performance**: Category analysis and market share
- **Geographic Analysis**: State-level performance metrics
- **Interactive Visualizations**: Plotly-based charts and maps

### Enhanced Notebook (`EDA_Refactored.ipynb`)
- **Structured Analysis**: Organized sections with clear documentation
- **Configurable Parameters**: Easy customization for different time periods
- **Professional Visualizations**: Business-ready charts with proper formatting
- **Executive Summary**: Automated report generation with actionable insights

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd claude-data-analysis
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Verify data files:**
   Ensure all CSV files are present in the `ecommerce_data/` directory.

## Quick Start

### Basic Usage

```python
from data_loader import EcommerceDataLoader
from business_metrics import EcommerceMetrics

# Initialize data loader
loader = EcommerceDataLoader("ecommerce_data")
datasets = loader.load_all_datasets()

# Create sales dataset for 2023
sales_2023 = loader.create_sales_dataset(target_year=2023, order_status='delivered')

# Calculate revenue metrics
metrics = EcommerceMetrics()
revenue_metrics = metrics.calculate_revenue_metrics(sales_2023)

print(f"Total Revenue 2023: ${revenue_metrics['total_revenue']:,.2f}")
print(f"Total Orders: {revenue_metrics['total_orders']:,}")
```

### Advanced Configuration

```python
# Analyze specific month with comparison
sales_current = loader.create_sales_dataset(target_year=2023, target_month=12)
sales_previous = loader.create_sales_dataset(target_year=2022, target_month=12)

# Calculate metrics with year-over-year comparison
revenue_metrics = metrics.calculate_revenue_metrics(sales_current, sales_previous)

# Generate comprehensive report
summary = metrics.generate_summary_report(
    revenue_metrics,
    satisfaction_metrics,
    delivery_metrics
)
```

## Notebook Usage

### Configuration Parameters

At the beginning of `EDA_Refactored.ipynb`, modify these parameters:

```python
# Analysis Configuration
TARGET_YEAR = 2023          # Primary analysis year
COMPARISON_YEAR = 2022      # Comparison year for growth calculations
TARGET_MONTH = None         # Set to 1-12 for specific month analysis
DATA_PATH = "ecommerce_data" # Path to CSV files
```

### Running the Analysis

1. **Start Jupyter:**
   ```bash
   jupyter notebook EDA_Refactored.ipynb
   ```

2. **Configure Parameters:**
   - Update the configuration cell with your desired analysis parameters
   - Run the configuration cell

3. **Execute Analysis:**
   - Run all cells sequentially
   - Each section provides detailed insights and visualizations
   - Review the executive summary for key findings

## Key Metrics Explained

### Revenue Metrics
- **Total Revenue**: Sum of all delivered order values
- **Average Order Value (AOV)**: Total revenue / Number of orders
- **Growth Rate**: (Current Period - Previous Period) / Previous Period × 100

### Customer Experience Metrics
- **Average Rating**: Mean review score (1-5 stars)
- **Satisfaction Rate**: Percentage of 4+ star reviews
- **Net Promoter Score (NPS)**: Promoters % - Detractors %

### Delivery Performance
- **Average Delivery Time**: Mean days from order to delivery
- **Fast Delivery Rate**: Percentage delivered within 3 days
- **Delivery Categories**: 1-3 days, 4-7 days, 8+ days

## Customization

### Adding New Metrics

1. **Extend business_metrics.py:**
   ```python
   def calculate_custom_metric(self, data):
       # Your custom calculation
       return result
   ```

2. **Add visualization:**
   ```python
   def plot_custom_metric(self, data):
       # Create plotly visualization
       return fig
   ```

### Custom Filtering

```python
# Create custom filtered dataset
custom_data = loader.create_sales_dataset(
    target_year=2023,
    target_month=6,
    order_status='delivered'
)

# Add additional filters
high_value_orders = custom_data[custom_data['price'] > 500]
```

## Best Practices

### Performance Optimization
- Use specific date ranges to reduce memory usage
- Filter data early in the pipeline
- Cache processed datasets for repeated analysis

### Data Quality
- Always validate data completeness before analysis
- Check for missing values in key columns
- Verify date ranges match expected periods

### Reproducibility
- Document configuration parameters
- Use version control for analysis notebooks
- Keep raw data unchanged

## Troubleshooting

### Common Issues

1. **Import Errors:**
   ```bash
   # Ensure all dependencies are installed
   uv sync
   ```

2. **Data Not Found:**
   ```python
   # Verify file paths
   import os
   os.listdir("ecommerce_data/")
   ```

3. **Memory Issues:**
   ```python
   # Use date filtering to reduce data size
   sales_data = loader.create_sales_dataset(target_year=2023, target_month=1)
   ```

### Performance Tips

- Filter data by date range early in the analysis
- Use `.copy()` when creating data subsets to avoid pandas warnings
- Close figures after displaying to free memory: `plt.close()`

## Contributing

When extending this analysis framework:

1. Follow existing code structure and naming conventions
2. Add docstrings to all functions
3. Include example usage in docstrings
4. Update this README with new features
5. Test with different date ranges and configurations

## License

This project is designed for educational and business analysis purposes. Ensure compliance with data privacy regulations when using with real customer data.

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review function docstrings for usage examples
3. Examine the notebook cells for implementation patterns
4. Test with different configuration parameters