import streamlit as st
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
st.title('💰 Budget Tracker')

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
if st.button('Add $20 to spent amount (simulate purchase)'):
    st.session_state.spent_this_month += 20.0
    st.rerun()

if st.button('Reset spent amount'):
    st.session_state.spent_this_month = 45.67  # Reset to initial value
    st.rerun()