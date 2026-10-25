import streamlit as st
from datetime import datetime
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

st.title('🛒 Shopping List')

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