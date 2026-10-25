import streamlit as st

# App title
st.title('🎬 Movie Preferences')

# Text input
name = st.text_input('What\'s your name?')

# Slider
age = st.slider('How old are you?', 6, 120, 18)

# Selectbox (dropdown)
genre = st.selectbox('Favorite movie genre:', 
    ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romantic', 'Documentary'])

# Checkbox
wants_popcorn = st.checkbox('Do you like popcorn?')

# Button
if st.button('Get My Movie Recommendation'):
    # Display results
    st.write(f'Hi {name}!')
    
    if 13 < age < 18:
        st.write('You might enjoy some great PG-13 movies!')
    elif age < 13:
        st.write("You might enjoy some great PG movies!")
    else:
        st.write('You have access to all movie ratings!')
    
    # st.write(f'Since you like {genre} movies, here are some recommendations:')
    
    recommendations = [
    "The Matrix",
    "John Wick",
    "Mad Max: Fury Road"
    ]

    st.write(
        f"Since you like {genre} movies, here are some recommendations:\n\n"
        + "\n".join(f"- {movie}" for movie in recommendations)
    )

    if genre == 'Action':
        st.write(f'Since you like {genre} movies, here are some recommendations:\n• The Matrix\n• John Wick\n• Mad Max: Fury Road')
    elif genre == 'Comedy':
        st.write(f'Since you like {genre} movies, here are some recommendations• The Grand Budapest Hotel\n• Superbad\n• Anchorman\n• Zohan\n• Jumanji')
    elif genre == 'Drama':
        st.write(f'Since you like {genre} movies, here are some recommendations• The Shawshank Redemption\n• Forrest Gump\n• Good Will Hunting')
    else:
        st.write(f'Great choice! {genre} has some amazing films!')
    
    if wants_popcorn:
        st.write('🍿 Don\'t forget the popcorn!')
    else:
        st.write('🥤 Maybe some soda instead?')