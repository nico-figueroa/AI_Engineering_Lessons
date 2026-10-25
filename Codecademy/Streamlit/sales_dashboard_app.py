import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Set page config
st.set_page_config(page_title="Coffee Shop ML Tracker", layout="wide")

# Create sample historical data
@st.cache_data
def create_sample_data():
    """Create sample historical sales data"""
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now().date(), periods=30, freq='D')
    
    sales_data = []
    for date in dates:
        # Simulate realistic daily sales patterns
        base_sales = 900
        if date.weekday() >= 5:  # Weekend boost
            base_sales += 300
        if date.weekday() == 1:  # Tuesday dip
            base_sales -= 100
        
        # Add randomness
        daily_sales = base_sales + np.random.normal(0, 80)
        daily_sales = max(daily_sales, 200)  # Minimum sales
        
        customers = int(daily_sales / 12) + np.random.randint(-5, 5)
        customers = max(customers, 15)  # Minimum customers
        
        sales_data.append({
            'Date': date,
            'Daily_Sales': daily_sales,
            'Customers': customers,
        })
    
    return pd.DataFrame(sales_data)

# Create ML models
@st.cache_resource
def create_ml_models():
    """Create ML models for comparison"""
    np.random.seed(42)
    n_days = 365
    
    # Generate training data
    days = pd.date_range('2023-01-01', periods=n_days, freq='D')
    data = pd.DataFrame({
        'day_of_week': days.dayofweek,
        'temperature': np.random.normal(70, 15, n_days),
        'is_weekend': (days.dayofweek >= 5).astype(int),
        'month': days.month,
    })
    
    # Sales relationship
    base_sales = 800 + data['temperature'] * 5
    base_sales += data['is_weekend'] * 200
    base_sales += (data['day_of_week'] == 1) * -50  # Tuesday dip
    base_sales += np.random.normal(0, 50, n_days)
    
    data['sales'] = np.maximum(base_sales, 100)
    
    # Train models
    X = data[['day_of_week', 'temperature', 'is_weekend', 'month']]
    y = data['sales']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Random Forest
    rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Linear Regression
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    
    return {
        'random_forest': rf_model,
        'linear_regression': lr_model,
        'rf_accuracy': rf_model.score(X_test, y_test),
        'lr_accuracy': lr_model.score(X_test, y_test),
        'test_data': (X_test, y_test)
    }

def predict_sales(models, model_type, day_of_week, temperature, is_weekend, month):
    """Make sales prediction with specified model"""
    model = models[model_type]
    input_data = [[day_of_week, temperature, is_weekend, month]]
    prediction = model.predict(input_data)[0]
    return max(prediction, 100)

# Load sample data
sales_df = create_sample_data()

# Initialize session state - THIS IS THE KEY FIX
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'ml_models' not in st.session_state:
    st.session_state.ml_models = None

st.title('☕ Coffee Shop ML Tracker')
st.write('Simple machine learning sales prediction for your coffee shop')

# Check if models are loaded
if not st.session_state.model_loaded or st.session_state.ml_models is None:
    st.info("Load the ML models to start predicting sales")
    
    if st.button("Load ML Models", type="primary"):
        with st.spinner("Training ML models..."):
            time.sleep(2)  # Simulate training
            st.session_state.ml_models = create_ml_models()
            st.session_state.model_loaded = True
        
        st.success("Models loaded successfully!")
        st.balloons()
        st.rerun()

