import streamlit as st

# Initialize app state (set up the memory)
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = []

st.title('🛒 My Shopping List')

# --- USER INPUT SECTION ---
st.header('Add Items')

# Text input
item_name = st.text_input('What do you need to buy?')

# Selectbox  
category = st.selectbox('Category:', ['Food', 'Household', 'Personal', 'Other'])

# Number input
quantity = st.number_input('How many?', min_value=1, value=1)

# Button to add item (this triggers saving to memory)
if st.button('Add to List'):
    if item_name:  # Only add if user typed something
        new_item = {
            'name': item_name,
            'category': category,
            'quantity': quantity,
            'bought': False
        }
        st.session_state.shopping_list.append(new_item)
        st.success(f'Added {quantity} {item_name} to your list!')
    else:
        st.error('Please enter an item name!')

# --- DISPLAY CURRENT STATE (show what's in memory) ---
st.header('Your Shopping List')

if st.session_state.shopping_list:
    # Show summary
    total_items = len(st.session_state.shopping_list)
    bought_items = len([item for item in st.session_state.shopping_list if item['bought']])
    st.write(f'**Total items:** {total_items} | **Bought:** {bought_items} | **Still need:** {total_items - bought_items}')
    
    # Display each item
    for i, item in enumerate(st.session_state.shopping_list):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            # Checkbox to mark as bought (this changes the memory)
            is_bought = st.checkbox(
                f"{item['quantity']} {item['name']} ({item['category']})",
                value=item['bought'],
                key=f'item_{i}'
            )
            # Update the memory when checkbox changes
            st.session_state.shopping_list[i]['bought'] = is_bought
        
        with col2:
            if item['bought']:
                st.write('✅ Done')
            else:
                st.write('⏳ Need')
        
        with col3:
            # Button to remove item (this modifies memory)
            if st.button('Remove', key=f'remove_{i}'):
                st.session_state.shopping_list.pop(i)
                st.rerun()  # Refresh the app to show changes

    # Button to clear everything
    st.write('---')
    if st.button('Clear Entire List'):
        st.session_state.shopping_list = []
        st.success('Shopping list cleared!')

else:
    st.info('Your shopping list is empty. Add some items above!')

# Show what's in memory for learning purposes
st.write('---')
st.subheader('🧠 App Memory (Session State)')
st.write('This is what the app remembers:')
st.write(st.session_state.shopping_list)