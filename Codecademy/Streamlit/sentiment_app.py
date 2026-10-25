import streamlit as st
import pandas as pd
import numpy as np
import re
import time
import io
from datetime import datetime

from transformers import pipeline
import torch

@st.cache_resource
def load_sentiment_model(model_name):
    """Load and cache the sentiment analysis model"""
    try:
        classifier = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1,
            return_all_scores=True
        )
        return classifier
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# CHECKPOINT 1: Add interactive preprocessing function
def preprocess_text_interactive(text, remove_punctuation=False, convert_case=None, remove_emojis=False):
    """Interactive text preprocessing with options"""
    import string
    
    processed_text = text
    
    # Remove emojis (simple approach - removes non-ASCII characters)
    if remove_emojis:
        processed_text = ''.join(char for char in processed_text if ord(char) < 128)
    
    # Handle case conversion
    if convert_case == "lowercase":
        processed_text = processed_text.lower()
    elif convert_case == "uppercase":
        processed_text = processed_text.upper()
    
    # Remove punctuation
    if remove_punctuation:
        processed_text = processed_text.translate(str.maketrans('', '', string.punctuation))
    
    # Clean up extra whitespace
    processed_text = ' '.join(processed_text.split())
    
    return processed_text

def analyze_sentiment_batch(texts, classifier, batch_size=16):
    """Analyze sentiment for multiple texts in batches"""
    if classifier is None:
        return None
    
    results = []
    progress_bar = st.progress(0)
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            batch_results = classifier(batch)
            
            for result in batch_results:
                # Find the highest scoring sentiment
                best_result = max(result, key=lambda x: x['score'])
                results.append({
                    'sentiment': best_result['label'].upper(),
                    'confidence': best_result['score']
                })
            
            # Update progress
            progress = min(1.0, (i + batch_size) / len(texts))
            progress_bar.progress(progress)
            
        except Exception as e:
            st.error(f"Error processing batch {i//batch_size + 1}: {e}")
            # Add empty results for failed batch
            results.extend([{'sentiment': 'NEUTRAL', 'confidence': 0.5}] * len(batch))
    
    progress_bar.empty()
    return results

if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False
if 'classifier' not in st.session_state:
    st.session_state.classifier = None

# CHECKPOINT 3: Add basic text statistics function
def analyze_basic_text_stats(text):
    """Analyze basic text characteristics"""
    if not text:
        return None
    
    # Basic statistics
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    char_count_no_spaces = len(text.replace(' ', ''))
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    # Punctuation analysis
    exclamation_count = text.count('!')
    question_count = text.count('?')
    period_count = text.count('.')
    comma_count = text.count(',')
    
    # Emoji detection (simple check for non-ASCII)
    emoji_count = sum(1 for char in text if ord(char) > 127)
    
    # All caps detection
    caps_words = [word for word in words if word.isupper() and len(word) > 1]
    caps_percentage = (len(caps_words) / len(words)) * 100 if words else 0
    
    return {
        'word_count': word_count,
        'char_count': char_count,
        'char_count_no_spaces': char_count_no_spaces,
        'avg_word_length': avg_word_length,
        'exclamation_count': exclamation_count,
        'question_count': question_count,
        'period_count': period_count,
        'comma_count': comma_count,
        'emoji_count': emoji_count,
        'caps_words': caps_words,
        'caps_percentage': caps_percentage
    }

