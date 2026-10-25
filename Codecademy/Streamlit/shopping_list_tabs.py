import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configure the page
st.set_page_config(
    page_title="Shopping Manager",
    page_icon="🛒",
    layout="wide"
)

# Initialize session state with sample data
if 'shopping_items' not in st.session_state:
    st.session_state.shopping_items = [
        {'name': 'Milk', 'category': 'Food', 'cost': 3.99, 'bought': False, 'date': datetime.now()},
        {'name': 'Bread', 'category': 'Food', 'cost': 2.49, 'bought': True, 'date': datetime.now() - timedelta(days=1)},
        {'name': 'Soap', 'category': 'Household', 'cost': 4.99, 'bought': False, 'date': datetime.now()},
        {'name': 'Apples', 'category': 'Food', 'cost': 5.99, 'bought': True, 'date': datetime.now()},
    ]

if 'monthly_budget' not in st.session_state:
    st.session_state.monthly_budget = 200.0

if 'spent_this_month' not in st.session_state:
    st.session_state.spent_this_month = 45.67

st.title('🛒 Shopping Manager - Tab Version')
st.write("All features organized in tabs on one page!")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🛒 Shopping List", "📊 Analytics", "💰 Budget Tracker"])

# TAB 1: Shopping List
with tab1:
    st.header('Shopping List Management')
    
    # Simple add item form
    st.subheader("Add New Item")
    col1, col2 = st.columns(2)

    with col1:
        item_name = st.text_input('Item name:')
        category = st.selectbox('Category:', ['Food', 'Household', 'Personal', 'Other'])

    with col2:
        cost = st.number_input('Cost ($):', min_value=0.0, step=0.01, value=0.0)

    if st.button('Add Item', type='primary'):
        if item_name:
            new_item = {
                'name': item_name,
                'category': category,
                'cost': cost,
                'bought': False,
                'date': datetime.now()
            }
            st.session_state.shopping_items.append(new_item)
            st.success(f'Added "{item_name}" to your list!')
            st.rerun()

    st.divider()

    # Display items
    st.subheader('Your Shopping List')
    if st.session_state.shopping_items:
        for i, item in enumerate(st.session_state.shopping_items):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                status = "✅" if item['bought'] else "⬜"
                st.write(f"{status} **{item['name']}** - ${item['cost']:.2f} ({item['category']})")
            
            with col2:
                if st.button('Toggle', key=f'toggle_{i}'):
                    st.session_state.shopping_items[i]['bought'] = not item['bought']
                    st.rerun()
            
            with col3:
                if st.button('Delete', key=f'delete_{i}'):
                    st.session_state.shopping_items.pop(i)
                    st.rerun()
        
        # Summary
        pending_count = len([item for item in st.session_state.shopping_items if not item['bought']])
        pending_cost = sum(item['cost'] for item in st.session_state.shopping_items if not item['bought'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Pending Items', pending_count)
        with col2:
            st.metric('Total Cost', f'${pending_cost:.2f}')
    else:
        st.write('Your shopping list is empty. Add some items above!')

# TAB 2: Analytics
with tab2:
    st.header('Shopping Analytics')
    
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

# TAB 3: Budget Tracker
with tab3:
    st.header('Budget Management')
    
    # Budget settings
    st.subheader('Monthly Budget Settings')
    monthly_budget = st.number_input(
        'Set your monthly budget ($):', 
        value=st.session_state.monthly_budget,
        min_value=0.0,
        step=10.0
    )

    if monthly_budget != st.session_state.monthly_budget:
        st.session_state.monthly_budget = monthly_budget

    st.divider()

    # Budget overview
    st.subheader('This Month Overview')

    spent_this_month = st.session_state.spent_this_month
    remaining = monthly_budget - spent_this_month

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Monthly Budget', f'${monthly_budget:.2f}')
    with col2:
        st.metric('Spent So Far', f'${spent_this_month:.2f}')
    with col3:
        st.metric('Remaining', f'${remaining:.2f}')

    # Progress bar
    budget_used = spent_this_month / monthly_budget if monthly_budget > 0 else 0
    st.progress(budget_used)

    if budget_used > 1.0:
        st.error(f'🚨 Over budget by ${spent_this_month - monthly_budget:.2f}!')
    elif budget_used > 0.8:
        st.warning(f'⚠️ You\'ve used {budget_used*100:.1f}% of your budget')
    else:
        st.success(f'✅ You\'ve used {budget_used*100:.1f}% of your budget - looking good!')

    st.divider()

    # Current shopping list impact
    st.subheader('Shopping List Impact')

    if st.session_state.shopping_items:
        pending_cost = sum(item['cost'] for item in st.session_state.shopping_items if not item['bought'])
        projected_total = spent_this_month + pending_cost
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric('Current List Cost', f'${pending_cost:.2f}')
        with col2:
            st.metric('Projected Monthly Total', f'${projected_total:.2f}')
        
        if projected_total > monthly_budget:
            overage = projected_total - monthly_budget
            st.error(f'⚠️ Buying these items would put you ${overage:.2f} over budget!')
        else:
            remaining_after = monthly_budget - projected_total
            st.success(f'✅ You\'ll have ${remaining_after:.2f} left after these purchases')

    else:
        st.write('No pending items to calculate impact.')

    # Quick budget adjustment
    st.subheader('Quick Actions')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Add $20 to spent amount (simulate purchase)'):
            st.session_state.spent_this_month += 20.0
            st.rerun()
    with col2:
        if st.button('Reset spent amount'):
            st.session_state.spent_this_month = 45.67  # Reset to initial value
            st.rerun()