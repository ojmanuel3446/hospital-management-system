import streamlit as st
import datetime

from models.diagnosis import Diagnosis
from services.diagnosis_service import DiagnosisService
from services.appointment_service import AppointmentService


class DiagnosesPage:

    def __init__(self):
        self.service = DiagnosisService()
        self.appointment_service = AppointmentService()

    # ======================================================
    # GET LOGGED-IN USER
    # ======================================================

    def get_current_user(self):
        """
        Get the logged-in profile from Streamlit session state.

        AuthService.login() returns the complete profile row.
        """

        user = st.session_state.get("user")

        if not user:
            user = st.session_state.get("profile")

        return user

    # ======================================================
    # GET ROLE
    # ======================================================

    def get_role(self):

        user = self.get_current_user()

        if not user:
            return None

        return (user.get("role") or "").lower()

    # ======================================================
    # MAIN PAGE
    # ======================================================

    def show(self):

        st.title("Diagnoses")

        # ==================================================
        # CHECK LOGIN
        # ==================================================

        user = self.get_current_user()

        if not user:
            st.error("User session not found.")
            return

        role = self.get_role()

        # ==================================================
        # SUCCESS NOTIFICATION
        # ==================================================

        self.show_notification()

        # ==================================================
        # ADD BUTTON
        # ==================================================

        # Patients CANNOT add diagnoses.
        if role in ["admin", "doctor"]:

            if st.button(
                "Add Diagnosis",
                type="primary",
                key="add_diagnosis_button"
            ):
                self.add_diagnosis_modal()

        st.divider()

        # ==================================================
        # DIAGNOSIS LIST
        # ==================================================

        self.show_diagnoses()

    # ======================================================
    # CENTERED SUCCESS NOTIFICATION
    # ======================================================

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
            key="diagnosis_notification_ok"
        ):
            st.session_state["diagnosis_notification"] = None
            st.rerun()

    # ======================================================
    # SHOW NOTIFICATION
    # ======================================================

    def show_notification(self):

        message = st.session_state.get(
            "diagnosis_notification"
        )

        if message:
            self.notification_modal(message)

    # ======================================================
    # GET APPOINTMENTS
    # ======================================================

    def get_appointments(self):

        appointments, error = (
            self.appointment_service.get_all()
        )

        if error:
            st.error(
                f"Unable to load appointments:\n\n{error}"
            )
            return []

        appointments = appointments or []

        role = self.get_role()
        user = self.get_current_user()

        # ==================================================
        # ADMIN
        # ==================================================

        if role == "admin":
            return appointments

        # ==================================================
        # DOCTOR
        # ==================================================

        if role == "doctor":

            # Get doctor's profile ID
            profile_id = user.get("id")

            # Find doctor's doctor_id
            doctor_id = None

            for appointment in appointments:

                doctor = (
                    appointment.get("doctors")
                    or {}
                )

                if doctor.get("profile_id") == profile_id:
                    doctor_id = doctor.get(
                        "doctor_id"
                    )
                    break

            # If we could not determine doctor ID
            if not doctor_id:
                return []

            # Only doctor's appointments
            return [
                appointment
                for appointment in appointments
                if appointment.get("doctor_id")
                == doctor_id
            ]

        # ==================================================
        # PATIENT
        # ==================================================

        if role == "patient":

            profile_id = user.get("id")

            patient_id = None

            for appointment in appointments:

                patient = (
                    appointment.get("patients")
                    or {}
                )

                if patient.get("profile_id") == profile_id:
                    patient_id = patient.get(
                        "patient_id"
                    )
                    break

            if not patient_id:
                return []

            return [
                appointment
                for appointment in appointments
                if appointment.get("patient_id")
                == patient_id
            ]

        return []

    # ======================================================
    # PATIENT NAME
    # ======================================================

    def get_patient_name(self, appointment):

        patient = (
            appointment.get("patients")
            or {}
        )

        profile = (
            patient.get("profiles")
            or {}
        )

        first_name = profile.get(
            "first_name",
            ""
        )

        last_name = profile.get(
            "last_name",
            ""
        )

        return (
            f"{first_name} {last_name}"
        ).strip()

    # ======================================================
    # DOCTOR NAME
    # ======================================================

    def get_doctor_name(self, appointment):

        doctor = (
            appointment.get("doctors")
            or {}
        )

        profile = (
            doctor.get("profiles")
            or {}
        )

        first_name = profile.get(
            "first_name",
            ""
        )

        last_name = profile.get(
            "last_name",
            ""
        )

        name = (
            f"{first_name} {last_name}"
        ).strip()

        if name:
            return f"Dr. {name}"

        return "Doctor"

    # ======================================================
    # APPOINTMENT DISPLAY
    # ======================================================

    def appointment_display(self, appointment):

        patient_name = (
            self.get_patient_name(
                appointment
            )
        )

        doctor_name = (
            self.get_doctor_name(
                appointment
            )
        )

        appointment_date = (
            appointment.get(
                "appointment_date"
            )
            or "N/A"
        )

        if appointment_date:

            try:

                parsed_date = (
                    datetime.datetime.fromisoformat(
                        appointment_date.replace(
                            "Z",
                            "+00:00"
                        )
                    )
                )

                appointment_date = (
                    parsed_date.strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                )

            except (
                ValueError,
                TypeError
            ):
                pass

        return (
            f"{patient_name or 'Unknown Patient'} "
            f"— {doctor_name} "
            f"— {appointment_date}"
        )

    # ======================================================
    # ADD DIAGNOSIS MODAL
    # ======================================================

    @st.dialog("Add Diagnosis")
    def add_diagnosis_modal(self):

        role = self.get_role()

        # Patients should never reach this modal.
        if role == "patient":
            st.error(
                "Patients cannot create diagnoses."
            )
            return

        st.subheader(
            "Create New Diagnosis"
        )

        appointments = (
            self.get_appointments()
        )

        if not appointments:

            st.warning(
                "No appointments are available."
            )

            return

        # ==================================================
        # APPOINTMENT OPTIONS
        # ==================================================

        appointment_options = {
            self.appointment_display(
                appointment
            ): appointment
            for appointment in appointments
        }

        # ==================================================
        # FORM
        # ==================================================

        with st.form(
            "diagnosis_add_form",
            clear_on_submit=True
        ):

            st.markdown(
                "### Appointment"
            )

            appointment_label = st.selectbox(
                "Appointment",
                options=list(
                    appointment_options.keys()
                ),
                index=None,
                placeholder="Select an appointment..."
            )

            st.markdown(
                "### Medical Information"
            )

            diagnosis_description = (
                st.text_area(
                    "Diagnosis",
                    placeholder="Enter diagnosis..."
                )
            )

            treatment_plan = (
                st.text_area(
                    "Treatment Plan",
                    placeholder="Enter treatment plan..."
                )
            )

            submitted = (
                st.form_submit_button(
                    "Create Diagnosis",
                    type="primary",
                    use_container_width=True
                )
            )

        # ==================================================
        # NOTHING SUBMITTED
        # ==================================================

        if not submitted:
            return

        # ==================================================
        # VALIDATION
        # ==================================================

        if not appointment_label:

            st.error(
                "Please select an appointment."
            )

            return

        if not diagnosis_description.strip():

            st.error(
                "Diagnosis description is required."
            )

            return

        # ==================================================
        # SELECTED APPOINTMENT
        # ==================================================

        selected_appointment = (
            appointment_options[
                appointment_label
            ]
        )

        # ==================================================
        # CREATE DIAGNOSIS OBJECT
        # ==================================================

        diagnosis = Diagnosis(

            appointment_id=(
                selected_appointment[
                    "appointment_id"
                ]
            ),

            diagnosis_description=(
                diagnosis_description.strip()
            ),

            treatment_plan=(
                treatment_plan.strip()
            )
        )

        # ==================================================
        # CREATE
        # ==================================================

        created, error = (
            self.service.create(
                diagnosis
            )
        )

        # ==================================================
        # ERROR
        # ==================================================

        if error:

            st.error(
                f"Unable to add diagnosis:\n\n{error}"
            )

            return

        # ==================================================
        # PATIENT NAME
        # ==================================================

        patient_name = (
            self.get_patient_name(
                selected_appointment
            )
        )

        # ==================================================
        # SUCCESS
        # ==================================================

        st.session_state[
            "diagnosis_notification"
        ] = (
            f"Diagnosis for <strong>"
            f"{patient_name}"
            f"</strong> has been added successfully."
        )

        st.rerun()

    # ======================================================
    # SHOW DIAGNOSES
    # ======================================================

    def show_diagnoses(self):

        user = self.get_current_user()

        if not user:
            st.error(
                "User session not found."
            )
            return

        # ==================================================
        # IMPORTANT:
        # GET FILTERED DIAGNOSES
        # ==================================================

        diagnoses, error = (
            self.service.get_for_user(
                user
            )
        )

        if error:

            st.error(
                f"Unable to load diagnoses:\n\n{error}"
            )

            return

        if not diagnoses:

            st.info(
                "No diagnoses found."
            )

            return

        role = self.get_role()

        # ==================================================
        # DISPLAY
        # ==================================================

        for diagnosis in diagnoses:

            appointment = (
                diagnosis.get(
                    "appointments"
                )
                or {}
            )

            # ----------------------------------------------
            # PATIENT
            # ----------------------------------------------

            patient_name = (
                self.get_patient_name(
                    appointment
                )
            )

            # ----------------------------------------------
            # DOCTOR
            # ----------------------------------------------

            doctor_name = (
                self.get_doctor_name(
                    appointment
                )
            )

            # ----------------------------------------------
            # DATE
            # ----------------------------------------------

            appointment_date = (
                appointment.get(
                    "appointment_date"
                )
                or "N/A"
            )

            formatted_date = (
                appointment_date
            )

            if appointment_date != "N/A":

                try:

                    parsed_date = (
                        datetime.datetime.fromisoformat(
                            appointment_date.replace(
                                "Z",
                                "+00:00"
                            )
                        )
                    )

                    formatted_date = (
                        parsed_date.strftime(
                            "%B %d, %Y at %I:%M %p"
                        )
                    )

                except (
                    ValueError,
                    TypeError
                ):
                    pass

            # ==================================================
            # DIAGNOSIS CARD
            # ==================================================

            col1, col2 = st.columns(
                [7, 3]
            )

            with col1:

                st.subheader(
                    f"{patient_name or 'Unknown Patient'}"
                )

                st.write(
                    f"**Doctor:** "
                    f"{doctor_name}"
                )

                st.write(
                    f"**Appointment:** "
                    f"{formatted_date}"
                )

                st.write(
                    f"**Diagnosis:** "
                    f"{diagnosis.get(
                        'diagnosis_description',
                        'N/A'
                    )}"
                )

                st.write(
                    f"**Treatment Plan:** "
                    f"{diagnosis.get(
                        'treatment_plan',
                        'N/A'
                    )}"
                )

            # ==================================================
            # ACTION BUTTONS
            # ==================================================

            with col2:

                st.write("")

                # Patients CANNOT edit/delete.
                if role in ["admin", "doctor"]:

                    # ------------------------------------------
                    # EDIT
                    # ------------------------------------------

                    if st.button(
                        "Edit",
                        key=(
                            f"edit_diagnosis_"
                            f"{diagnosis['diagnosis_id']}"
                        ),
                        use_container_width=True
                    ):

                        self.edit_diagnosis_modal(
                            diagnosis
                        )

                    # ------------------------------------------
                    # DELETE
                    # ------------------------------------------

                    if st.button(
                        "Delete",
                        key=(
                            f"delete_diagnosis_"
                            f"{diagnosis['diagnosis_id']}"
                        ),
                        use_container_width=True
                    ):

                        self.delete_diagnosis_modal(
                            diagnosis
                        )

            st.divider()

    # ======================================================
    # EDIT DIAGNOSIS MODAL
    # ======================================================

    @st.dialog("Edit Diagnosis")
    def edit_diagnosis_modal(
        self,
        diagnosis
    ):

        role = self.get_role()

        if role not in ["admin", "doctor"]:

            st.error(
                "You do not have permission to edit diagnoses."
            )

            return

        appointments = (
            self.get_appointments()
        )

        if not appointments:

            st.warning(
                "No appointments available."
            )

            return

        appointment_options = {
            self.appointment_display(
                appointment
            ): appointment
            for appointment in appointments
        }

        # ==================================================
        # CURRENT APPOINTMENT
        # ==================================================

        current_appointment = next(
            (
                appointment
                for appointment in appointments
                if appointment[
                    "appointment_id"
                ]
                == diagnosis[
                    "appointment_id"
                ]
            ),
            None
        )

        current_label = None

        if current_appointment:

            current_label = (
                self.appointment_display(
                    current_appointment
                )
            )

        appointment_labels = list(
            appointment_options.keys()
        )

        if current_label in appointment_labels:

            appointment_index = (
                appointment_labels.index(
                    current_label
                )
            )

        else:

            appointment_index = 0

        # ==================================================
        # FORM
        # ==================================================

        with st.form(
            "diagnosis_edit_form"
        ):

            st.markdown(
                "### Appointment"
            )

            appointment_label = st.selectbox(
                "Appointment",
                appointment_labels,
                index=appointment_index
            )

            st.markdown(
                "### Medical Information"
            )

            diagnosis_description = (
                st.text_area(
                    "Diagnosis",
                    value=(
                        diagnosis.get(
                            "diagnosis_description"
                        )
                        or ""
                    )
                )
            )

            treatment_plan = (
                st.text_area(
                    "Treatment Plan",
                    value=(
                        diagnosis.get(
                            "treatment_plan"
                        )
                        or ""
                    )
                )
            )

            submitted = (
                st.form_submit_button(
                    "Save Changes",
                    type="primary",
                    use_container_width=True
                )
            )

        # ==================================================
        # NOTHING SUBMITTED
        # ==================================================

        if not submitted:
            return

        # ==================================================
        # VALIDATION
        # ==================================================

        if not diagnosis_description.strip():

            st.error(
                "Diagnosis description is required."
            )

            return

        # ==================================================
        # SELECT APPOINTMENT
        # ==================================================

        selected_appointment = (
            appointment_options[
                appointment_label
            ]
        )

        # ==================================================
        # UPDATE
        # ==================================================

        data = {

            "appointment_id": (
                selected_appointment[
                    "appointment_id"
                ]
            ),

            "diagnosis_description": (
                diagnosis_description.strip()
            ),

            "treatment_plan": (
                treatment_plan.strip()
            )
        }

        result, error = (
            self.service.update(
                diagnosis[
                    "diagnosis_id"
                ],
                data
            )
        )

        # ==================================================
        # ERROR
        # ==================================================

        if error:

            st.error(
                f"Unable to update diagnosis:\n\n{error}"
            )

            return

        # ==================================================
        # PATIENT NAME
        # ==================================================

        patient_name = (
            self.get_patient_name(
                selected_appointment
            )
        )

        # ==================================================
        # SUCCESS
        # ==================================================

        st.session_state[
            "diagnosis_notification"
        ] = (
            f"Diagnosis for <strong>"
            f"{patient_name}"
            f"</strong> has been updated successfully."
        )

        st.rerun()

    # ======================================================
    # DELETE DIAGNOSIS MODAL
    # ======================================================

    @st.dialog("Delete Diagnosis")
    def delete_diagnosis_modal(
        self,
        diagnosis
    ):

        role = self.get_role()

        if role not in ["admin", "doctor"]:

            st.error(
                "You do not have permission to delete diagnoses."
            )

            return

        appointment = (
            diagnosis.get(
                "appointments"
            )
            or {}
        )

        patient_name = (
            self.get_patient_name(
                appointment
            )
        )

        diagnosis_text = (
            diagnosis.get(
                "diagnosis_description"
            )
            or "Unknown diagnosis"
        )

        st.warning(
            f"Are you sure you want to delete "
            f"the diagnosis for "
            f"**{patient_name}**?"
        )

        st.write(
            f"**Diagnosis:** "
            f"{diagnosis_text}"
        )

        st.write(
            "This action cannot be undone."
        )

        st.divider()

        col1, col2 = st.columns(2)

        # ==================================================
        # CANCEL
        # ==================================================

        with col1:

            if st.button(
                "Cancel",
                key=(
                    f"cancel_diagnosis_"
                    f"{diagnosis['diagnosis_id']}"
                ),
                use_container_width=True
            ):

                st.rerun()

        # ==================================================
        # DELETE
        # ==================================================

        with col2:

            if st.button(
                "Delete Diagnosis",
                key=(
                    f"confirm_delete_diagnosis_"
                    f"{diagnosis['diagnosis_id']}"
                ),
                type="primary",
                use_container_width=True
            ):

                success, error = (
                    self.service.delete(
                        diagnosis[
                            "diagnosis_id"
                        ]
                    )
                )

                # ==========================================
                # ERROR
                # ==========================================

                if error:

                    st.error(
                        f"Unable to delete diagnosis:\n\n{error}"
                    )

                    return

                # ==========================================
                # SUCCESS
                # ==========================================

                st.session_state[
                    "diagnosis_notification"
                ] = (
                    f"Diagnosis for <strong>"
                    f"{patient_name}"
                    f"</strong> has been deleted successfully."
                )

                st.rerun()