# CHECKPOINT 4: Add positive/negative word analysis function
def analyze_sentiment_words(text):
    """Analyze positive and negative words in the text"""
    if not text:
        return None
    
    # Extended word lists for better analysis
    positive_words = [
        'love', 'great', 'excellent', 'amazing', 'fantastic', 'wonderful', 'perfect', 
        'awesome', 'brilliant', 'outstanding', 'superb', 'magnificent', 'incredible',
        'good', 'nice', 'happy', 'pleased', 'satisfied', 'delighted', 'thrilled',
        'best', 'favorite', 'enjoy', 'recommend', 'impressed', 'beautiful', 'lovely'
    ]
    
    negative_words = [
        'hate', 'terrible', 'awful', 'horrible', 'worst', 'disappointing', 'poor',
        'bad', 'dreadful', 'useless', 'disgusting', 'pathetic', 'annoying',
        'sad', 'angry', 'frustrated', 'upset', 'worried', 'concerned', 'dissatisfied',
        'failed', 'broken', 'wrong', 'problem', 'issue', 'complaint', 'regret'
    ]
    
    # Convert text to lowercase and split into words
    words = text.lower().replace(',', ' ').replace('.', ' ').replace('!', ' ').replace('?', ' ').split()
    
    # Find sentiment words
    found_positive = [word for word in words if word in positive_words]
    found_negative = [word for word in words if word in negative_words]
    
    # Calculate statistics
    positive_count = len(found_positive)
    negative_count = len(found_negative)
    total_words = len(words)
    sentiment_word_count = positive_count + negative_count
    
    # Calculate ratios
    positive_ratio = (positive_count / total_words * 100) if total_words > 0 else 0
    negative_ratio = (negative_count / total_words * 100) if total_words > 0 else 0
    sentiment_ratio = (sentiment_word_count / total_words * 100) if total_words > 0 else 0
    
    # Determine word-level sentiment balance
    if positive_count > negative_count:
        word_sentiment = "Positive"
        word_confidence = positive_count / (positive_count + negative_count) if sentiment_word_count > 0 else 0
    elif negative_count > positive_count:
        word_sentiment = "Negative"
        word_confidence = negative_count / (positive_count + negative_count) if sentiment_word_count > 0 else 0
    else:
        word_sentiment = "Neutral"
        word_confidence = 0.5
    
    return {
        'positive_words': found_positive,
        'negative_words': found_negative,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'positive_ratio': positive_ratio,
        'negative_ratio': negative_ratio,
        'sentiment_ratio': sentiment_ratio,
        'word_sentiment': word_sentiment,
        'word_confidence': word_confidence,
        'total_words': total_words
    }

def preprocess_text(text):
    """Clean and preprocess text for better analysis"""
    if pd.isna(text):
        return ""
    
    text = str(text)
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = ' '.join(text.split())
    return text[:512]

def create_sentiment_metrics(df):
    """Create sentiment distribution metrics"""
    if df is None or len(df) == 0:
        st.warning("No data available for analysis.")
        return
    
    total = len(df)
    sentiment_counts = df['sentiment'].value_counts()
    
    positive_count = sentiment_counts.get('POSITIVE', 0)
    negative_count = sentiment_counts.get('NEGATIVE', 0)
    neutral_count = sentiment_counts.get('NEUTRAL', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyzed", f"{total:,}", help="Total number of texts analyzed")
    
    with col2:
        positive_pct = (positive_count / total * 100) if total > 0 else 0
        st.metric("Positive", f"{positive_count:,} ({positive_pct:.1f}%)", 
                 delta=f"{positive_pct:.1f}%", delta_color="normal")
    
    with col3:
        negative_pct = (negative_count / total * 100) if total > 0 else 0
        st.metric("Negative", f"{negative_count:,} ({negative_pct:.1f}%)", 
                 delta=f"-{negative_pct:.1f}%", delta_color="inverse")
    
    with col4:
        neutral_pct = (neutral_count / total * 100) if total > 0 else 0
        st.metric("Neutral", f"{neutral_count:,} ({neutral_pct:.1f}%)", 
                 delta=f"{neutral_pct:.1f}%", delta_color="off")

# Initialize session state
if 'text_history' not in st.session_state:
    st.session_state.text_history = []

# Main App
st.markdown('📊 AI Sentiment Analysis Dashboard')

st.markdown("""
Analyze sentiment in text data using state-of-the-art AI models from Hugging Face. 
Upload your data or enter text directly to get insights into emotional tone and sentiment patterns.
""")

# Sidebar Configuration
with st.sidebar:
    st.header("🛠️ Configuration")
    
    # Model selection with display names and actual model names
    model_options = {
        "cardiffnlp/twitter-roberta-base-sentiment-latest (Recommended)": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "distilbert-base-uncased-finetuned-sst-2-english (Faster)": "distilbert-base-uncased-finetuned-sst-2-english"
    }
    
    model_display_name = st.selectbox(
        "Choose Model",
        list(model_options.keys())
    )
    
    # Get the actual model name
    actual_model_name = model_options[model_display_name]
    
    st.subheader("Analysis Options")
    batch_size = st.slider("Batch Size", 8, 32, 16, help="Larger batches are faster but use more memory")
    confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5, help="Minimum confidence to highlight results")
    
    if st.button("Load Model", type="primary"):
        with st.spinner(f"Loading model: {actual_model_name}..."):
            st.session_state.classifier = load_sentiment_model(actual_model_name)
            if st.session_state.classifier:
                st.session_state.model_loaded = True
                st.success("Model loaded successfully!")
                st.balloons()
            else:
                st.session_state.model_loaded = False
                st.error("Failed to load model")

