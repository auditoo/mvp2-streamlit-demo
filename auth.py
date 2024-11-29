import streamlit as st
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    def logout():
        st.session_state["password_correct"] = False
        st.cache_data.clear()

    with st.sidebar:
        # Return True if the password is validated.
        if st.session_state.get("password_correct", False):
            st.button("Logout", on_click=logout)
            st.success(":smile: Mot de passe correct")
            return True

        # Show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        if "password_correct" in st.session_state:
            st.error("😕 Mot de passe incorrect")
        return False

