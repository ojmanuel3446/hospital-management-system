import streamlit as st

from services.auth import AuthService


class LoginPage:

    def show(self):
        st.title("Hospital Management System")
        st.subheader("Login")

        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button("Login")

            if submitted:

                if not email or not password:
                    st.error("Please enter your email and password.")
                    return

                try:
                    auth_service = AuthService()

                    profile, error = auth_service.login(
                        email,
                        password
                    )

                    if error:
                        st.error(error)
                        return

                    if not profile:
                        st.error("Login failed. No profile was returned.")
                        return

                    # Store logged-in user
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = profile
                    st.session_state["role"] = profile.get("role", "")

                    # Save profile ID in URL
                    profile_id = profile.get("id")

                    if profile_id:
                        st.query_params["profile_id"] = str(profile_id)

                    # Refresh Streamlit
                    st.rerun()

                except Exception as e:
                    st.error(f"Login error: {e}")