# Display model status
if st.session_state.model_loaded:
    st.success("✅ Model is loaded and ready!")
else:
    st.info("ℹ️ Please load a model from the sidebar to begin analysis.")

# Main Content Tabs
tab1, tab2, tab3 = st.tabs(["📝 Text Input", "📁 File Upload", "📊 Analysis History"])

# Tab 1: Text Input
with tab1:
    # CHECKPOINT 1: Interactive text preprocessing interface
    st.header("Interactive Text Analysis")
    
    # Preprocessing experiments section
    st.subheader("Text Preprocessing Experiments")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Text input with examples
        example = st.selectbox(
            "Try Example Texts",
            [
                "Custom",
                "I LOVE this!!! 😍😍😍",
                "This is terrible... 😢",
                "It's okay, nothing special.",
                "WOW!!! AMAZING!!! 🎉🎉🎉",
                "Not sure how I feel about this???",
            ]
        )
        
        if example == "Custom":
            user_text = st.text_area(
                "Enter text to analyze:",
                placeholder="Type or paste your text here...",
                height=120
            )
        else:
            user_text = st.text_area(
                "Enter text to analyze:",
                value=example,
                height=120
            )
        
        # Preprocessing options
        st.subheader("Preprocessing Options")
        remove_punctuation = st.checkbox("Remove punctuation", help="Remove !?.,; etc.")
        convert_case = st.selectbox("Case conversion", ["None", "lowercase", "uppercase"])
        remove_emojis = st.checkbox("Remove emojis", help="Remove emoji characters")
    
    with col2:
        if user_text:
            # Show preprocessing preview
            st.subheader("Preprocessing Preview")
            
            case_option = None if convert_case == "None" else convert_case
            processed_text = preprocess_text_interactive(
                user_text, 
                remove_punctuation, 
                case_option, 
                remove_emojis
            )
            
            st.write("**Original:**")
            st.text_area("", value=user_text, height=60, disabled=True, key="original")
            
            st.write("**Processed:**")
            st.text_area("", value=processed_text, height=60, disabled=True, key="processed")
            
            # Show differences
            if user_text != processed_text:
                changes = []
                if remove_punctuation and any(p in user_text for p in "!?.,;"):
                    changes.append("punctuation removed")
                if case_option and case_option == "lowercase" and any(c.isupper() for c in user_text):
                    changes.append("converted to lowercase")
                if case_option and case_option == "uppercase" and any(c.islower() for c in user_text):
                    changes.append("converted to uppercase")
                if remove_emojis and any(ord(c) > 127 for c in user_text):
                    changes.append("emojis removed")
                
                if changes:
                    st.info(f"Changes: {', '.join(changes)}")

    # CHECKPOINT 2: Analysis section with comparative analysis
    col1, col2 = st.columns([1, 3])
    with col1:
        analyze_button = st.button("Compare Analysis", type="primary", disabled=not st.session_state.model_loaded)
        save_to_history = st.checkbox("Save to history", value=True)

    if analyze_button and user_text and st.session_state.classifier:
        st.markdown("---")
        st.subheader("Comparative Analysis Results")
        
        with st.spinner("Analyzing both versions..."):
            # Analyze original text
            original_cleaned = preprocess_text(user_text)  # Basic cleaning
            original_result = st.session_state.classifier([original_cleaned])[0]
            original_best = max(original_result, key=lambda x: x['score'])
            
            # Analyze preprocessed text if different
            case_option = None if convert_case == "None" else convert_case
            processed_text = preprocess_text_interactive(
                user_text, remove_punctuation, case_option, remove_emojis
            )
            processed_cleaned = preprocess_text(processed_text)
            
            if processed_cleaned != original_cleaned:
                processed_result = st.session_state.classifier([processed_cleaned])[0]
                processed_best = max(processed_result, key=lambda x: x['score'])
            else:
                processed_result = original_result
                processed_best = original_best
            
            # Display comparative results
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Original Text Analysis**")
                original_sentiment = original_best['label'].upper()
                original_confidence = original_best['score']
                
                color_map = {'POSITIVE': '🟢', 'NEGATIVE': '🔴', 'NEUTRAL': '🔵'}
                st.metric(
                    "Sentiment", 
                    f"{color_map.get(original_sentiment, '⚪')} {original_sentiment}"
                )
                st.metric("Confidence", f"{original_confidence:.2%}")
                st.progress(original_confidence)
            
            with col2:
                st.write("**Preprocessed Text Analysis**")
                processed_sentiment = processed_best['label'].upper()
                processed_confidence = processed_best['score']
                
                st.metric(
                    "Sentiment", 
                    f"{color_map.get(processed_sentiment, '⚪')} {processed_sentiment}"
                )
                st.metric("Confidence", f"{processed_confidence:.2%}")
                st.progress(processed_confidence)
            
            # Comparison insights
            st.subheader("Comparison Insights")
            
            confidence_diff = processed_confidence - original_confidence
            sentiment_changed = original_sentiment != processed_sentiment
            
            if sentiment_changed:
                st.warning(f"⚠️ Sentiment prediction changed from {original_sentiment} to {processed_sentiment}")
            else:
                st.success("✅ Sentiment prediction remained consistent")
            
            if abs(confidence_diff) > 0.1:
                direction = "increased" if confidence_diff > 0 else "decreased"
                st.info(f"Confidence {direction} by {abs(confidence_diff):.1%} after preprocessing")
            
            # CHECKPOINT 3: Basic text analysis
            st.markdown("---")
            st.subheader("📊 Text Characteristics")
            
            # Analyze the original text
            text_stats = analyze_basic_text_stats(user_text)
            
            if text_stats:
                # Display basic stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Words", text_stats['word_count'])
                with col2:
                    st.metric("Characters", text_stats['char_count'])
                with col3:
                    st.metric("Avg Word Length", f"{text_stats['avg_word_length']:.1f}")
                with col4:
                    st.metric("Emojis", text_stats['emoji_count'])
                
                # Punctuation breakdown
                st.write("**Punctuation Analysis:**")
                punct_data = {
                    'Exclamations (!)': text_stats['exclamation_count'],
                    'Questions (?)': text_stats['question_count'],
                    'Periods (.)': text_stats['period_count'],
                    'Commas (,)': text_stats['comma_count']
                }
                
                punct_cols = st.columns(4)
                for i, (punct_type, count) in enumerate(punct_data.items()):
                    with punct_cols[i]:
                        st.write(f"**{punct_type}:** {count}")
                
                # Capitalization analysis
                if text_stats['caps_percentage'] > 0:
                    st.write(f"**Capitalization:** {text_stats['caps_percentage']:.1f}% of words are ALL CAPS")
                    if text_stats['caps_words']:
                        st.write(f"ALL CAPS words: {', '.join(text_stats['caps_words'][:5])}")

            # CHECKPOINT 4: Positive/negative word analysis
            st.markdown("---")
            st.subheader("🎯 Sentiment Word Analysis")
            
            word_analysis = analyze_sentiment_words(user_text)
            
            if word_analysis:
                # Main sentiment word metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Positive Words", word_analysis['positive_count'])
                with col2:
                    st.metric("Negative Words", word_analysis['negative_count'])
                with col3:
                    st.metric("Word-Level Sentiment", word_analysis['word_sentiment'])
                with col4:
                    st.metric("Sentiment Word %", f"{word_analysis['sentiment_ratio']:.1f}%")
                
                # Show found words
                col1, col2 = st.columns(2)
                
                with col1:
                    if word_analysis['positive_words']:
                        st.success("**Positive words found:**")
                        st.write(", ".join(word_analysis['positive_words']))
                    else:
                        st.info("No positive indicator words found")
                
                with col2:
                    if word_analysis['negative_words']:
                        st.error("**Negative words found:**")
                        st.write(", ".join(word_analysis['negative_words']))
                    else:
                        st.info("No negative indicator words found")
                
                # Word-level vs AI prediction comparison
                st.subheader("Word Analysis vs AI Prediction")
                
                ai_sentiment = processed_sentiment
                word_sentiment = word_analysis['word_sentiment'].upper()
                
                if ai_sentiment == word_sentiment:
                    st.success(f"✅ Word analysis ({word_sentiment}) matches AI prediction ({ai_sentiment})")
                else:
                    st.warning(f"⚠️ Word analysis suggests {word_sentiment} but AI predicts {ai_sentiment}")
                    st.info("This difference shows the AI considers context, not just individual words")
                
                # Insights based on word analysis
                insights = []
                
                if word_analysis['sentiment_ratio'] < 5:
                    insights.append("Few sentiment indicator words - prediction may rely on subtle context")
                
                if word_analysis['positive_count'] > 0 and word_analysis['negative_count'] > 0:
                    insights.append("Mixed sentiment words detected - text contains both positive and negative elements")
                
                if word_analysis['sentiment_ratio'] > 20:
                    insights.append("High density of sentiment words - strong emotional expression")
                
                if insights:
                    st.subheader("💡 Word Analysis Insights")
                    for insight in insights:
                        st.write(f"• {insight}")

            # Save to history if requested
            if save_to_history:
                st.session_state.text_history.append({
                    'text': user_text[:100] + '...' if len(user_text) > 100 else user_text,
                    'sentiment': processed_sentiment,  # Use preprocessed result
                    'confidence': processed_confidence,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'preprocessing_used': remove_punctuation or (case_option is not None) or remove_emojis
                })

