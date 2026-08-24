import datetime
import streamlit as st

from models.patient import Patient
from services.patient_service import PatientService


class PatientsPage:

    def __init__(self):
        self.service = PatientService()

    # ======================================================
    # MAIN PAGE
    # ======================================================

    def show(self):

        st.title("Patients")

        self.show_notification()

        if st.button(
            "Add Patient",
            type="primary",
            key="add_patient_button"
        ):
            self.add_patient_modal()

        st.divider()

        self.show_patient_list()

    # ======================================================
    # SUCCESS NOTIFICATION
    # ======================================================

    @st.dialog("Success")
    def notification_modal(self, message):

        st.markdown(
            f"""<div style="
text-align: center;
padding: 20px 10px;
font-size: 20px;
font-weight: 500;
">
{message}
</div>""",
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "OK",
            type="primary",
            use_container_width=True,
            key="patient_notification_ok"
        ):
            st.session_state["patient_notification"] = None
            st.rerun()

    # ======================================================
    # SHOW NOTIFICATION
    # ======================================================

    def show_notification(self):

        message = st.session_state.get(
            "patient_notification"
        )

        if message:
            self.notification_modal(message)

    # ======================================================
    # ADD PATIENT MODAL
    # ======================================================

    @st.dialog("Add Patient")
    def add_patient_modal(self):

        st.subheader("Create New Patient")

        with st.form(
            "patient_add_form",
            clear_on_submit=True
        ):

            st.markdown("### Personal Information")

            col1, col2 = st.columns(2)

            with col1:

                first_name = st.text_input(
                    "First Name"
                )

                email = st.text_input(
                    "Email"
                )

                date_of_birth = st.date_input(
                    "Date of Birth"
                )

            with col2:

                last_name = st.text_input(
                    "Last Name"
                )

                password = st.text_input(
                    "Password",
                    type="password"
                )

                phone = st.text_input(
                    "Phone"
                )

            st.markdown("### Patient Information")

            address = st.text_area(
                "Address"
            )

            medical_history = st.text_area(
                "Medical History",
                placeholder=(
                    "Enter relevant medical history, "
                    "previous illnesses, allergies, "
                    "surgeries, etc."
                )
            )

            submitted = st.form_submit_button(
                "Create Patient",
                type="primary",
                use_container_width=True
            )

        if not submitted:
            return

        # ==================================================
        # VALIDATION
        # ==================================================

        if not first_name.strip():
            st.error("First name is required.")
            return

        if not last_name.strip():
            st.error("Last name is required.")
            return

        if not email.strip():
            st.error("Email is required.")
            return

        if not password:
            st.error("Password is required.")
            return

        # ==================================================
        # CREATE PATIENT
        # ==================================================

        patient = Patient(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip(),
            password_hash=password,
            address=address.strip(),
            phone=phone.strip(),
            date_of_birth=date_of_birth,
            medical_history=medical_history.strip()
        )

        created_patient, error = self.service.create(
            patient
        )

        if error:

            st.error(
                f"Unable to add patient:\n\n{error}"
            )

            return

        full_name = (
            f"{first_name.strip()} "
            f"{last_name.strip()}"
        )

        st.session_state[
            "patient_notification"
        ] = (
            f"Patient <strong>{full_name}</strong> "
            f"has been added successfully."
        )

        st.rerun()

    # ======================================================
    # PATIENT LIST
    # ======================================================

    def show_patient_list(self):

        patients, error = self.service.get_all()

        if error:

            st.error(
                f"Unable to load patients:\n\n{error}"
            )

            return

        if not patients:

            st.info("No patients found.")

            return

        for patient in patients:

            profile = patient.get("profiles") or {}

            first_name = profile.get(
                "first_name",
                ""
            )

            last_name = profile.get(
                "last_name",
                ""
            )

            full_name = (
                f"{first_name} {last_name}"
            ).strip()

            col1, col2 = st.columns([7, 3])

            # ==================================================
            # PATIENT INFORMATION
            # ==================================================

            with col1:

                st.subheader(
                    f"{full_name}"
                )

                st.write(
                    f"**Email:** "
                    f"{profile.get('email', 'N/A')}"
                )

                st.write(
                    f"**Phone:** "
                    f"{patient.get('phone', 'N/A')}"
                )

                st.write(
                    f"**Date of Birth:** "
                    f"{patient.get('date_of_birth', 'N/A')}"
                )

                st.write(
                    f"**Address:** "
                    f"{patient.get('address', 'N/A')}"
                )

            # ==================================================
            # ACTIONS
            # ==================================================

            with col2:

                st.write("")

                if st.button(
                    "Medical Record",
                    key=(
                        f"record_patient_"
                        f"{patient['patient_id']}"
                    ),
                    use_container_width=True
                ):
                    self.medical_record_modal(
                        patient
                    )

                if st.button(
                    "Edit",
                    key=(
                        f"edit_patient_"
                        f"{patient['patient_id']}"
                    ),
                    use_container_width=True
                ):
                    self.edit_patient_modal(
                        patient
                    )

                if st.button(
                    "Delete",
                    key=(
                        f"delete_patient_"
                        f"{patient['patient_id']}"
                    ),
                    use_container_width=True
                ):
                    self.delete_patient_modal(
                        patient
                    )

            st.divider()

    # ======================================================
    # MEDICAL RECORD
    # ======================================================

    @st.dialog("Medical Record")
    def medical_record_modal(self, patient):

        # ==================================================
        # LOAD MEDICAL RECORD
        # ==================================================

        patient_record, error = (
            self.service.get_medical_record(
                patient["patient_id"]
            )
        )

        if error:

            st.error(
                f"Unable to load medical record:\n\n{error}"
            )

            return

        if not patient_record:

            st.warning(
                "Medical record not found."
            )

            return

        # ==================================================
        # PROFILE
        # ==================================================

        profile = (
            patient_record.get("profiles")
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

        full_name = (
            f"{first_name} {last_name}"
        ).strip()

        # ==================================================
        # PATIENT INFORMATION
        # ==================================================

        st.subheader(
            f"{full_name}"
        )

        st.write(
            f"**Email:** "
            f"{profile.get('email', 'N/A')}"
        )

        st.write(
            f"**Phone:** "
            f"{patient_record.get('phone') or 'N/A'}"
        )

        st.write(
            f"**Date of Birth:** "
            f"{patient_record.get('date_of_birth') or 'N/A'}"
        )

        st.write(
            f"**Address:** "
            f"{patient_record.get('address') or 'N/A'}"
        )

        # ==================================================
        # GENERAL MEDICAL HISTORY
        # ==================================================

        st.divider()

        st.markdown(
            "## General Medical History"
        )

        medical_history = (
            patient_record.get(
                "medical_history"
            )
        )

        if medical_history:

            st.info(
                medical_history
            )

        else:

            st.caption(
                "No general medical history has been recorded."
            )

        # ==================================================
        # MEDICAL TIMELINE
        # ==================================================

        st.divider()

        st.markdown(
            "## Medical Timeline"
        )

        appointments = (
            patient_record.get(
                "appointments"
            )
            or []
        )

        # ==================================================
        # NO APPOINTMENTS
        # ==================================================

        if not appointments:

            st.info(
                "No appointments have been recorded "
                "for this patient yet."
            )

            st.caption(
                "Once an appointment is created and a "
                "diagnosis is recorded, it will appear "
                "here automatically."
            )

            return

        # ==================================================
        # SORT APPOINTMENTS
        # ==================================================

        appointments = sorted(
            appointments,
            key=lambda appointment: (
                appointment.get(
                    "appointment_date"
                )
                or ""
            ),
            reverse=True
        )

        # ==================================================
        # APPOINTMENT HISTORY
        # ==================================================

        for index, appointment in enumerate(
            appointments
        ):

            appointment_date = (
                appointment.get(
                    "appointment_date"
                )
            )

            formatted_date = (
                appointment_date
                or "Date not available"
            )

            formatted_time = ""

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

                    formatted_date = (
                        parsed_date.strftime(
                            "%B %d, %Y"
                        )
                    )

                    formatted_time = (
                        parsed_date.strftime(
                            "%I:%M %p"
                        )
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    formatted_time = ""

            # ==================================================
            # DOCTOR
            # ==================================================

            doctor = (
                appointment.get(
                    "doctors"
                )
                or {}
            )

            doctor_profile = (
                doctor.get(
                    "profiles"
                )
                or {}
            )

            doctor_first_name = (
                doctor_profile.get(
                    "first_name",
                    ""
                )
            )

            doctor_last_name = (
                doctor_profile.get(
                    "last_name",
                    ""
                )
            )

            doctor_name = (
                f"Dr. "
                f"{doctor_first_name} "
                f"{doctor_last_name}"
            ).strip()

            if doctor_name == "Dr.":

                doctor_name = (
                    "Doctor not assigned"
                )

            specialization = (
                doctor.get(
                    "specialization"
                )
                or "N/A"
            )

            # ==================================================
            # APPOINTMENT DETAILS
            # ==================================================

            status = (
                appointment.get(
                    "status"
                )
                or "N/A"
            )

            reason = (
                appointment.get(
                    "reason_for_visit"
                )
                or "No reason recorded."
            )

            # ==================================================
            # APPOINTMENT CARD
            # ==================================================

            st.markdown(
                f"""### {formatted_date}"""
            )

            if formatted_time:

                st.caption(
                    f"{formatted_time}"
                )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "#### Doctor"
                )

                st.write(
                    f"**{doctor_name}**"
                )

                st.caption(
                    specialization
                )

            with col2:

                st.markdown(
                    "#### Appointment Status"
                )

                st.write(
                    f"**{status.capitalize()}**"
                )

            st.markdown(
                "#### Reason for Visit"
            )

            st.write(
                reason
            )

            # ==================================================
            # DIAGNOSIS SECTION
            # ==================================================

            st.markdown(
                "### Diagnosis & Treatment"
            )

            diagnoses = (
                appointment.get(
                    "diagnoses"
                )
                or []
            )

            # ==================================================
            # NO DIAGNOSIS
            # ==================================================

            if not diagnoses:

                st.info(
                    "No diagnosis has been recorded "
                    "for this appointment."
                )

            # ==================================================
            # DIAGNOSES
            # ==================================================

            else:

                for diagnosis_index, diagnosis in enumerate(
                    diagnoses,
                    start=1
                ):

                    diagnosis_description = (
                        diagnosis.get(
                            "diagnosis_description"
                        )
                        or "No diagnosis description."
                    )

                    treatment_plan = (
                        diagnosis.get(
                            "treatment_plan"
                        )
                        or "No treatment plan recorded."
                    )

                    st.markdown(
                        f"#### 🩺 Diagnosis {diagnosis_index}"
                    )

                    st.write(
                        f"**Diagnosis:** "
                        f"{diagnosis_description}"
                    )

                    st.write(
                        f"**Treatment Plan:** "
                        f"{treatment_plan}"
                    )

                    if diagnosis_index < len(diagnoses):

                        st.divider()

            # ==================================================
            # APPOINTMENT SEPARATOR
            # ==================================================

            if index < len(appointments) - 1:

                st.divider()

    # ======================================================
    # EDIT PATIENT
    # ======================================================

    @st.dialog("Edit Patient")
    def edit_patient_modal(self, patient):

        profile = (
            patient.get("profiles")
            or {}
        )

        st.write(
            "Update the patient's information."
        )

        existing_date = (
            patient.get(
                "date_of_birth"
            )
        )

        if existing_date:

            try:

                if isinstance(
                    existing_date,
                    str
                ):

                    existing_date = (
                        datetime.date.fromisoformat(
                            existing_date
                        )
                    )

            except ValueError:

                existing_date = (
                    datetime.date.today()
                )

        else:

            existing_date = (
                datetime.date.today()
            )

        # ==================================================
        # FORM
        # ==================================================

        with st.form(
            "patient_edit_form"
        ):

            st.markdown(
                "### Personal Information"
            )

            col1, col2 = st.columns(2)

            with col1:

                first_name = st.text_input(
                    "First Name",
                    value=profile.get(
                        "first_name",
                        ""
                    )
                )

                email = st.text_input(
                    "Email",
                    value=profile.get(
                        "email",
                        ""
                    )
                )

                date_of_birth = st.date_input(
                    "Date of Birth",
                    value=existing_date
                )

            with col2:

                last_name = st.text_input(
                    "Last Name",
                    value=profile.get(
                        "last_name",
                        ""
                    )
                )

                phone = st.text_input(
                    "Phone",
                    value=patient.get(
                        "phone",
                        ""
                    ) or ""
                )

            address = st.text_area(
                "Address",
                value=patient.get(
                    "address",
                    ""
                ) or ""
            )

            medical_history = st.text_area(
                "Medical History",
                value=patient.get(
                    "medical_history",
                    ""
                ) or ""
            )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
                use_container_width=True
            )

        if not submitted:
            return

        # ==================================================
        # VALIDATION
        # ==================================================

        if not first_name.strip():

            st.error(
                "First name is required."
            )

            return

        if not last_name.strip():

            st.error(
                "Last name is required."
            )

            return

        if not email.strip():

            st.error(
                "Email is required."
            )

            return

        # ==================================================
        # PROFILE DATA
        # ==================================================

        profile_data = {

            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip()
        }

        # ==================================================
        # PATIENT DATA
        # ==================================================

        patient_data = {

            "address": address.strip(),

            "phone": phone.strip(),

            "date_of_birth":
                date_of_birth.isoformat(),

            "medical_history":
                medical_history.strip()
        }

        # ==================================================
        # UPDATE DATABASE
        # ==================================================

        result, error = (
            self.service.update(
                patient["patient_id"],
                patient["profile_id"],
                profile_data,
                patient_data
            )
        )

        if error:

            st.error(
                f"Unable to update patient:\n\n{error}"
            )

            return

        full_name = (
            f"{first_name.strip()} "
            f"{last_name.strip()}"
        )

        st.session_state[
            "patient_notification"
        ] = (
            f"Patient <strong>{full_name}</strong> "
            f"has been updated successfully."
        )

        st.rerun()

    # ======================================================
    # DELETE PATIENT
    # ======================================================

    @st.dialog("Delete Patient")
    def delete_patient_modal(self, patient):

        profile = (
            patient.get("profiles")
            or {}
        )

        name = (
            f"{profile.get('first_name', '')} "
            f"{profile.get('last_name', '')}"
        ).strip()

        st.warning(
            f"Are you sure you want to delete "
            f"**{name}**?"
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
                    f"cancel_patient_"
                    f"{patient['patient_id']}"
                ),
                use_container_width=True
            ):

                st.rerun()

        # ==================================================
        # DELETE
        # ==================================================

        with col2:

            if st.button(
                "Delete Patient",
                key=(
                    f"confirm_delete_patient_"
                    f"{patient['patient_id']}"
                ),
                type="primary",
                use_container_width=True
            ):

                success, error = (
                    self.service.delete(
                        patient["patient_id"],
                        patient["profile_id"]
                    )
                )

                if error:

                    st.error(
                        f"Unable to delete patient:\n\n{error}"
                    )

                    return

                st.session_state[
                    "patient_notification"
                ] = (
                    f"Patient <strong>{name}</strong> "
                    f"has been deleted successfully."
                )

                st.rerun()