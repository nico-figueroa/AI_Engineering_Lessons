import streamlit as st
import pandas as pd
def initialize_session_state():
    """Initialize all session state variables"""
    if 'shopping_items' not in st.session_state:
        st.session_state.shopping_items = [
            {'name': 'Milk', 'category': 'Food', 'cost': 3.99, 'bought': False},
            {'name': 'Bread', 'category': 'Food', 'cost': 2.49, 'bought': True},
            {'name': 'Soap', 'category': 'Household', 'cost': 4.99, 'bought': False},
        ]
    
    if 'monthly_budget' not in st.session_state:
        st.session_state.monthly_budget = 200.0
    
    if 'spent_this_month' not in st.session_state:
        st.session_state.spent_this_month = 45.67

# Call this at the start of every page
initialize_session_state()

st.title('📊 Analytics')

if st.session_state.shopping_items:
    # Convert to DataFrame for easy analysis
    df = pd.DataFrame(st.session_state.shopping_items)
    
    st.subheader('Spending by Category')
    
    # Group by category and sum costs
    category_totals = df.groupby('category')['cost'].sum().sort_values(ascending=False)
    
    # Show as bar chart
    st.bar_chart(category_totals)
    
    # Show the data in a table too
    st.subheader('Category Breakdown')
    category_df = pd.DataFrame({
        'Category': category_totals.index,
        'Total Spent': category_totals.values,
        'Item Count': df.groupby('category').size().values
    })
    
    st.dataframe(
        category_df,
        column_config={
            "Total Spent": st.column_config.NumberColumn("Total Spent", format="$%.2f")
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Items', len(df))
    with col2:
        st.metric('Total Spent', f"${df['cost'].sum():.2f}")
    with col3:
        st.metric('Average Cost', f"${df['cost'].mean():.2f}")

else:
    st.write('No items to analyze yet. Add some items to your shopping list!')