import streamlit as st
import pandas as pd
import numpy as np

st.title('My First Streamlit App')

st.write('Hello, World!')

# Create some sample data
data = pd.DataFrame({
    'numbers': np.random.randn(20),
    'letters': np.random.choice(['A', 'B', 'C'], 20)
})

st.dataframe(data)
st.line_chart(data['numbers'])