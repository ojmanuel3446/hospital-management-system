import streamlit as st

from config.database import Database


class DashboardPage:

    def __init__(self):
        self.supabase = Database().get_client()

    # ==========================================================
    # GET COUNTS
    # ==========================================================

    def get_counts(self):
        try:
            doctors_response = (
                self.supabase
                .table("doctors")
                .select("doctor_id", count="exact")
                .execute()
            )

            patients_response = (
                self.supabase
                .table("patients")
                .select("patient_id", count="exact")
                .execute()
            )

            appointments_response = (
                self.supabase
                .table("appointments")
                .select("appointment_id", count="exact")
                .execute()
            )

            diagnoses_response = (
                self.supabase
                .table("diagnoses")
                .select("diagnosis_id", count="exact")
                .execute()
            )

            doctors_count = doctors_response.count or 0
            patients_count = patients_response.count or 0
            appointments_count = appointments_response.count or 0
            diagnoses_count = diagnoses_response.count or 0

            return {
                "doctors": doctors_count,
                "patients": patients_count,
                "appointments": appointments_count,
                "diagnoses": diagnoses_count
            }, None

        except Exception as e:
            return None, str(e)

    # ==========================================================
    # SHOW DASHBOARD
    # ==========================================================

    def show(self):

        st.title("Hospital Management System")

        st.write(
            "Welcome to the Hospital Management System."
        )

        st.divider()

        st.header("Dashboard")

        # ======================================================
        # LOAD COUNTS
        # ======================================================

        counts, error = self.get_counts()

        if error:
            st.error(
                f"Unable to load dashboard statistics:\n\n{error}"
            )
            return

        # ======================================================
        # STATISTICS
        # ======================================================

        col1, col2, col3, col4 = st.columns(4)

        # ======================================================
        # DOCTORS
        # ======================================================

        with col1:
            st.metric(
                label="Doctors",
                value=counts["doctors"]
            )

        # ======================================================
        # PATIENTS
        # ======================================================

        with col2:
            st.metric(
                label="Patients",
                value=counts["patients"]
            )

        # ======================================================
        # APPOINTMENTS
        # ======================================================

        with col3:
            st.metric(
                label="Appointments",
                value=counts["appointments"]
            )

        # ======================================================
        # DIAGNOSES
        # ======================================================

        with col4:
            st.metric(
                label="Diagnoses",
                value=counts["diagnoses"]
            )

        # ======================================================
        # REFRESH
        # ======================================================

        st.divider()

        if st.button(
            "Refresh Dashboard",
            use_container_width=False
        ):
            st.rerun()