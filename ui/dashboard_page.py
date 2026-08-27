import streamlit as st

from datetime import datetime, date

import calendar

from config.database import Database


class DashboardPage:

    def __init__(self):
        self.supabase = Database().get_client()

    # ==========================================================
    # GET CURRENT USER
    # ==========================================================

    def get_current_user(self):
        return st.session_state.get("user", {})

    # ==========================================================
    # GET CURRENT ROLE
    # ==========================================================

    def get_role(self):

        user = self.get_current_user()

        role = (
            st.session_state.get("role")
            or user.get("role")
            or ""
        )

        return str(role).lower().strip()

    # ==========================================================
    # ADMIN DASHBOARD
    # ==========================================================

    def show_admin_dashboard(self):

        st.title("Hospital Management System")

        st.write(
            "Welcome to the Hospital Management System."
        )

        st.divider()

        st.header("Dashboard")

        # ======================================================
        # GET DOCTOR COUNT
        # ======================================================

        doctors_count = 0

        try:

            response = (
                self.supabase
                .table("doctors")
                .select(
                    "doctor_id",
                    count="exact"
                )
                .execute()
            )

            doctors_count = response.count or 0

        except Exception as e:

            st.error(
                f"Unable to load doctors: {e}"
            )

        # ======================================================
        # GET PATIENT COUNT
        # ======================================================

        patients_count = 0

        try:

            response = (
                self.supabase
                .table("patients")
                .select(
                    "patient_id",
                    count="exact"
                )
                .execute()
            )

            patients_count = response.count or 0

        except Exception as e:

            st.error(
                f"Unable to load patients: {e}"
            )

        # ======================================================
        # GET APPOINTMENT COUNT
        # ======================================================

        appointments_count = 0

        try:

            response = (
                self.supabase
                .table("appointments")
                .select(
                    "appointment_id",
                    count="exact"
                )
                .execute()
            )

            appointments_count = response.count or 0

        except Exception as e:

            st.error(
                f"Unable to load appointments: {e}"
            )

        # ======================================================
        # GET DIAGNOSIS COUNT
        # ======================================================

        diagnoses_count = 0

        try:

            response = (
                self.supabase
                .table("diagnoses")
                .select(
                    "diagnosis_id",
                    count="exact"
                )
                .execute()
            )

            diagnoses_count = response.count or 0

        except Exception as e:

            st.error(
                f"Unable to load diagnoses: {e}"
            )

        # ======================================================
        # DISPLAY STATISTICS
        # ======================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Doctors",
                doctors_count
            )

        with col2:

            st.metric(
                "Patients",
                patients_count
            )

        with col3:

            st.metric(
                "Appointments",
                appointments_count
            )

        with col4:

            st.metric(
                "Diagnoses",
                diagnoses_count
            )

    # ==========================================================
    # GET LOGGED-IN DOCTOR PROFILE ID
    # ==========================================================

    def get_profile_id(self):

        try:

            user = self.get_current_user()

            if not user:

                return None, (
                    "No logged-in user was found."
                )

            profile_id = (
                user.get("profile_id")
                or user.get("id")
            )

            if not profile_id:

                return None, (
                    "Doctor profile ID was not found."
                )

            return profile_id, None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # GET LOGGED-IN DOCTOR ID
    # ==========================================================

    def get_doctor_id(self):

        try:

            profile_id, error = (
                self.get_profile_id()
            )

            if error:

                return None, error

            response = (
                self.supabase
                .table("doctors")
                .select("doctor_id")
                .eq(
                    "profile_id",
                    profile_id
                )
                .limit(1)
                .execute()
            )

            data = response.data or []

            if not data:

                return None, (
                    "No doctor record is linked to this account.\n\n"
                    f"Profile ID: {profile_id}\n\n"
                    "Please make sure this doctor's profile exists "
                    "in the doctors table and that doctors.profile_id "
                    "matches profiles.id."
                )

            doctor_id = data[0].get(
                "doctor_id"
            )

            if not doctor_id:

                return None, (
                    "Doctor record exists but doctor_id is missing."
                )

            return doctor_id, None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # GET DOCTOR APPOINTMENTS
    # ==========================================================

    def get_doctor_appointments(
        self,
        doctor_id
    ):

        try:

            response = (
                self.supabase
                .table("appointments")
                .select(
                    """
                    appointment_id,
                    patient_id,
                    doctor_id,
                    appointment_date,
                    status,
                    reason_for_visit,
                    patients (
                        patient_id,
                        profile_id,
                        profiles (
                            first_name,
                            last_name
                        )
                    )
                    """
                )
                .eq(
                    "doctor_id",
                    doctor_id
                )
                .order(
                    "appointment_date",
                    desc=False
                )
                .execute()
            )

            return response.data or [], None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # GET MONTHLY APPOINTMENTS
    # ==========================================================

    def get_month_appointments(
        self,
        doctor_id,
        year,
        month
    ):

        try:

            start_date = datetime(
                year,
                month,
                1
            )

            if month == 12:

                end_date = datetime(
                    year + 1,
                    1,
                    1
                )

            else:

                end_date = datetime(
                    year,
                    month + 1,
                    1
                )

            response = (
                self.supabase
                .table("appointments")
                .select(
                    """
                    appointment_id,
                    patient_id,
                    doctor_id,
                    appointment_date,
                    status,
                    reason_for_visit,
                    patients (
                        patient_id,
                        profile_id,
                        profiles (
                            first_name,
                            last_name
                        )
                    )
                    """
                )
                .eq(
                    "doctor_id",
                    doctor_id
                )
                .gte(
                    "appointment_date",
                    start_date.isoformat()
                )
                .lt(
                    "appointment_date",
                    end_date.isoformat()
                )
                .order(
                    "appointment_date",
                    desc=False
                )
                .execute()
            )

            return response.data or [], None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # CALCULATE STATISTICS
    # ==========================================================

    def get_statistics(
        self,
        appointments
    ):

        today = date.today()

        current_year = today.year
        current_month = today.month

        today_count = 0
        month_count = 0
        pending_count = 0
        completed_count = 0

        for appointment in appointments:

            appointment_date = (
                appointment.get(
                    "appointment_date"
                )
            )

            if not appointment_date:

                continue

            try:

                appointment_datetime = (
                    datetime.fromisoformat(
                        appointment_date.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                appointment_day = (
                    appointment_datetime.date()
                )

            except Exception:

                continue

            status = (
                str(
                    appointment.get(
                        "status",
                        ""
                    )
                )
                .lower()
                .strip()
            )

            if appointment_day == today:

                today_count += 1

            if (
                appointment_datetime.year
                == current_year
                and
                appointment_datetime.month
                == current_month
            ):

                month_count += 1

            if status == "pending":

                pending_count += 1

            elif status == "completed":

                completed_count += 1

        return {
            "today": today_count,
            "month": month_count,
            "pending": pending_count,
            "completed": completed_count
        }

    # ==========================================================
    # GET PATIENT NAME
    # ==========================================================

    def get_patient_name(
        self,
        appointment
    ):

        patient_name = "Unknown Patient"

        patient = appointment.get(
            "patients"
        )

        if not patient:

            return patient_name

        patient_profile = patient.get(
            "profiles"
        )

        if not patient_profile:

            return patient_name

        first_name = patient_profile.get(
            "first_name",
            ""
        )

        last_name = patient_profile.get(
            "last_name",
            ""
        )

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        if full_name:

            return full_name

        return patient_name

    # ==========================================================
    # FORMAT APPOINTMENT DATE
    # ==========================================================

    def format_appointment_datetime(
        self,
        appointment
    ):

        appointment_date = (
            appointment.get(
                "appointment_date"
            )
        )

        if not appointment_date:

            return (
                "Date unavailable",
                "Time unavailable"
            )

        try:

            dt = datetime.fromisoformat(
                appointment_date.replace(
                    "Z",
                    "+00:00"
                )
            )

            formatted_date = dt.strftime(
                "%B %d, %Y"
            )

            formatted_time = dt.strftime(
                "%I:%M %p"
            )

            return (
                formatted_date,
                formatted_time
            )

        except Exception:

            return (
                "Date unavailable",
                "Time unavailable"
            )

    # ==========================================================
    # SHOW MONTHLY CALENDAR
    # ==========================================================

    def show_calendar(
        self,
        appointments,
        year,
        month
    ):

        month_name = calendar.month_name[
            month
        ]

        st.subheader(
            f"{month_name} {year}"
        )

        appointments_by_date = {}

        for appointment in appointments:

            appointment_datetime = (
                appointment.get(
                    "appointment_date"
                )
            )

            if not appointment_datetime:

                continue

            try:

                dt = datetime.fromisoformat(
                    appointment_datetime.replace(
                        "Z",
                        "+00:00"
                    )
                )

                appointment_day = dt.day

            except Exception:

                continue

            if appointment_day not in appointments_by_date:

                appointments_by_date[
                    appointment_day
                ] = []

            appointments_by_date[
                appointment_day
            ].append(
                appointment
            )

        cal = calendar.Calendar(
            firstweekday=6
        )

        weeks = cal.monthdayscalendar(
            year,
            month
        )

        day_names = [
            "Sun",
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat"
        ]

        header_columns = st.columns(7)

        for index, day_name in enumerate(
            day_names
        ):

            with header_columns[index]:

                st.markdown(
                    f"**{day_name}**"
                )

        for week in weeks:

            columns = st.columns(7)

            for index, day in enumerate(
                week
            ):

                with columns[index]:

                    if day == 0:

                        st.write("")

                        continue

                    day_appointments = (
                        appointments_by_date.get(
                            day,
                            []
                        )
                    )

                    if day_appointments:

                        st.markdown(
                            f"### {day}"
                        )

                    else:

                        st.markdown(
                            f"**{day}**"
                        )

                    for appointment in day_appointments:

                        appointment_datetime = (
                            appointment.get(
                                "appointment_date"
                            )
                        )

                        try:

                            dt = datetime.fromisoformat(
                                appointment_datetime.replace(
                                    "Z",
                                    "+00:00"
                                )
                            )

                            appointment_time = (
                                dt.strftime(
                                    "%I:%M %p"
                                )
                            )

                        except Exception:

                            appointment_time = (
                                "Time unavailable"
                            )

                        patient_name = (
                            self.get_patient_name(
                                appointment
                            )
                        )

                        st.caption(
                            f"🕐 {appointment_time}"
                        )

                        st.write(
                            patient_name
                        )

                        status = (
                            appointment.get(
                                "status"
                            )
                        )

                        if status:

                            st.caption(
                                f"Status: {status}"
                            )

                    st.divider()

    # ==========================================================
    # SHOW APPOINTMENT LIST
    # ==========================================================

    def show_appointment_list(
        self,
        appointments
    ):

        st.subheader(
            "Upcoming Appointments"
        )

        today = date.today()

        upcoming = []

        for appointment in appointments:

            appointment_datetime = (
                appointment.get(
                    "appointment_date"
                )
            )

            if not appointment_datetime:

                continue

            try:

                dt = datetime.fromisoformat(
                    appointment_datetime.replace(
                        "Z",
                        "+00:00"
                    )
                )

                if dt.date() >= today:

                    upcoming.append(
                        appointment
                    )

            except Exception:

                continue

        if not upcoming:

            st.info(
                "You have no upcoming appointments."
            )

            return

        for appointment in upcoming[:10]:

            (
                formatted_date,
                formatted_time
            ) = self.format_appointment_datetime(
                appointment
            )

            patient_name = (
                self.get_patient_name(
                    appointment
                )
            )

            status = appointment.get(
                "status",
                "Pending"
            )

            reason = (
                appointment.get(
                    "reason_for_visit"
                )
                or
                "No reason provided"
            )

            with st.container(
                border=True
            ):

                col1, col2, col3 = st.columns(
                    [2, 2, 3]
                )

                with col1:

                    st.write(
                        f"**{formatted_date}**"
                    )

                    st.write(
                        f"🕐 {formatted_time}"
                    )

                with col2:

                    st.write(
                        "**Patient**"
                    )

                    st.write(
                        patient_name
                    )

                with col3:

                    st.write(
                        "**Reason**"
                    )

                    st.write(
                        reason
                    )

                    st.caption(
                        f"Status: {status}"
                    )

    # ==========================================================
    # DOCTOR DASHBOARD
    # ==========================================================

    def show_doctor_dashboard(self):

        doctor_id, error = (
            self.get_doctor_id()
        )

        if error:

            st.error(
                "Unable to load doctor dashboard:"
            )

            st.warning(error)

            return

        appointments, error = (
            self.get_doctor_appointments(
                doctor_id
            )
        )

        if error:

            st.error(
                "Unable to load appointments:"
            )

            st.warning(error)

            return

        st.title(
            "Doctor Dashboard"
        )

        st.write(
            "Overview of your appointments and schedule."
        )

        st.divider()

        statistics = (
            self.get_statistics(
                appointments
            )
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Today's Appointments",
                statistics["today"]
            )

        with col2:

            st.metric(
                "This Month",
                statistics["month"]
            )

        with col3:

            st.metric(
                "Pending",
                statistics["pending"]
            )

        with col4:

            st.metric(
                "Completed",
                statistics["completed"]
            )

        st.divider()

        today = date.today()

        if "dashboard_calendar_year" not in st.session_state:

            st.session_state[
                "dashboard_calendar_year"
            ] = today.year

        if "dashboard_calendar_month" not in st.session_state:

            st.session_state[
                "dashboard_calendar_month"
            ] = today.month

        calendar_year = st.session_state[
            "dashboard_calendar_year"
        ]

        calendar_month = st.session_state[
            "dashboard_calendar_month"
        ]

        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )

        with col1:

            if st.button(
                "← Previous Month",
                use_container_width=True
            ):

                if calendar_month == 1:

                    st.session_state[
                        "dashboard_calendar_month"
                    ] = 12

                    st.session_state[
                        "dashboard_calendar_year"
                    ] -= 1

                else:

                    st.session_state[
                        "dashboard_calendar_month"
                    ] -= 1

                st.rerun()

        with col2:

            st.markdown(
                f"""
                <h3 style="text-align:center;">
                    {calendar.month_name[calendar_month]}
                    {calendar_year}
                </h3>
                """,
                unsafe_allow_html=True
            )

        with col3:

            if st.button(
                "Next Month →",
                use_container_width=True
            ):

                if calendar_month == 12:

                    st.session_state[
                        "dashboard_calendar_month"
                    ] = 1

                    st.session_state[
                        "dashboard_calendar_year"
                    ] += 1

                else:

                    st.session_state[
                        "dashboard_calendar_month"
                    ] += 1

                st.rerun()

        month_appointments, error = (
            self.get_month_appointments(
                doctor_id,
                calendar_year,
                calendar_month
            )
        )

        if error:

            st.error(
                "Unable to load monthly appointments:"
            )

            st.warning(error)

            return

        self.show_calendar(
            month_appointments,
            calendar_year,
            calendar_month
        )

        st.divider()

        self.show_appointment_list(
            appointments
        )

        st.divider()

        if st.button(
            "Refresh Dashboard",
            use_container_width=True
        ):

            st.rerun()

    # ==========================================================
    # GET LOGGED-IN PATIENT ID
    # ==========================================================

    def get_patient_id(self):

        try:

            user = self.get_current_user()

            if not user:

                return None, (
                    "No logged-in user was found."
                )

            profile_id = (
                user.get("profile_id")
                or user.get("id")
            )

            if not profile_id:

                return None, (
                    "Patient profile ID was not found."
                )

            response = (
                self.supabase
                .table("patients")
                .select("patient_id")
                .eq(
                    "profile_id",
                    profile_id
                )
                .limit(1)
                .execute()
            )

            data = response.data or []

            if not data:

                return None, (
                    "No patient record is linked to this account."
                )

            patient_id = data[0].get(
                "patient_id"
            )

            if not patient_id:

                return None, (
                    "Patient record exists but patient_id is missing."
                )

            return patient_id, None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # GET PATIENT APPOINTMENTS
    # ==========================================================

    def get_patient_appointments(
        self,
        patient_id
    ):

        try:

            response = (
                self.supabase
                .table("appointments")
                .select(
                    """
                    appointment_id,
                    patient_id,
                    doctor_id,
                    appointment_date,
                    status,
                    reason_for_visit,
                    doctors (
                        doctor_id,
                        profile_id,
                        specialization,
                        profiles (
                            first_name,
                            last_name
                        )
                    )
                    """
                )
                .eq(
                    "patient_id",
                    patient_id
                )
                .order(
                    "appointment_date",
                    desc=False
                )
                .execute()
            )

            return response.data or [], None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # PATIENT DASHBOARD
    # ==========================================================

    def show_patient_dashboard(self):

        st.title(
            "Hospital Management System"
        )

        st.write(
            "Welcome to the Hospital Management System."
        )

        st.divider()

        st.header("Dashboard")

        # ======================================================
        # GET PATIENT
        # ======================================================

        patient_id, error = (
            self.get_patient_id()
        )

        if error:

            st.error(
                "Unable to load patient dashboard."
            )

            st.warning(error)

            return

        # ======================================================
        # GET PATIENT APPOINTMENTS
        # ======================================================

        appointments, error = (
            self.get_patient_appointments(
                patient_id
            )
        )

        if error:

            st.error(
                "Unable to load appointments."
            )

            st.warning(error)

            return

        # ======================================================
        # CALCULATE APPOINTMENT STATISTICS
        # ======================================================

        today = date.today()

        upcoming_count = 0
        completed_count = 0
        pending_count = 0

        for appointment in appointments:

            appointment_date = (
                appointment.get(
                    "appointment_date"
                )
            )

            status = (
                str(
                    appointment.get(
                        "status",
                        ""
                    )
                )
                .lower()
                .strip()
            )

            if status == "completed":

                completed_count += 1

            if status == "pending":

                pending_count += 1

            if appointment_date:

                try:

                    appointment_datetime = (
                        datetime.fromisoformat(
                            appointment_date.replace(
                                "Z",
                                "+00:00"
                            )
                        )
                    )

                    if appointment_datetime.date() >= today:

                        upcoming_count += 1

                except Exception:

                    pass

        # ======================================================
        # DISPLAY STATISTICS
        # ======================================================

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Upcoming Appointments",
                upcoming_count
            )

        with col2:

            st.metric(
                "Pending",
                pending_count
            )

        with col3:

            st.metric(
                "Completed",
                completed_count
            )

        st.divider()

        # ======================================================
        # UPCOMING APPOINTMENTS
        # ======================================================

        st.subheader(
            "Upcoming Appointments"
        )

        upcoming_appointments = []

        for appointment in appointments:

            appointment_date = (
                appointment.get(
                    "appointment_date"
                )
            )

            if not appointment_date:

                continue

            try:

                appointment_datetime = (
                    datetime.fromisoformat(
                        appointment_date.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                if appointment_datetime.date() >= today:

                    upcoming_appointments.append(
                        appointment
                    )

            except Exception:

                continue

        if not upcoming_appointments:

            st.info(
                "You have no upcoming appointments."
            )

        else:

            for appointment in upcoming_appointments[:10]:

                (
                    formatted_date,
                    formatted_time
                ) = self.format_appointment_datetime(
                    appointment
                )

                status = (
                    appointment.get(
                        "status",
                        "Pending"
                    )
                )

                reason = (
                    appointment.get(
                        "reason_for_visit"
                    )
                    or
                    "No reason provided"
                )

                doctor_name = "Unknown Doctor"

                doctor = appointment.get(
                    "doctors"
                )

                if doctor:

                    doctor_profile = (
                        doctor.get(
                            "profiles"
                        )
                    )

                    if doctor_profile:

                        first_name = (
                            doctor_profile.get(
                                "first_name",
                                ""
                            )
                        )

                        last_name = (
                            doctor_profile.get(
                                "last_name",
                                ""
                            )
                        )

                        doctor_name = (
                            f"Dr. {first_name} {last_name}"
                        ).strip()

                with st.container(
                    border=True
                ):

                    col1, col2, col3 = st.columns(
                        [2, 2, 3]
                    )

                    with col1:

                        st.write(
                            f"**{formatted_date}**"
                        )

                        st.write(
                            f"🕐 {formatted_time}"
                        )

                    with col2:

                        st.write(
                            "**Doctor**"
                        )

                        st.write(
                            doctor_name
                        )

                        if doctor:

                            specialization = (
                                doctor.get(
                                    "specialization"
                                )
                            )

                            if specialization:

                                st.caption(
                                    specialization
                                )

                    with col3:

                        st.write(
                            "**Reason for Visit**"
                        )

                        st.write(
                            reason
                        )

                        st.caption(
                            f"Status: {status}"
                        )

        st.divider()

        # ======================================================
        # PATIENT INFORMATION
        # ======================================================

        st.subheader(
            "Quick Access"
        )

        st.write(
            "Use the sidebar to view your profile "
            "and manage your appointments."
        )

    # ==========================================================
    # MAIN SHOW METHOD
    # ==========================================================

    def show(self):

        role = self.get_role()

        # ======================================================
        # ADMIN
        # ======================================================

        if role == "admin":

            self.show_admin_dashboard()

            return

        # ======================================================
        # DOCTOR
        # ======================================================

        if role == "doctor":

            self.show_doctor_dashboard()

            return

        # ======================================================
        # PATIENT
        # ======================================================

        if role == "patient":

            self.show_patient_dashboard()

            return

        # ======================================================
        # INVALID ROLE
        # ======================================================

        st.error(
            "Invalid user role."
        )