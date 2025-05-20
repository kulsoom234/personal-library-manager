import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Page config
st.set_page_config(
    page_title="Personal Library Manager System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1E3A8A;
    font-weight: 700;
    text-align: center;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.sub-header {
    font-size: 1.5rem;
    color: #3B82F6;
    font-weight: 600;
    margin-top: 1rem;
}
.success-message {
    background-color: #ECFDF5;
    border-left: 5px solid #10B981;
    padding: 1rem;
    border-radius: 5px;
}
.warning-message {
    background-color: #FEF3C7;
    border-left: 5px solid #F59E0B;
    padding: 1rem;
    border-radius: 5px;
}
.read-badge {
    background-color: #10B981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
}
.unread-badge {
    background-color: #F87171;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
}
.book-card {
    background-color: #F3F4F6;
    border-left: 5px solid #3B82F6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Load/save library
def load_library():
    if os.path.exists('library.json'):
        with open('library.json', 'r') as file:
            st.session_state.library = json.load(file)

def save_library():
    with open('library.json', 'w') as file:
        json.dump(st.session_state.library, file, indent=2)

# Add book
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True

# Remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True

# Search books
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

# Get library stats
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        authors[book['author']] = authors.get(book['author'], 0) + 1
        decade = (int(book['publication_year']) // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades,
    }

# Sidebar
load_library()
st.sidebar.title("📚 Navigation")
lottie_url = "https://assets9.lottiefiles.com/temp/1f20_acAfIn.json"
lottie_book = load_lottieurl(lottie_url)
if lottie_book:
    st_lottie(lottie_book, height=150)

nav = st.sidebar.radio("Go to", ["View Library", "Add Book", "Search Book", "Library Stats"])

st.session_state.current_view = nav.lower().replace(" ", "_")

# Header
st.markdown("<h1 class='main-header'>Personal Library Manager</h1>", unsafe_allow_html=True)

# Add Book View
if st.session_state.current_view == "add_book":
    st.markdown("<h2 class='sub-header'>Add a New Book</h2>", unsafe_allow_html=True)
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            publication_year = st.number_input("Publication Year", 1000, datetime.now().year, step=1)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Science", "Tech", "Fantasy", "Romance", "Poetry", "History", "Religion", "Others"])
            read_status = st.radio("Read Status", ["Read", "Unread"])
        submitted = st.form_submit_button("Add Book")

        if submitted and title and author:
            add_book(title, author, publication_year, genre, read_status == "Read")
            st.success("Book added successfully!")
            st.balloons()

# View Library
elif st.session_state.current_view == "view_library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty.</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class='book-card'>
                        <h4>{book['title']}</h4>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Year:</strong> {book['publication_year']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <span class='{ "read-badge" if book["read_status"] else "unread-badge" }'>
                        { "Read" if book["read_status"] else "Unread" }</span>
                    </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                if col1.button("Remove", key=f"remove_{i}"):
                    remove_book(i)
                    st.rerun()
                if col2.button("Toggle Status", key=f"toggle_{i}"):
                    book['read_status'] = not book['read_status']
                    save_library()
                    st.rerun()

# Search View
elif st.session_state.current_view == "search_book":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search By", ["Title", "Author", "Genre"])
    search_term = st.text_input("Search Term")
    if st.button("Search"):
        search_books(search_term, search_by)
        st.write(f"Found {len(st.session_state.search_results)} result(s):")
        for book in st.session_state.search_results:
            st.markdown(f"""
                <div class='book-card'>
                    <h4>{book['title']}</h4>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <span class='{ "read-badge" if book["read_status"] else "unread-badge" }'>
                    { "Read" if book["read_status"] else "Unread" }</span>
                </div>
            """, unsafe_allow_html=True)

# Stats View
elif st.session_state.current_view == "library_stats":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
    stats = get_library_stats()
    if stats['total_books'] == 0:
        st.warning("Library is empty. Add books to view statistics.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Books", stats['total_books'])
        col2.metric("Read", stats['read_books'])
        col3.metric("Read %", f"{stats['percent_read']:.1f}%")

        # Pie chart
        fig = go.Figure(data=[go.Pie(
            labels=["Read", "Unread"],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4
        )])
        fig.update_layout(title="Read vs Unread Books")
        st.plotly_chart(fig)

        # Genre chart
        if stats['genres']:
            genre_df = pd.DataFrame({
                "Genre": list(stats['genres'].keys()),
                "Count": list(stats['genres'].values())
            })
            st.plotly_chart(px.bar(genre_df, x="Genre", y="Count", title="Books by Genre"))

        # Decade line chart
        if stats['decades']:
            decade_df = pd.DataFrame({
                "Decade": list(stats['decades'].keys()),
                "Count": list(stats['decades'].values())
            })
            st.plotly_chart(px.line(decade_df, x="Decade", y="Count", markers=True, title="Books by Decade"))

# Footer
st.markdown("---")
st.markdown("© 2025 KulsoomFarrukh (FK) | Personal Library Manager", unsafe_allow_html=True)
