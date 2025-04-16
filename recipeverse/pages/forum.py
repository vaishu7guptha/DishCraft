import streamlit as st

def forum_page():
    st.markdown("""
    <div style="background-color: var(--card); padding: 2rem; border-radius: 10px; text-align:center; border:1px solid var(--border);">
        <h2>Community Forum</h2>
        <p>Discuss and share your experiences with recipes below.</p>
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRrdDky2oMzWDYVULNrNP9E6LAPiP5SXUEAfw&s" alt="Forum Discussion" style="width:100%; border-radius:10px; margin-top:1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    if "forum_messages" not in st.session_state:
        st.session_state["forum_messages"] = []
    
    new_message = st.text_area("Share your thoughts or recipe tips:")
    if st.button("Post Message"):
        if new_message.strip():
            st.session_state["forum_messages"].append(new_message.strip())
            st.success("Message posted!")
        else:
            st.warning("Please enter a message before posting.")
    
    st.markdown("### Forum")
    for idx, message in enumerate(reversed(st.session_state["forum_messages"]), 1):
        st.markdown(f"**Message #{idx}:** {message}")