else:
    # Models are loaded - show the main interface
    models = st.session_state.ml_models
    st.success(f"🤖 ML Models Ready! RF: {models['rf_accuracy']:.2%} | LR: {models['lr_accuracy']:.2%}")
    
    # Model selection
    st.header("🔧 Model Selection")
    model_type = st.selectbox(
        "Choose ML Model for Prediction",
        ["random_forest", "linear_regression"],
        format_func=lambda x: "Random Forest" if x == "random_forest" else "Linear Regression"
    )
    
    # Sales prediction section
    st.header("📊 Sales Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Parameters")
        
        # Fixed the slider issue by removing format_func
        day_of_week = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 3)
        
        # Show day name separately
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        st.write(f"Selected: **{day_names[day_of_week]}**")
        
        temperature = st.slider("Temperature (°F)", 30, 110, 70)
        is_weekend = st.checkbox("Weekend", value=False)
        
        current_month = datetime.now().month
        
        # Make prediction with selected model
        prediction = predict_sales(
            models,
            model_type,
            day_of_week,
            temperature,
            int(is_weekend),
            current_month
        )
    
    with col2:
        st.subheader("Prediction Result")
        
        model_name = "Random Forest" if model_type == "random_forest" else "Linear Regression"
        accuracy = models['rf_accuracy'] if model_type == "random_forest" else models['lr_accuracy']
        
        st.metric(
            f"{model_name} Prediction",
            f"${prediction:.0f}",
            delta=f"vs average: ${prediction - 900:.0f}"
        )
        
        st.info(f"Model Accuracy: {accuracy:.2%}")
        
        # Simple breakdown
        st.write("**Factors affecting sales:**")
        if is_weekend:
            st.write("🟢 Weekend boost: +$200")
        if day_of_week == 1:  # Tuesday
            st.write("🔴 Tuesday dip: -$50")
        if temperature > 80:
            st.write("🟢 Hot weather: Higher sales")
        elif temperature < 50:
            st.write("🔵 Cold weather: Moderate impact")
    
    # Model comparison section
    st.header("⚖️ Model Comparison")
    
    scenarios = {
        "Typical Monday": (0, 70, False),
        "Weekend Rush": (6, 75, True),
        "Cold Tuesday": (1, 45, False),
        "Hot Friday": (4, 95, False)
    }
    
    comparison_results = []
    for name, (dow, temp, weekend) in scenarios.items():
        rf_pred = predict_sales(models, 'random_forest', dow, temp, int(weekend), current_month)
        lr_pred = predict_sales(models, 'linear_regression', dow, temp, int(weekend), current_month)
        
        comparison_results.append({
            'Scenario': name,
            'Random Forest': f"${rf_pred:.0f}",
            'Linear Regression': f"${lr_pred:.0f}",
            'Difference': f"${abs(rf_pred - lr_pred):.0f}"
        })
    
    comparison_df = pd.DataFrame(comparison_results)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Temperature sensitivity comparison
    st.header("🌡️ Temperature Impact Comparison")
    
    temp_range = range(40, 101, 10)
    rf_predictions = []
    lr_predictions = []
    
    for temp in temp_range:
        rf_pred = predict_sales(models, 'random_forest', day_of_week, temp, int(is_weekend), current_month)
        lr_pred = predict_sales(models, 'linear_regression', day_of_week, temp, int(is_weekend), current_month)
        rf_predictions.append(rf_pred)
        lr_predictions.append(lr_pred)
    
    # Create comparison chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(temp_range, rf_predictions, 'bo-', linewidth=2, markersize=6, label='Random Forest')
    ax.plot(temp_range, lr_predictions, 'ro-', linewidth=2, markersize=6, label='Linear Regression')
    
    # Highlight current predictions
    current_rf = predict_sales(models, 'random_forest', day_of_week, temperature, int(is_weekend), current_month)
    current_lr = predict_sales(models, 'linear_regression', day_of_week, temperature, int(is_weekend), current_month)
    
    ax.scatter([temperature], [current_rf], color='blue', s=100, marker='*', zorder=5)
    ax.scatter([temperature], [current_lr], color='red', s=100, marker='*', zorder=5)
    
    ax.set_xlabel('Temperature (°F)')
    ax.set_ylabel('Predicted Sales ($)')
    ax.set_title('How Temperature Affects Sales - Model Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    plt.close()
    
    # Model performance comparison
    st.header("📊 Model Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Accuracy Comparison")
        perf_df = pd.DataFrame({
            'Model': ['Random Forest', 'Linear Regression'],
            'Accuracy': [f"{models['rf_accuracy']:.2%}", f"{models['lr_accuracy']:.2%}"],
            'R² Score': [f"{models['rf_accuracy']:.3f}", f"{models['lr_accuracy']:.3f}"]
        })
        st.dataframe(perf_df, use_container_width=True, hide_index=True)
        
        if models['rf_accuracy'] > models['lr_accuracy']:
            st.success("🏆 Random Forest performs better!")
        else:
            st.success("🏆 Linear Regression performs better!")
    
    with col2:
        st.subheader("Visual Comparison")
        fig, ax = plt.subplots(figsize=(6, 4))
        
        models_names = ['Random Forest', 'Linear Regression']
        accuracies = [models['rf_accuracy'], models['lr_accuracy']]
        colors = ['blue', 'red']
        
        bars = ax.bar(models_names, accuracies, color=colors, alpha=0.7)
        ax.set_ylabel('Accuracy (R² Score)')
        ax.set_title('Model Performance Comparison')
        ax.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, value in zip(bars, accuracies):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{value:.3f}', ha='center', va='bottom')
        
        st.pyplot(fig)
        plt.close()

# Historical data section - ALWAYS show this
st.header("📈 Historical Performance")
st.info("Sample data - in production this would show your real sales")

col1, col2, col3 = st.columns(3)

with col1:
    total_sales = sales_df['Daily_Sales'].sum()
    st.metric("30-Day Total", f"${total_sales:,.0f}")

with col2:
    avg_daily = sales_df['Daily_Sales'].mean()
    st.metric("Daily Average", f"${avg_daily:.0f}")

with col3:
    best_day = sales_df['Daily_Sales'].max()
    st.metric("Best Day", f"${best_day:.0f}")

# Simple sales trend chart
st.subheader("Sales Trend (Last 30 Days)")
chart_data = sales_df.set_index('Date')['Daily_Sales']
st.line_chart(chart_data)

# Simple insights
weekend_avg = sales_df[sales_df['Date'].dt.dayofweek >= 5]['Daily_Sales'].mean()
weekday_avg = sales_df[sales_df['Date'].dt.dayofweek < 5]['Daily_Sales'].mean()
weekend_lift = ((weekend_avg - weekday_avg) / weekday_avg * 100)

st.subheader("💡 Key Insights")
col1, col2 = st.columns(2)

with col1:
    st.info(f"**Weekend boost**: +{weekend_lift:.1f}% higher sales")

with col2:
    st.info(f"**Best performing day**: {sales_df.loc[sales_df['Daily_Sales'].idxmax(), 'Date'].strftime('%A')}")

st.markdown("---")
st.markdown("🚀 **Tip**: Use the ML model above to predict sales for different scenarios!")