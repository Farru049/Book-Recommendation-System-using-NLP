import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import streamlit as st

# Data Preprocessing
def load_and_preprocess_data(file_path):
    try:
        # Load the dataset, skipping bad lines
        books_data = pd.read_csv(file_path, on_bad_lines='skip')  # Skipping bad lines
        
        # Drop rows with missing titles or authors
        books_data = books_data.dropna(subset=['title', 'authors'])
        
        # Clean text columns (remove leading/trailing spaces)
        books_data['title'] = books_data['title'].str.strip()
        books_data['authors'] = books_data['authors'].str.strip()
        
        return books_data
    except Exception as e:
        st.error(f"Error loading or preprocessing data: {e}")
        return None

# Recommender System with NLP (TF-IDF and cosine similarity)
class Recommender:
    def __init__(self, books_data):
        self.books_data = books_data
        self.book_titles = books_data['title'].tolist()
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None

    def build_similarity_matrix(self):
        try:
            # Combine title and authors for better similarity computation
            self.books_data['combined'] = self.books_data['title'] + " " + self.books_data['authors']
            
            # Transform the text data into TF-IDF features
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.books_data['combined'])
        except Exception as e:
            st.error(f"Error building similarity matrix: {e}")

    def get_recommendations(self, book_title):
        try:
            # Find the index of the book based on the title
            if book_title not in self.book_titles:
                st.warning(f"Book '{book_title}' not found in the database.")
                return []
            
            book_idx = self.books_data[self.books_data['title'] == book_title].index[0]
            
            # Calculate the cosine similarity between the selected book and all others
            cosine_sim = cosine_similarity(self.tfidf_matrix[book_idx], self.tfidf_matrix).flatten()
            
            # Get the indices of the most similar books (excluding the selected book itself)
            similar_books_idx = cosine_sim.argsort()[-6:-1][::-1]  # Top 5 similar books
            
            # Return the recommended books with details
            recommended_books = self.books_data.iloc[similar_books_idx]
            return recommended_books
        except Exception as e:
            st.error(f"Error in getting recommendations: {e}")
            return []

def main():
    st.set_page_config(page_title="Book Recommendation System", page_icon="📚")
    
    # Main title and description
    st.title("📚 Book Recommendation System")
    st.markdown("""
        Discover your next great read! This intelligent recommendation system 
        helps you find books similar to your favorites using advanced text analysis.
    """)

    # Use books.csv directly from the directory
    file_path = 'books.csv'

    # Load and preprocess the data
    books_data = load_and_preprocess_data(file_path)
    
    if books_data is not None:
        # Initialize the recommender system
        recommender = Recommender(books_data)
        recommender.build_similarity_matrix()

        # Prepare book titles for autocomplete
        all_titles = sorted(books_data['title'].unique())

        # Book Selection and Recommendations
        st.header("Find Similar Books")
        
        # Create two columns for input and button
        col1, col2 = st.columns([3, 1])

        # Input book title with autocomplete
        with col1:
            selected_book = st.selectbox(
                "Select a book title",
                options=all_titles,
                index=None,
                placeholder="Choose a book or start typing..."
            )

        # Recommend button
        with col2:
            st.write("") # Add some vertical spacing
            recommend_button = st.button("Get Recommendations", type="primary")

        # Display recommendations when button is clicked
        if recommend_button and selected_book:
            # Get recommendations based on the input title
            recommendations = recommender.get_recommendations(selected_book)

            if not recommendations.empty:
                st.subheader(f"Books Similar to '{selected_book}':")
                for idx, book in recommendations.iterrows():
                    with st.expander(f"{book['title']} by {book['authors']}"):
                        # You can add more details here if available in your dataset
                        st.write("Additional book details would go here")
            else:
                st.warning("No recommendations found.")

        # How It Works Section
        st.header("How We Recommend Books")
        st.markdown("""
        Our recommendation system uses advanced Natural Language Processing (NLP) techniques:

        1. **Text Analysis**: We break down book titles and authors into meaningful features
        2. **Similarity Calculation**: We compute how similar books are to each other
        3. **Smart Recommendations**: We suggest the most similar books based on our analysis

        ### Technology
        - Advanced NLP with TF-IDF Vectorization
        - Machine Learning Similarity Matching
        - Powered by Python, Scikit-learn, and Pandas
        """)
    else:
        st.error("Failed to load book data. Please check the data source.")

if __name__ == "__main__":
    main()