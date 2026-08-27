import streamlit as st

from datetime import datetime, date, time

from models.appointment import Appointment
from models.diagnosis import Diagnosis

from services.appointment_service import AppointmentService
from services.patient_service import PatientService
from services.doctor_service import DoctorService
from services.diagnosis_service import DiagnosisService


class AppointmentsPage:

    def __init__(self):
        self.appointment_service = AppointmentService()
        self.patient_service = PatientService()
        self.doctor_service = DoctorService()
        self.diagnosis_service = DiagnosisService()
        self.supabase = self.appointment_service.supabase

    # ==========================================================
    # MAIN
    # ==========================================================

    def show(self):

        role = st.session_state.get(
            "role",
            ""
        ).lower()

        st.title("Appointments")

        self.show_notification()

        # ------------------------------------------------------
        # ADMIN ONLY
        # ------------------------------------------------------

        if role == "admin":

            if st.button(
                "Add Appointment",
                type="primary",
                key="add_appointment_button"
            ):
                self.add_appointment_modal()

            st.divider()

        # ------------------------------------------------------
        # SHOW AUTHORIZED APPOINTMENTS
        # ------------------------------------------------------

        self.show_appointments()

    # ==========================================================
    # NOTIFICATION
    # ==========================================================

    @st.dialog("Success")
    def notification_modal(self, message):

        st.markdown(
            f"""
            <div style="
                text-align: center;
                padding: 20px 10px;
                font-size: 20px;
                font-weight: 500;
            ">
                {message}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key="appointment_notification_ok"
        ):

            st.session_state[
                "appointment_notification"
            ] = None

            st.rerun()

    def show_notification(self):

        message = st.session_state.get(
            "appointment_notification"
        )

        if message:
            self.notification_modal(message)

    # ==========================================================
    # DATETIME HELPERS
    # ==========================================================

    def get_time_options(self):

        time_options = []

        for hour in range(0, 24):

            for minute in (0, 30):

                time_options.append(
                    time(
                        hour,
                        minute
                    )
                )

        return time_options

    def parse_appointment_datetime(self, value):

        if not value:
            return None

        try:

            if isinstance(value, datetime):
                return value

            value = str(value)

            # Handle Z timezone
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"

            return datetime.fromisoformat(value)

        except Exception:
            return None

    def format_appointment_datetime(self, value):

        dt = self.parse_appointment_datetime(value)

        if not dt:
            return str(value or "N/A")

        return dt.strftime(
            "%B %d, %Y at %I:%M %p"
        )

    # ==========================================================
    # CHECK DOCTOR SLOT
    # ==========================================================

    def doctor_slot_exists(
        self,
        doctor_id,
        appointment_datetime,
        exclude_appointment_id=None
    ):

        try:

            response = (
                self.supabase
                .table("appointments")
                .select(
                    "appointment_id, appointment_date"
                )
                .eq(
                    "doctor_id",
                    doctor_id
                )
                .eq(
                    "appointment_date",
                    appointment_datetime.isoformat()
                )
                .execute()
            )

            for appointment in response.data or []:

                existing_id = appointment.get(
                    "appointment_id"
                )

                # Ignore current appointment during editing
                if (
                    exclude_appointment_id
                    and str(existing_id)
                    == str(exclude_appointment_id)
                ):
                    continue

                return True, None

            return False, None

        except Exception as e:

            return False, str(e)

    # ==========================================================
    # GET CURRENT USER'S DATABASE ID
    # ==========================================================

    def get_current_role_record(self):

        role = st.session_state.get(
            "role",
            ""
        ).lower()

        user = st.session_state.get(
            "user",
            {}
        )

        profile_id = (
            user.get("profile_id")
            or user.get("id")
        )

        if not profile_id:
            return None, None

        # ------------------------------------------------------
        # DOCTOR
        # ------------------------------------------------------

        if role == "doctor":

            try:

                response = (
                    self.supabase
                    .table("doctors")
                    .select("doctor_id")
                    .eq(
                        "profile_id",
                        profile_id
                    )
                    .single()
                    .execute()
                )

                if response.data:

                    return (
                        "doctor",
                        response.data["doctor_id"]
                    )

            except Exception:

                return "doctor", None

        # ------------------------------------------------------
        # PATIENT
        # ------------------------------------------------------

        if role == "patient":

            try:

                response = (
                    self.supabase
                    .table("patients")
                    .select("patient_id")
                    .eq(
                        "profile_id",
                        profile_id
                    )
                    .single()
                    .execute()
                )

                if response.data:

                    return (
                        "patient",
                        response.data["patient_id"]
                    )

            except Exception:

                return "patient", None

        return role, None

    # ==========================================================
    # GET AUTHORIZED APPOINTMENTS
    # ==========================================================

    def get_authorized_appointments(self):

        role, record_id = (
            self.get_current_role_record()
        )

        try:

            query = (
                self.supabase
                .table("appointments")
                .select(
                    """
                    *,
                    patients (
                        patient_id,
                        profile_id,
                        profiles (
                            id,
                            first_name,
                            last_name,
                            email
                        )
                    ),
                    doctors (
                        doctor_id,
                        profile_id,
                        specialization,
                        profiles (
                            id,
                            first_name,
                            last_name,
                            email
                        )
                    )
                    """
                )
            )

            # --------------------------------------------------
            # ADMIN
            # --------------------------------------------------

            if role == "admin":

                response = (
                    query
                    .order(
                        "appointment_date",
                        desc=True
                    )
                    .execute()
                )

            # --------------------------------------------------
            # DOCTOR
            # --------------------------------------------------

            elif role == "doctor":

                if not record_id:
                    return None, "Doctor record not found."

                response = (
                    query
                    .eq(
                        "doctor_id",
                        record_id
                    )
                    .order(
                        "appointment_date",
                        desc=True
                    )
                    .execute()
                )

            # --------------------------------------------------
            # PATIENT
            # --------------------------------------------------

            elif role == "patient":

                if not record_id:
                    return None, "Patient record not found."

                response = (
                    query
                    .eq(
                        "patient_id",
                        record_id
                    )
                    .order(
                        "appointment_date",
                        desc=True
                    )
                    .execute()
                )

            else:

                return None, "Invalid user role."

            return response.data, None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # SHOW APPOINTMENTS
    # ==========================================================

    def show_appointments(self):

        appointments, error = (
            self.get_authorized_appointments()
        )

        if error:

            st.error(
                f"Unable to load appointments:\n\n{error}"
            )

            return

        if not appointments:

            st.info(
                "No appointments found."
            )

            return

        role = st.session_state.get(
            "role",
            ""
        ).lower()

        # ------------------------------------------------------
        # INFORMATION
        # ------------------------------------------------------

        if role == "doctor":

            st.info(
                "You are viewing only your appointments. "
                "You can update the status of your appointments."
            )

        elif role == "patient":

            st.info(
                "You are viewing only your appointments."
            )

        # ------------------------------------------------------
        # DISPLAY
        # ------------------------------------------------------

        for appointment in appointments:

            patient = (
                appointment.get("patients")
                or {}
            )

            patient_profile = (
                patient.get("profiles")
                or {}
            )

            doctor = (
                appointment.get("doctors")
                or {}
            )

            doctor_profile = (
                doctor.get("profiles")
                or {}
            )

            patient_name = (
                f"{patient_profile.get('first_name', '')} "
                f"{patient_profile.get('last_name', '')}"
            ).strip()

            doctor_name = (
                f"{doctor_profile.get('first_name', '')} "
                f"{doctor_profile.get('last_name', '')}"
            ).strip()

            if not patient_name:
                patient_name = "Unknown Patient"

            if not doctor_name:
                doctor_name = "Unknown Doctor"

            appointment_date = appointment.get(
                "appointment_date"
            )

            formatted_datetime = (
                self.format_appointment_datetime(
                    appointment_date
                )
            )

            status = appointment.get(
                "status",
                "N/A"
            )

            reason = appointment.get(
                "reason_for_visit",
                "N/A"
            )

            # --------------------------------------------------
            # CARD
            # --------------------------------------------------

            col1, col2 = st.columns([7, 2])

            with col1:

                if role == "patient":

                    st.subheader(
                        f"Dr. {doctor_name}"
                    )

                else:

                    st.subheader(
                        patient_name
                    )

                st.write(
                    f"**Doctor:** {doctor_name}"
                )

                st.write(
                    f"**Patient:** {patient_name}"
                )

                st.write(
                    f"**Appointment:** {formatted_datetime}"
                )

                st.write(
                    f"**Status:** "
                    f"{str(status).capitalize()}"
                )

                st.write(
                    f"**Reason:** {reason}"
                )

            # --------------------------------------------------
            # ACTION BUTTONS
            # --------------------------------------------------

            with col2:

                st.write("")

                # ----------------------------------------------
                # OPEN
                # ----------------------------------------------

                if st.button(
                    "Open",
                    key=(
                        f"open_appointment_"
                        f"{appointment['appointment_id']}"
                    ),
                    use_container_width=True
                ):

                    self.open_appointment_modal(
                        appointment
                    )

                # ----------------------------------------------
                # ADMIN EDIT / DELETE
                # ----------------------------------------------

                if role == "admin":

                    if st.button(
                        "Edit",
                        key=(
                            f"edit_appointment_"
                            f"{appointment['appointment_id']}"
                        ),
                        use_container_width=True
                    ):

                        self.edit_appointment_modal(
                            appointment
                        )

                    if st.button(
                        "Delete",
                        key=(
                            f"delete_appointment_"
                            f"{appointment['appointment_id']}"
                        ),
                        use_container_width=True
                    ):

                        self.delete_appointment_modal(
                            appointment
                        )

            st.divider()

    # ==========================================================
    # OPEN APPOINTMENT
    # ==========================================================

    @st.dialog(
        "Appointment Details",
        width="large"
    )
    def open_appointment_modal(
        self,
        appointment
    ):

        role = st.session_state.get(
            "role",
            ""
        ).lower()

        patient = (
            appointment.get("patients")
            or {}
        )

        patient_profile = (
            patient.get("profiles")
            or {}
        )

        doctor = (
            appointment.get("doctors")
            or {}
        )

        doctor_profile = (
            doctor.get("profiles")
            or {}
        )

        patient_name = (
            f"{patient_profile.get('first_name', '')} "
            f"{patient_profile.get('last_name', '')}"
        ).strip()

        doctor_name = (
            f"{doctor_profile.get('first_name', '')} "
            f"{doctor_profile.get('last_name', '')}"
        ).strip()

        if not patient_name:
            patient_name = "Unknown Patient"

        if not doctor_name:
            doctor_name = "Unknown Doctor"

        # ------------------------------------------------------
        # TITLE
        # ------------------------------------------------------

        if role == "patient":

            st.subheader(
                f"Appointment with Dr. {doctor_name}"
            )

        else:

            st.subheader(
                f"Appointment — {patient_name}"
            )

        # ------------------------------------------------------
        # INFORMATION
        # ------------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Doctor:** {doctor_name}"
            )

            st.write(
                f"**Patient:** {patient_name}"
            )

            appointment_datetime = (
                self.format_appointment_datetime(
                    appointment.get("appointment_date")
                )
            )

            st.write(
                f"**Date & Time:** {appointment_datetime}"
            )

        with col2:

            appointment_status = str(
                appointment.get(
                    "status",
                    "N/A"
                )
            ).capitalize()

            st.write(
                f"**Status:** {appointment_status}"
            )

            reason = appointment.get(
                "reason_for_visit",
                "N/A"
            )

            st.write(
                f"**Reason:** {reason}"
            )

        st.divider()

        # ======================================================
        # DOCTOR CAN UPDATE APPOINTMENT STATUS
        # ======================================================

        if role == "doctor":

            st.subheader(
                "Update Appointment Status"
            )

            statuses = [
                "scheduled",
                "completed",
                "cancelled"
            ]

            current_status = appointment.get(
                "status",
                "scheduled"
            )

            if current_status not in statuses:
                current_status = "scheduled"

            current_status_index = (
                statuses.index(current_status)
            )

            with st.form(
                f"doctor_status_form_"
                f"{appointment['appointment_id']}"
            ):

                new_status = st.selectbox(
                    "Appointment Status",
                    statuses,
                    index=current_status_index,
                    format_func=lambda status:
                        status.capitalize()
                )

                status_submitted = (
                    st.form_submit_button(
                        "Update Status",
                        type="primary",
                        use_container_width=True
                    )
                )

            if status_submitted:

                # ----------------------------------------------
                # UPDATE ONLY STATUS
                # ----------------------------------------------

                updated, error = (
                    self.appointment_service.update(
                        appointment[
                            "appointment_id"
                        ],
                        {
                            "status": new_status
                        }
                    )
                )

                if error:

                    st.error(
                        "Unable to update appointment "
                        f"status:\n\n{error}"
                    )

                    return

                # ----------------------------------------------
                # SUCCESS
                # ----------------------------------------------

                st.session_state[
                    "appointment_notification"
                ] = (
                    f"Appointment status for "
                    f"<strong>{patient_name}</strong> "
                    f"has been changed to "
                    f"<strong>{new_status.capitalize()}</strong> "
                    f"successfully."
                )

                st.rerun()

            st.divider()

        # ======================================================
        # DIAGNOSES
        # ======================================================

        st.subheader(
            "Medical Record"
        )

        diagnoses, error = (
            self.get_diagnoses_for_appointment(
                appointment[
                    "appointment_id"
                ]
            )
        )

        if error:

            st.error(
                f"Unable to load diagnosis:\n\n{error}"
            )

        elif diagnoses:

            for diagnosis in diagnoses:

                diagnosis_description = (
                    diagnosis.get(
                        "diagnosis_description",
                        "N/A"
                    )
                )

                treatment_plan = (
                    diagnosis.get(
                        "treatment_plan",
                        "N/A"
                    )
                )

                recorded = (
                    self.format_appointment_datetime(
                        diagnosis.get("created_at")
                    )
                )

                st.markdown(
                    f"""
                    **Diagnosis:**  

                    {diagnosis_description}

                    **Treatment Plan:**  

                    {treatment_plan}

                    **Recorded:**  

                    {recorded}
                    """
                )

                st.divider()

        else:

            st.info(
                "No diagnosis has been recorded."
            )

        # ======================================================
        # DOCTOR CAN ADD DIAGNOSIS
        # ======================================================

        if role == "doctor":

            st.subheader(
                "Add Diagnosis"
            )

            with st.form(
                f"diagnosis_form_"
                f"{appointment['appointment_id']}"
            ):

                diagnosis_description = st.text_area(
                    "Diagnosis",
                    placeholder=(
                        "Enter the patient's diagnosis..."
                    )
                )

                treatment_plan = st.text_area(
                    "Treatment Plan",
                    placeholder=(
                        "Enter the treatment plan..."
                    )
                )

                submitted = (
                    st.form_submit_button(
                        "Save Diagnosis",
                        type="primary",
                        use_container_width=True
                    )
                )

            if submitted:

                if not diagnosis_description.strip():

                    st.error(
                        "Diagnosis is required."
                    )

                    return

                diagnosis = Diagnosis(
                    appointment_id=(
                        appointment["appointment_id"]
                    ),
                    diagnosis_description=(
                        diagnosis_description.strip()
                    ),
                    treatment_plan=(
                        treatment_plan.strip()
                    )
                )

                created, error = (
                    self.diagnosis_service.create(
                        diagnosis
                    )
                )

                if error:

                    st.error(
                        f"Unable to add diagnosis:\n\n{error}"
                    )

                    return

                st.session_state[
                    "appointment_notification"
                ] = (
                    f"Diagnosis for "
                    f"<strong>{patient_name}</strong> "
                    f"has been added successfully."
                )

                st.rerun()

    # ==========================================================
    # GET DIAGNOSES
    # ==========================================================

    def get_diagnoses_for_appointment(
        self,
        appointment_id
    ):

        try:

            response = (
                self.supabase
                .table("diagnoses")
                .select("*")
                .eq(
                    "appointment_id",
                    appointment_id
                )
                .order(
                    "created_at",
                    desc=True
                )
                .execute()
            )

            return response.data, None

        except Exception as e:

            return None, str(e)

    # ==========================================================
    # ADMIN ADD APPOINTMENT
    # ==========================================================

    @st.dialog("Add Appointment")
    def add_appointment_modal(self):

        st.subheader(
            "Create New Appointment"
        )

        # ------------------------------------------------------
        # LOAD PATIENTS
        # ------------------------------------------------------

        patients, patient_error = (
            self.patient_service.get_all()
        )

        # ------------------------------------------------------
        # LOAD DOCTORS
        # ------------------------------------------------------

        doctors, doctor_error = (
            self.doctor_service.get_all()
        )

        if patient_error:

            st.error(
                f"Unable to load patients:\n\n"
                f"{patient_error}"
            )

            return

        if doctor_error:

            st.error(
                f"Unable to load doctors:\n\n"
                f"{doctor_error}"
            )

            return

        if not patients:

            st.warning(
                "No patients available."
            )

            return

        if not doctors:

            st.warning(
                "No doctors available."
            )

            return

        # ------------------------------------------------------
        # PATIENT OPTIONS
        # ------------------------------------------------------

        patient_options = {}

        for patient in patients:

            profile = (
                patient.get("profiles")
                or {}
            )

            name = (
                f"{profile.get('first_name', '')} "
                f"{profile.get('last_name', '')}"
            ).strip()

            if not name:
                name = "Unknown Patient"

            patient_options[name] = (
                patient["patient_id"]
            )

        # ------------------------------------------------------
        # DOCTOR OPTIONS
        # ------------------------------------------------------

        doctor_options = {}

        for doctor in doctors:

            profile = (
                doctor.get("profiles")
                or {}
            )

            name = (
                f"{profile.get('first_name', '')} "
                f"{profile.get('last_name', '')}"
            ).strip()

            if not name:
                name = "Unknown Doctor"

            specialization = doctor.get(
                "specialization"
            )

            if specialization:

                name = (
                    f"{name} - "
                    f"{specialization}"
                )

            doctor_options[name] = (
                doctor["doctor_id"]
            )

        # ======================================================
        # FORM
        # ======================================================

        with st.form(
            "appointment_add_form"
        ):

            patient_name = st.selectbox(
                "Patient",
                list(
                    patient_options.keys()
                )
            )

            doctor_name = st.selectbox(
                "Doctor",
                list(
                    doctor_options.keys()
                )
            )

            # --------------------------------------------------
            # DATE
            # --------------------------------------------------

            appointment_date = st.date_input(
                "Appointment Date",
                min_value=date.today(),
                value=date.today()
            )

            # --------------------------------------------------
            # TIME
            # --------------------------------------------------

            time_options = (
                self.get_time_options()
            )

            appointment_time = st.selectbox(
                "Appointment Time",
                time_options,
                format_func=lambda t:
                    t.strftime("%I:%M %p")
            )

            # --------------------------------------------------
            # STATUS
            # --------------------------------------------------

            status = st.selectbox(
                "Status",
                [
                    "scheduled",
                    "completed",
                    "cancelled"
                ]
            )

            # --------------------------------------------------
            # REASON
            # --------------------------------------------------

            reason = st.text_area(
                "Reason for Visit"
            )

            submitted = st.form_submit_button(
                "Create Appointment",
                type="primary",
                use_container_width=True
            )

        # ======================================================
        # NOT SUBMITTED
        # ======================================================

        if not submitted:
            return

        # ======================================================
        # REASON VALIDATION
        # ======================================================

        if not reason.strip():

            st.error(
                "Reason for visit is required."
            )

            return

        # ======================================================
        # DATE VALIDATION
        # ======================================================

        today = date.today()

        if appointment_date < today:

            st.error(
                "Appointment date cannot be in the past."
            )

            return

        # ======================================================
        # COMBINE DATE + TIME
        # ======================================================

        appointment_datetime = datetime.combine(
            appointment_date,
            appointment_time
        )

        # ======================================================
        # TODAY TIME VALIDATION
        # ======================================================

        if (
            appointment_date == today
            and appointment_datetime <= datetime.now()
        ):

            st.error(
                "Appointment time must be in the future."
            )

            return

        # ======================================================
        # DOCTOR SLOT CHECK
        # ======================================================

        selected_doctor_id = (
            doctor_options[doctor_name]
        )

        slot_taken, slot_error = (
            self.doctor_slot_exists(
                selected_doctor_id,
                appointment_datetime
            )
        )

        if slot_error:

            st.error(
                "Unable to check appointment availability:\n\n"
                f"{slot_error}"
            )

            return

        # ======================================================
        # DUPLICATE
        # ======================================================

        if slot_taken:

            st.error(
                "This appointment slot is already taken "
                "for this doctor. Please select another time."
            )

            return

        # ======================================================
        # CREATE APPOINTMENT
        # ======================================================

        appointment = Appointment(
            patient_id=(
                patient_options[patient_name]
            ),
            doctor_id=(
                doctor_options[doctor_name]
            ),
            appointment_date=(
                appointment_datetime
            ),
            status=status,
            reason_for_visit=(
                reason.strip()
            )
        )

        # ======================================================
        # DATABASE
        # ======================================================

        created, error = (
            self.appointment_service.create(
                appointment
            )
        )

        if error:

            st.error(
                f"Unable to add appointment:\n\n{error}"
            )

            return

        # ======================================================
        # SUCCESS
        # ======================================================

        st.session_state[
            "appointment_notification"
        ] = (
            f"Appointment for "
            f"<strong>{patient_name}</strong> "
            f"has been added successfully."
        )

        st.rerun()

    # ==========================================================
    # ADMIN EDIT
    # ==========================================================

    @st.dialog("Edit Appointment")
    def edit_appointment_modal(
        self,
        appointment
    ):

        appointment_id = (
            appointment["appointment_id"]
        )

        # ------------------------------------------------------
        # CURRENT DATE/TIME
        # ------------------------------------------------------

        current_datetime = (
            self.parse_appointment_datetime(
                appointment.get(
                    "appointment_date"
                )
            )
        )

        if current_datetime:

            current_date = (
                current_datetime.date()
            )

            current_time = (
                current_datetime.time()
            )

            # Normalize seconds/microseconds

            current_time = time(
                current_time.hour,
                current_time.minute
            )

        else:

            current_date = date.today()
            current_time = time(8, 0)

        # ------------------------------------------------------
        # TIME OPTIONS
        # ------------------------------------------------------

        time_options = (
            self.get_time_options()
        )

        if current_time not in time_options:

            current_time = time(
                current_time.hour,
                30 if current_time.minute >= 30 else 0
            )

        # ------------------------------------------------------
        # STATUS
        # ------------------------------------------------------

        statuses = [
            "scheduled",
            "completed",
            "cancelled"
        ]

        current_status = (
            appointment.get("status")
        )

        status_index = (
            statuses.index(current_status)
            if current_status in statuses
            else 0
        )

        # ======================================================
        # PATIENT / DOCTOR
        # ======================================================

        patient = (
            appointment.get("patients")
            or {}
        )

        patient_profile = (
            patient.get("profiles")
            or {}
        )

        patient_name = (
            f"{patient_profile.get('first_name', '')} "
            f"{patient_profile.get('last_name', '')}"
        ).strip()

        doctor = (
            appointment.get("doctors")
            or {}
        )

        doctor_profile = (
            doctor.get("profiles")
            or {}
        )

        doctor_name = (
            f"{doctor_profile.get('first_name', '')} "
            f"{doctor_profile.get('last_name', '')}"
        ).strip()

        if not patient_name:
            patient_name = "Unknown Patient"

        if not doctor_name:
            doctor_name = "Unknown Doctor"

        # ======================================================
        # FORM
        # ======================================================

        with st.form(
            f"edit_appointment_form_{appointment_id}"
        ):

            st.subheader(
                "Appointment Information"
            )

            # --------------------------------------------------
            # CURRENT PATIENT / DOCTOR
            # --------------------------------------------------

            st.write(
                f"**Patient:** {patient_name}"
            )

            st.write(
                f"**Doctor:** {doctor_name}"
            )

            st.divider()

            # --------------------------------------------------
            # DATE
            # --------------------------------------------------

            today = date.today()

            # Allow existing past date to display

            edit_min_date = min(
                current_date,
                today
            )

            appointment_date = st.date_input(
                "Appointment Date",
                value=current_date,
                min_value=edit_min_date,
                key=f"edit_date_{appointment_id}"
            )

            # --------------------------------------------------
            # TIME
            # --------------------------------------------------

            current_time_index = (
                time_options.index(
                    current_time
                )
            )

            appointment_time = st.selectbox(
                "Appointment Time",
                time_options,
                index=current_time_index,
                format_func=lambda t:
                    t.strftime("%I:%M %p"),
                key=f"edit_time_{appointment_id}"
            )

            # --------------------------------------------------
            # STATUS
            # --------------------------------------------------

            status = st.selectbox(
                "Status",
                statuses,
                index=status_index,
                key=f"edit_status_{appointment_id}"
            )

            # --------------------------------------------------
            # REASON
            # --------------------------------------------------

            reason = st.text_area(
                "Reason for Visit",
                value=(
                    appointment.get(
                        "reason_for_visit",
                        ""
                    ) or ""
                ),
                key=f"edit_reason_{appointment_id}"
            )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
                use_container_width=True
            )

        # ======================================================
        # NOT SUBMITTED
        # ======================================================

        if not submitted:
            return

        # ======================================================
        # REASON VALIDATION
        # ======================================================

        if not reason.strip():

            st.error(
                "Reason for visit is required."
            )

            return

        # ======================================================
        # DATE VALIDATION
        # ======================================================

        today = date.today()

        if appointment_date < today:

            st.error(
                "Appointment date cannot be in the past."
            )

            return

        # ======================================================
        # COMBINE DATE + TIME
        # ======================================================

        new_datetime = datetime.combine(
            appointment_date,
            appointment_time
        )

        # ======================================================
        # TODAY TIME VALIDATION
        # ======================================================

        if (
            appointment_date == today
            and new_datetime <= datetime.now()
        ):

            st.error(
                "Appointment time must be in the future."
            )

            return

        # ======================================================
        # GET DOCTOR ID
        # ======================================================

        doctor_id = doctor.get(
            "doctor_id"
        )

        if not doctor_id:

            st.error(
                "Unable to identify the doctor "
                "for this appointment."
            )

            return

        # ======================================================
        # DUPLICATE DOCTOR SLOT CHECK
        # ======================================================

        slot_taken, slot_error = (
            self.doctor_slot_exists(
                doctor_id,
                new_datetime,
                exclude_appointment_id=appointment_id
            )
        )

        if slot_error:

            st.error(
                "Unable to check appointment availability:\n\n"
                f"{slot_error}"
            )

            return

        if slot_taken:

            st.error(
                "This appointment slot is already taken "
                "for this doctor. Please select another date "
                "or time."
            )

            return

        # ======================================================
        # UPDATE DATA
        # ======================================================

        data = {
            "appointment_date": new_datetime,
            "status": status,
            "reason_for_visit": reason.strip()
        }

        # ======================================================
        # UPDATE
        # ======================================================

        updated, error = (
            self.appointment_service.update(
                appointment_id,
                data
            )
        )

        if error:

            st.error(
                f"Unable to update appointment:\n\n{error}"
            )

            return

        # ======================================================
        # SUCCESS
        # ======================================================

        st.session_state[
            "appointment_notification"
        ] = (
            "Appointment date, time, and details "
            "have been updated successfully."
        )

        st.rerun()

    # ==========================================================
    # ADMIN DELETE
    # ==========================================================

    @st.dialog("Delete Appointment")
    def delete_appointment_modal(
        self,
        appointment
    ):

        st.warning(
            "Are you sure you want to delete this appointment?"
        )

        st.write(
            "This action cannot be undone."
        )

        st.divider()

        col1, col2 = st.columns(2)

        # ======================================================
        # CANCEL
        # ======================================================

        with col1:

            if st.button(
                "Cancel",
                key=(
                    f"cancel_delete_"
                    f"{appointment['appointment_id']}"
                ),
                use_container_width=True
            ):

                st.rerun()

        # ======================================================
        # DELETE
        # ======================================================

        with col2:

            if st.button(
                "Delete Appointment",
                key=(
                    f"confirm_delete_"
                    f"{appointment['appointment_id']}"
                ),
                type="primary",
                use_container_width=True
            ):

                success, error = (
                    self.appointment_service.delete(
                        appointment["appointment_id"]
                    )
                )

                # ------------------------------------------------
                # ERROR
                # ------------------------------------------------

                if error:

                    st.error(
                        f"Unable to delete appointment:\n\n"
                        f"{error}"
                    )

                    return

                # ------------------------------------------------
                # SUCCESS
                # ------------------------------------------------

                st.session_state[
                    "appointment_notification"
                ] = (
                    "Appointment has been deleted successfully."
                )

                st.rerun()