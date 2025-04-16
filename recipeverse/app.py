
import streamlit as st
import streamlit.components.v1 as components
from pages import login, home, recipe, forum

import base64

def get_logo_base64():
    try:
        with open("/content/recipeverse/assets/logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""  # Fallback if logo missing

st.set_page_config(
    page_title="DishCraft",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session State Initialization
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"
if 'theme' not in st.session_state:
    st.session_state.theme = "light"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Theme Management
def apply_theme():
    theme_css = """
    <style>
    :root {
        --primary: #123458;    /* Navy Blue - Main brand color */
        --secondary: #D4C9BE;  /* Warm Gray - Secondary/Accent */
        --background: #F1EFEC; /* Light Beige - Background */
        --card: #FFFFFF;       /* White - Cards */
        --text: #030303;      /* Black - Primary text */
        --border: #D4C9BE;     /* Warm Gray - Borders */
    }
    
    body {
        background-color: var(--background);
        color: var(--text);
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    .navbar {
        background: var(--card) !important;
        border-bottom: 2px solid var(--secondary);
        box-shadow: 0 2px 8px rgba(3,3,3,0.1);
    }
    
    .nav-item {
        color: var(--text) !important;
        transition: all 0.2s ease;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: 500;
    }
    
    .nav-item:hover {
        background: var(--secondary);
        color: var(--text) !important;
    }
    
    .active {
        background: var(--primary);
        color: white !important;
    }
    </style>
    """
    st.markdown(theme_css, unsafe_allow_html=True)

def handle_navigation():
    params = st.query_params.to_dict()
    if 'page' in params:
        new_page = params['page']
        if new_page != st.session_state.current_page:
            st.session_state.current_page = new_page
            st.rerun()

def navbar():
    current_page = st.session_state.get('current_page', 'Home')
    login_text = 'Login' if not st.session_state.logged_in else 'Logout'
    login_page = 'Login' if not st.session_state.logged_in else 'Home'

    # Create columns for layout control
    col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1])
    
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem;">
            <img src="data:image/png;base64,{get_logo_base64()}" alt="Logo" style="height: 45px;">
            <div class="title" style="font-size: 1.8rem; font-weight: 700; color: var(--primary);">
                DishCraft
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("Home", type="primary" if current_page == 'Home' else "secondary"):
            st.session_state.current_page = 'Home'
            st.rerun()

    with col3:
        if st.button("Generate", type="primary" if current_page == 'Generate' else "secondary"):
            st.session_state.current_page = 'Generate'
            st.rerun()

    with col4:
        if st.button("Forum", type="primary" if current_page == 'Forum' else "secondary"):
            st.session_state.current_page = 'Forum'
            st.rerun()

    with col5:
        if st.button(login_text, type="primary" if current_page == login_page else "secondary"):
            st.session_state.current_page = login_page
            if login_text == 'Logout':
                st.session_state.logged_in = False
            st.rerun()

def main():
    # Handle navigation and theme
    handle_navigation()
    
    # Apply theme
    apply_theme()
    
    # Show navbar
    navbar()
    
    # Page routing
    pages = {
        "Home": home.home_page,
        "Generate": recipe.recipe_page,
        "Forum": forum.forum_page,
        "Login": login.login_page
    }
    
    if st.session_state.current_page in pages:
        pages[st.session_state.current_page]()
    else:
        home.home_page()
    
    st.markdown("</div>", unsafe_allow_html=True)

    components.html(
        """
        <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'setPage') {
                const params = new URLSearchParams(window.location.search);
                params.set('page', event.data.data);
                window.history.pushState(null, '', '?' + params.toString());
                window.dispatchEvent(new PopStateEvent('popstate'));
            }
        });
        </script>
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
