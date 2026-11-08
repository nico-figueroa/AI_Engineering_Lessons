import streamlit as st
import chromadb
import logging

logger = logging.getLogger(__name__)

# Checkpoint 1: Initialize Chroma client and collection
try:
    client = chromadb.PersistentClient("./")
    collection = client.get_or_create_collection(name="RAG_Assistant", metadata={"hnsw:space": "cosine"})
except Exception:
    logger.error("Search initialization failed; exception details omitted.")
    st.error("Search is unavailable. Please contact the application operator.")
    st.stop()
# Checkpoint 2: Update previous titles and markdown text
st.title("Similarity Search Application")
st.markdown("This app uses Chroma to perform similarity searches on a collection of documents.")
st.sidebar.title("Model Adjustment")
st.sidebar.markdown("Adjust the settings for your query.")

#Checkpoint 3
#a: Add input text widget for user question
user_question = st.text_area("Enter your question", key="user_question")
#b: Add number of results to the sidebar
n_results = st.number_input("Number of results", 1, 10, 1)

# Checkpoint 4: Create a button that triggers the action of querying the Chroma Collection
if st.button("Get Answers"):
    st.write(f"Question: {user_question}")
    st.write(f"Number of Results: {n_results}")
    try:
        results = collection.query(query_texts=[user_question],n_results=n_results)
    except Exception:
        logger.error("Search request failed; exception details omitted.")
        st.error("Unable to complete your search. Please try again later.")
        st.stop()


    # Checkpoint 5: Access output from `results`
    for res in results.get("documents") or []:
      for txt in res:
          st.write(txt)
