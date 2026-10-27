import streamlit as st
import chromadb
from openai import OpenAI

#-----------------------------------------------#
## Checkpoint 1: Set up openai client and and define a completion helper function
#-----------------------------------------------#
client_openai = OpenAI()

def get_completion(prompt):
    response = client_openai.chat.completions.create(

        model="gpt-6-luna",
        messages=[
            {"role": "system", "content": "You're a helpful assistant who looks answers up for a user in a textbook and returns the answer to the user's question. If the answer is not in the textbook, you say 'I'm sorry, I don't have access to that information.'"},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content


##-----------------------------------------------##
## Checkpoint 2: Setup Streamlit App w Chromadb
##-----------------------------------------------##

client_chroma = chromadb.PersistentClient("./")
collection = client_chroma.get_or_create_collection(name="RAG_Assistant", metadata={"hnsw:space": "cosine"})

st.title("Similarity Search App")
st.markdown("This app uses Chroma to perform similarity searches on a collection of documents and OpenAI to answer questions based on the search results.")
st.sidebar.title("Configuration")
st.sidebar.markdown("Adjust the settings for your query.")
n_results = st.sidebar.number_input("Number of results", min_value=1, max_value=10, value=1)
user_question = st.text_area("Ask a question", key="user_question")

if st.button("Get Answers"):
    st.write(f"Question: {user_question}")
    st.write(f"Number of Results: {n_results}")
    results = collection.query(query_texts=[user_question], n_results=n_results, include=["documents", "metadatas"])
    
    search_results = []
    metadatas = results.get("metadatas") or [[]]

    for res in results.get("documents") or []:
        for doc, meta in zip(res, metadatas[0]):
            # Format the document text and its metadata
            metadata_str = ", ".join(f"{key}: {value}" for key, value in meta.items())
            search_results.append(f"{doc}\nMetadata: {metadata_str}")
    search_text = "\n\n".join(search_results)


    ##-----------------------------------------------##
    ## Checkpoint 3: Prompt using RAG Instructions
    ##-----------------------------------------------##
    prompt = f"""Your task is to answer the following user question using the supplied search results.
    User Question: {user_question}
    Search Results: {search_text}
    """
    ## Get and display the response from OpenAI
    response = get_completion(prompt)
    st.write(response)

    ##-----------------------------------------------##
    ## Checkpoint 4: Test your app!
    ##-----------------------------------------------##
    metadata_prompt = f"""
    Your task is to answer the following user question using the supplied search results. At the end of each search result will be Metadata. Cite the passages, their chunk index, and their URL in your answer.
    User Question: {user_question}
    Search Results: {search_text}
    """

    ## Get and display the response from OpenAI
    metadata_response = get_completion(metadata_prompt)
    st.write(metadata_response)
    st.json(results)
    ##-----------------------------------------------##