# Tab 2: File Upload (unchanged from original)
with tab2:
    st.header("Bulk File Analysis")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file with text data to analyze"
    )
    
    if uploaded_file:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! Found {len(df)} rows.")
            
            # Show preview
            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(df.head(10))
            
            # Column selection
            text_column = st.selectbox(
                "Select the column containing text to analyze:",
                options=df.columns.tolist(),
                help="Choose which column contains the text you want to analyze"
            )
            
            # Show sample from selected column
            if text_column:
                st.write("**Sample texts from selected column:**")
                sample_texts = df[text_column].dropna().head(3).tolist()
                for i, text in enumerate(sample_texts, 1):
                    st.write(f"{i}. {str(text)[:100]}{'...' if len(str(text)) > 100 else ''}")
            
            # Analysis button
            if st.button("Analyze File", type="primary", disabled=not st.session_state.model_loaded):
                if not st.session_state.classifier:
                    st.error("Please load the model first!")
                else:
                    texts = df[text_column].fillna("").apply(preprocess_text).tolist()
                    
                    # Limit for performance in restrictive environments
                    if len(texts) > 100:
                        st.warning(f"Large file ({len(texts)} rows). Processing first 100 rows for performance.")
                        texts = texts[:100]
                        df = df.head(100)
                    
                    with st.spinner(f"Analyzing {len(texts)} texts with AI model..."):
                        results = analyze_sentiment_batch(texts, st.session_state.classifier, batch_size)
                        
                        if results:
                            # Add results to the dataframe
                            df['sentiment'] = [r['sentiment'] for r in results]
                            df['confidence'] = [r['confidence'] for r in results]
                            
                            # Add to history (sample only to avoid memory issues)
                            for i, result in enumerate(results[:20]):  # Limit to first 20 for history
                                st.session_state.text_history.append({
                                    'text': texts[i][:100] + '...' if len(texts[i]) > 100 else texts[i],
                                    'sentiment': result['sentiment'],
                                    'confidence': result['confidence'],
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                            
                            st.success("Analysis complete!")
                            st.balloons()
                            
                            # Show results metrics
                            create_sentiment_metrics(df)
                            
                            # Show results dataframe
                            st.subheader("📊 Analysis Results")
                            st.dataframe(
                                df[['sentiment', 'confidence', text_column]].head(20),
                                use_container_width=True
                            )
                            
                            # Download results
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download Results as CSV",
                                data=csv,
                                file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.error("Batch analysis failed!")
                    
        except Exception as e:
            st.error(f"Error reading file: {e}")

# Tab 3: Analysis History (unchanged from original)
with tab3:
    st.header("Analysis History")
    
    if st.session_state.text_history:
        history_df = pd.DataFrame(st.session_state.text_history)
        
        # Show summary metrics
        create_sentiment_metrics(history_df)
        
        # Show history table
        st.subheader("Recent Analyses")
        st.dataframe(
            history_df.tail(20)[['timestamp', 'sentiment', 'confidence', 'text']],
            use_container_width=True
        )
        
        # Clear history button
        if st.button("Clear History", type="secondary"):
            st.session_state.text_history = []
            st.success("History cleared!")
            st.rerun()
            
    else:
        st.info("No analysis history available. Start analyzing some text!")