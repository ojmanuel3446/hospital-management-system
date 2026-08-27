import streamlit as st

from ui.login_page import LoginPage
from ui.dashboard_page import DashboardPage
from ui.doctors_page import DoctorsPage
from ui.patients_page import PatientsPage
from ui.appointments_page import AppointmentsPage
from ui.diagnoses_page import DiagnosesPage
from ui.profile_page import ProfilePage

from services.auth import AuthService


st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)


class HospitalApp:

    def __init__(self):

        self.auth_service = AuthService()

        self.pages = {
            "Dashboard": DashboardPage,
            "Doctors": DoctorsPage,
            "Patients": PatientsPage,
            "Appointments": AppointmentsPage,
            "Diagnoses": DiagnosesPage,
            "My Profile": ProfilePage
        }

    # ======================================================
    # RESTORE SESSION AFTER BROWSER REFRESH
    # ======================================================

    def restore_session(self):

        # --------------------------------------------------
        # Already authenticated in current Streamlit session
        # --------------------------------------------------

        if st.session_state.get(
            "authenticated",
            False
        ):

            return True

        # --------------------------------------------------
        # GET PROFILE ID FROM URL
        # --------------------------------------------------

        profile_id = st.query_params.get(
            "profile_id"
        )

        if not profile_id:

            return False

        # --------------------------------------------------
        # LOAD USER FROM DATABASE
        # --------------------------------------------------

        user, error = (
            self.auth_service.get_user_by_id(
                profile_id
            )
        )

        if error:

            return False

        if not user:

            return False

        # --------------------------------------------------
        # RESTORE SESSION
        # --------------------------------------------------

        st.session_state["authenticated"] = True

        st.session_state["user"] = user

        st.session_state["role"] = (
            user.get("role") or ""
        )

        return True

    # ======================================================
    # CLEAR LOGIN
    # ======================================================

    def clear_login(self):

        # Remove authentication data
        st.session_state.pop(
            "authenticated",
            None
        )

        st.session_state.pop(
            "user",
            None
        )

        st.session_state.pop(
            "role",
            None
        )

        # Remove saved profile ID from URL
        if "profile_id" in st.query_params:

            del st.query_params["profile_id"]

    # ======================================================
    # RUN APPLICATION
    # ======================================================

    def run(self):

        # ==================================================
        # TRY TO RESTORE LOGIN
        # ==================================================

        authenticated = (
            self.restore_session()
        )

        # ==================================================
        # LOGIN PAGE
        # ==================================================

        if not authenticated:

            login_page = LoginPage()

            login_page.show()

            return

        # ==================================================
        # GET LOGGED-IN USER
        # ==================================================

        user = (
            st.session_state.get(
                "user",
                {}
            )
        )

        role = (
            st.session_state.get(
                "role",
                ""
            )
        )

        # ==================================================
        # VALIDATE ROLE
        # ==================================================

        if role not in [
            "admin",
            "doctor",
            "patient"
        ]:

            st.error(
                "Invalid user role."
            )

            return

        # ==================================================
        # SIDEBAR
        # ==================================================

        st.sidebar.title(
            "Hospital System"
        )

        first_name = (
            user.get(
                "first_name",
                "User"
            )
        )

        last_name = (
            user.get(
                "last_name",
                ""
            )
        )

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        st.sidebar.write(
            f"Welcome, **{full_name}**!"
        )

        st.sidebar.write(
            f"Role: **{role.capitalize()}**"
        )

        st.sidebar.divider()

        # ==================================================
        # ROLE-BASED PAGES
        # ==================================================

        if role == "admin":

            available_pages = [
                "Dashboard",
                "Doctors",
                "Patients",
                "Appointments",
                "Diagnoses"
            ]

        elif role == "doctor":

            available_pages = [
                "Dashboard",
                "My Profile",
                "Appointments",
                "Diagnoses"
            ]

        elif role == "patient":

            available_pages = [
                "Dashboard",
                "My Profile",
                "Appointments"
            ]

        # ==================================================
        # NAVIGATION (button-style nav panel, no CSS)
        # ==================================================

        if "selected_page" not in st.session_state:

            st.session_state["selected_page"] = available_pages[0]

        # Keep selection valid if role/available_pages changes
        if st.session_state["selected_page"] not in available_pages:

            st.session_state["selected_page"] = available_pages[0]

        st.sidebar.write("**Navigation**")

        for page_name in available_pages:

            is_active = (
                st.session_state["selected_page"] == page_name
            )

            if st.sidebar.button(
                page_name,
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):

                st.session_state["selected_page"] = page_name

                st.rerun()

        selected_page = st.session_state["selected_page"]

        # ==================================================
        # LOGOUT
        # ==================================================

        st.sidebar.divider()

        if st.sidebar.button(
            "Logout",
            use_container_width=True
        ):

            self.clear_login()

            st.rerun()

        # ==================================================
        # DISPLAY PAGE
        # ==================================================

        page_class = (
            self.pages.get(
                selected_page
            )
        )

        if not page_class:

            st.error(
                "Page not found."
            )

            return

        page = page_class()

        page.show()


# ==========================================================
# APPLICATION ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    app = HospitalApp()

    app.run()