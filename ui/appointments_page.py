import streamlit as st
from datetime import datetime

from models.appointment import Appointment
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

        role = st.session_state.get("role", "").lower()

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
        # SHOW ONLY AUTHORIZED APPOINTMENTS
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
                text-align:center;
                padding:20px 10px;
                font-size:20px;
                font-weight:500;
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
            st.session_state["appointment_notification"] = None
            st.rerun()

    def show_notification(self):

        message = st.session_state.get(
            "appointment_notification"
        )

        if message:
            self.notification_modal(message)

    # ==========================================================
    # GET CURRENT USER'S DATABASE ID
    # ==========================================================

    def get_current_role_record(self):

        role = st.session_state.get("role", "").lower()
        user = st.session_state.get("user", {})

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

            response = (
                self.supabase
                .table("doctors")
                .select("doctor_id")
                .eq("profile_id", profile_id)
                .single()
                .execute()
            )

            if response.data:
                return "doctor", response.data["doctor_id"]

        # ------------------------------------------------------
        # PATIENT
        # ------------------------------------------------------

        if role == "patient":

            response = (
                self.supabase
                .table("patients")
                .select("patient_id")
                .eq("profile_id", profile_id)
                .single()
                .execute()
            )

            if response.data:
                return "patient", response.data["patient_id"]

        return role, None

    # ==========================================================
    # GET AUTHORIZED APPOINTMENTS
    # ==========================================================

    def get_authorized_appointments(self):

        role, record_id = self.get_current_role_record()

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
                    .order("appointment_date", desc=True)
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
                    .eq("doctor_id", record_id)
                    .order("appointment_date", desc=True)
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
                    .eq("patient_id", record_id)
                    .order("appointment_date", desc=True)
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
        # HEADER
        # ------------------------------------------------------

        if role == "doctor":

            st.info(
                "You are viewing only your appointments."
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

            appointment_date = (
                appointment.get(
                    "appointment_date",
                    "N/A"
                )
            )

            status = (
                appointment.get(
                    "status",
                    "N/A"
                )
            )

            reason = (
                appointment.get(
                    "reason_for_visit",
                    "N/A"
                )
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
                        f"{patient_name}"
                    )

                st.write(
                    f"**Doctor:** {doctor_name}"
                )

                st.write(
                    f"**Patient:** {patient_name}"
                )

                st.write(
                    f"**Appointment:** {appointment_date}"
                )

                st.write(
                    f"**Status:** {str(status).capitalize()}"
                )

                st.write(
                    f"**Reason:** {reason}"
                )

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
                # ADMIN ONLY EDIT
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

            st.write(
                f"**Date:** "
                f"{appointment.get('appointment_date', 'N/A')}"
            )

        with col2:

            st.write(
                f"**Status:** "
                f"{str(appointment.get('status', 'N/A')).capitalize()}"
            )

            st.write(
                f"**Reason:** "
                f"{appointment.get('reason_for_visit', 'N/A')}"
            )

        st.divider()

        # ------------------------------------------------------
        # DIAGNOSES
        # ------------------------------------------------------

        st.subheader("Medical Record")

        diagnoses, error = (
            self.get_diagnoses_for_appointment(
                appointment["appointment_id"]
            )
        )

        if error:

            st.error(
                f"Unable to load diagnosis:\n\n{error}"
            )

        elif diagnoses:

            for diagnosis in diagnoses:

                st.markdown(
                    f"""
                    **Diagnosis:**  
                    {diagnosis.get(
                        'diagnosis_description',
                        'N/A'
                    )}

                    **Treatment Plan:**  
                    {diagnosis.get(
                        'treatment_plan',
                        'N/A'
                    )}

                    **Recorded:**  
                    {diagnosis.get(
                        'created_at',
                        'N/A'
                    )}
                    """
                )

                st.divider()

        else:

            st.info(
                "No diagnosis has been recorded."
            )

        # ------------------------------------------------------
        # DOCTOR CAN ADD DIAGNOSIS
        # ------------------------------------------------------

        if role == "doctor":

            st.subheader("Add Diagnosis")

            with st.form(
                f"diagnosis_form_"
                f"{appointment['appointment_id']}"
            ):

                diagnosis_description = st.text_area(
                    "Diagnosis",
                    placeholder="Enter the patient's diagnosis..."
                )

                treatment_plan = st.text_area(
                    "Treatment Plan",
                    placeholder="Enter the treatment plan..."
                )

                submitted = st.form_submit_button(
                    "Save Diagnosis",
                    type="primary",
                    use_container_width=True
                )

            if submitted:

                if not diagnosis_description.strip():

                    st.error(
                        "Diagnosis is required."
                    )

                    return

                from models.diagnosis import Diagnosis

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

        patients, patient_error = (
            self.patient_service.get_all()
        )

        doctors, doctor_error = (
            self.doctor_service.get_all()
        )

        if patient_error:

            st.error(
                f"Unable to load patients:\n\n{patient_error}"
            )

            return

        if doctor_error:

            st.error(
                f"Unable to load doctors:\n\n{doctor_error}"
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

            patient_options[name] = (
                patient["patient_id"]
            )

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

            specialization = (
                doctor.get("specialization")
            )

            if specialization:

                name = (
                    f"{name} - "
                    f"{specialization}"
                )

            doctor_options[name] = (
                doctor["doctor_id"]
            )

        with st.form(
            "appointment_add_form",
            clear_on_submit=True
        ):

            patient_name = st.selectbox(
                "Patient",
                list(patient_options.keys())
            )

            doctor_name = st.selectbox(
                "Doctor",
                list(doctor_options.keys())
            )

            appointment_date = st.date_input(
                "Appointment Date"
            )

            appointment_time = st.time_input(
                "Appointment Time"
            )

            status = st.selectbox(
                "Status",
                [
                    "scheduled",
                    "completed",
                    "cancelled"
                ]
            )

            reason = st.text_area(
                "Reason for Visit"
            )

            submitted = st.form_submit_button(
                "Create Appointment",
                type="primary",
                use_container_width=True
            )

        if not submitted:
            return

        if not reason.strip():

            st.error(
                "Reason for visit is required."
            )

            return

        appointment_datetime = datetime.combine(
            appointment_date,
            appointment_time
        )

        appointment = Appointment(
            patient_id=patient_options[
                patient_name
            ],
            doctor_id=doctor_options[
                doctor_name
            ],
            appointment_date=appointment_datetime,
            status=status,
            reason_for_visit=reason.strip()
        )

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

        with st.form(
            f"edit_appointment_form_"
            f"{appointment['appointment_id']}"
        ):

            statuses = [
                "scheduled",
                "completed",
                "cancelled"
            ]

            current_status = (
                appointment.get(
                    "status"
                )
            )

            status_index = (
                statuses.index(current_status)
                if current_status in statuses
                else 0
            )

            status = st.selectbox(
                "Status",
                statuses,
                index=status_index
            )

            reason = st.text_area(
                "Reason for Visit",
                value=(
                    appointment.get(
                        "reason_for_visit",
                        ""
                    ) or ""
                )
            )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
                use_container_width=True
            )

        if not submitted:
            return

        if not reason.strip():

            st.error(
                "Reason for visit is required."
            )

            return

        data = {
            "status": status,
            "reason_for_visit": reason.strip()
        }

        updated, error = (
            self.appointment_service.update(
                appointment["appointment_id"],
                data
            )
        )

        if error:

            st.error(
                f"Unable to update appointment:\n\n{error}"
            )

            return

        st.session_state[
            "appointment_notification"
        ] = (
            "Appointment has been updated successfully."
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

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Cancel",
                use_container_width=True
            ):

                st.rerun()

        with col2:

            if st.button(
                "Delete Appointment",
                type="primary",
                use_container_width=True
            ):

                success, error = (
                    self.appointment_service.delete(
                        appointment[
                            "appointment_id"
                        ]
                    )
                )

                if error:

                    st.error(
                        f"Unable to delete appointment:\n\n{error}"
                    )

                    return

                st.session_state[
                    "appointment_notification"
                ] = (
                    "Appointment has been deleted successfully."
                )

                st.rerun()