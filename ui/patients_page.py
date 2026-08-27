import datetime
import re

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

        # ==================================================
        # CURRENT DATE
        # ==================================================

        today = datetime.date.today()
        current_year = today.year
        minimum_year = current_year - 100

        # ==================================================
        # FORM
        # ==================================================

        with st.form(
            "patient_add_form",
            clear_on_submit=False
        ):

            st.markdown(
                "### Personal Information"
            )

            col1, col2 = st.columns(2)

            # ==================================================
            # LEFT COLUMN
            # ==================================================

            with col1:

                first_name = st.text_input(
                    "First Name",
                    key="patient_add_first_name"
                )

                email = st.text_input(
                    "Email",
                    key="patient_add_email"
                )

            # ==================================================
            # RIGHT COLUMN
            # ==================================================

            with col2:

                last_name = st.text_input(
                    "Last Name",
                    key="patient_add_last_name"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="patient_add_password"
                )

            # ==================================================
            # DATE OF BIRTH
            # ==================================================

            st.markdown(
                "#### Date of Birth"
            )

            dob_col1, dob_col2, dob_col3 = st.columns(3)

            # ==================================================
            # BIRTH MONTH
            # ==================================================

            with dob_col1:

                birth_month = st.selectbox(
                    "Birth Month",
                    options=list(range(1, 13)),
                    format_func=lambda month: (
                        datetime.date(
                            2000,
                            month,
                            1
                        ).strftime("%B")
                    ),
                    key="patient_add_birth_month"
                )

            # ==================================================
            # BIRTH DAY
            # ==================================================

            with dob_col2:

                if birth_month == 2:
                    max_day = 29

                elif birth_month in [4, 6, 9, 11]:
                    max_day = 30

                else:
                    max_day = 31

                birth_day = st.selectbox(
                    "Birth Day",
                    options=list(
                        range(
                            1,
                            max_day + 1
                        )
                    ),
                    key="patient_add_birth_day"
                )

            # ==================================================
            # BIRTH YEAR
            # ==================================================

            with dob_col3:

                birth_year = st.selectbox(
                    "Birth Year",
                    options=list(
                        range(
                            current_year,
                            minimum_year - 1,
                            -1
                        )
                    ),
                    key="patient_add_birth_year"
                )

            # ==================================================
            # PHONE
            # ==================================================

            phone = st.text_input(
                "Phone",
                placeholder="Enter numbers only",
                key="patient_add_phone"
            )

            # ==================================================
            # ADDRESS
            # ==================================================

            address = st.text_area(
                "Address",
                key="patient_add_address"
            )

            # ==================================================
            # MEDICAL HISTORY
            # ==================================================

            medical_history = st.text_area(
                "Medical History",
                placeholder=(
                    "Enter relevant medical history, "
                    "previous illnesses, allergies, "
                    "surgeries, etc."
                ),
                key="patient_add_medical_history"
            )

            # ==================================================
            # SUBMIT
            # ==================================================

            submitted = st.form_submit_button(
                "Create Patient",
                type="primary",
                use_container_width=True
            )

        # ==================================================
        # WAIT FOR SUBMISSION
        # ==================================================

        if not submitted:
            return

        # ==================================================
        # NORMALIZE EMAIL
        # ==================================================

        normalized_email = email.strip().lower()

        # ==================================================
        # VALIDATION - FIRST NAME
        # ==================================================

        if not first_name.strip():

            st.error(
                "First name is required."
            )

            return

        # ==================================================
        # VALIDATION - LAST NAME
        # ==================================================

        if not last_name.strip():

            st.error(
                "Last name is required."
            )

            return

        # ==================================================
        # VALIDATION - EMAIL
        # ==================================================

        if not normalized_email:

            st.error(
                "Email is required."
            )

            return

        # ==================================================
        # EMAIL FORMAT
        # ==================================================

        if (
            "@" not in normalized_email
            or "." not in normalized_email.split("@")[-1]
        ):

            st.error(
                "Please enter a valid email address."
            )

            return

        # ==================================================
        # VALIDATION - PASSWORD
        # ==================================================

        if not password:

            st.error(
                "Password is required."
            )

            return

        # ==================================================
        # PHONE VALIDATION
        # ==================================================

        phone = phone.strip()

        if not phone:

            st.error(
                "Phone number is required."
            )

            return

        # Numbers only
        if not re.fullmatch(r"\d+", phone):

            st.error(
                "Phone number must contain numbers only."
            )

            return

        # ==================================================
        # VALIDATE DATE OF BIRTH
        # ==================================================

        try:

            date_of_birth = datetime.date(
                birth_year,
                birth_month,
                birth_day
            )

        except ValueError:

            st.error(
                "Please select a valid date of birth."
            )

            return

        # ==================================================
        # PREVENT FUTURE DATE
        # ==================================================

        if date_of_birth > today:

            st.error(
                "Date of birth cannot be in the future."
            )

            return

        # ==================================================
        # CREATE PATIENT OBJECT
        # ==================================================

        patient = Patient(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=normalized_email,
            password_hash=password,
            address=address.strip(),
            phone=phone,
            date_of_birth=date_of_birth,
            medical_history=medical_history.strip()
        )

        # ==================================================
        # DATABASE
        # ==================================================

        created_patient, error = (
            self.service.create(patient)
        )

        # ==================================================
        # DATABASE ERROR
        # ==================================================

        if error:

            error_text = str(error).lower()

            if (
                "duplicate" in error_text
                or "unique" in error_text
                or "profiles_email_key" in error_text
                or "email" in error_text
            ):

                st.error(
                    "This email address is already taken. "
                    "Please enter a different email address."
                )

            else:

                st.error(
                    f"Unable to add patient:\n\n{error}"
                )

            # IMPORTANT:
            # DO NOT CLEAR FORM WHEN DATABASE CREATION FAILS

            return

        # ==================================================
        # SUCCESS NAME
        # ==================================================

        full_name = (
            f"{first_name.strip()} "
            f"{last_name.strip()}"
        )

        # ==================================================
        # SUCCESS NOTIFICATION
        # ==================================================

        st.session_state[
            "patient_notification"
        ] = (
            f"Patient <strong>{full_name}</strong> "
            f"has been added successfully."
        )

        # ==================================================
        # CLEAR ADD FORM
        #
        # IMPORTANT:
        # We remove the widget keys only AFTER success.
        # We do NOT assign values to them while the widgets
        # are still instantiated.
        # ==================================================

        for key in [
            "patient_add_first_name",
            "patient_add_last_name",
            "patient_add_email",
            "patient_add_password",
            "patient_add_phone",
            "patient_add_address",
            "patient_add_medical_history",
            "patient_add_birth_month",
            "patient_add_birth_day",
            "patient_add_birth_year"
        ]:

            st.session_state.pop(
                key,
                None
            )

        st.rerun()

    # ======================================================
    # PATIENT LIST
    # ======================================================

    def show_patient_list(self):

        patients, error = (
            self.service.get_all()
        )

        if error:

            st.error(
                f"Unable to load patients:\n\n{error}"
            )

            return

        if not patients:

            st.info(
                "No patients found."
            )

            return

        for patient in patients:

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

            full_name = (
                f"{first_name} {last_name}"
            ).strip()

            col1, col2 = st.columns(
                [7, 3]
            )

            # ==================================================
            # PATIENT INFORMATION
            # ==================================================

            with col1:

                st.subheader(
                    full_name
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
    def medical_record_modal(
        self,
        patient
    ):

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
            full_name
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
                f"### {formatted_date}"
            )

            if formatted_time:

                st.caption(
                    formatted_time
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
            # DIAGNOSIS
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

            if not diagnoses:

                st.info(
                    "No diagnosis has been recorded "
                    "for this appointment."
                )

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
                        f"#### 🩺 Diagnosis "
                        f"{diagnosis_index}"
                    )

                    st.write(
                        f"**Diagnosis:** "
                        f"{diagnosis_description}"
                    )

                    st.write(
                        f"**Treatment Plan:** "
                        f"{treatment_plan}"
                    )

                    if diagnosis_index < len(
                        diagnoses
                    ):

                        st.divider()

            if index < len(appointments) - 1:

                st.divider()

    # ======================================================
    # EDIT PATIENT
    # ======================================================

    @st.dialog("Edit Patient")
    def edit_patient_modal(
        self,
        patient
    ):

        profile = (
            patient.get("profiles")
            or {}
        )

        st.write(
            "Update the patient's information."
        )

        # ==================================================
        # EXISTING DATE
        # ==================================================

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
        # DATE RANGE
        # ==================================================

        today = datetime.date.today()
        current_year = today.year
        minimum_year = current_year - 100

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

            # ==================================================
            # LEFT COLUMN
            # ==================================================

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

            # ==================================================
            # RIGHT COLUMN
            # ==================================================

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
                    ) or "",
                    placeholder="Enter numbers only"
                )

            # ==================================================
            # DATE OF BIRTH
            # ==================================================

            st.markdown(
                "#### Date of Birth"
            )

            dob_col1, dob_col2, dob_col3 = st.columns(3)

            existing_month = (
                existing_date.month
            )

            existing_day = (
                existing_date.day
            )

            existing_year = (
                existing_date.year
            )

            # ==================================================
            # KEEP YEAR INSIDE 100-YEAR RANGE
            # ==================================================

            if existing_year > current_year:

                existing_year = current_year

            if existing_year < minimum_year:

                existing_year = minimum_year

            # ==================================================
            # MONTH
            # ==================================================

            with dob_col1:

                edit_birth_month = st.selectbox(
                    "Birth Month",
                    options=list(
                        range(1, 13)
                    ),
                    index=existing_month - 1,
                    format_func=lambda month: (
                        datetime.date(
                            2000,
                            month,
                            1
                        ).strftime("%B")
                    )
                )

            # ==================================================
            # DAY
            # ==================================================

            with dob_col2:

                if edit_birth_month == 2:

                    max_day = 29

                elif edit_birth_month in [
                    4,
                    6,
                    9,
                    11
                ]:

                    max_day = 30

                else:

                    max_day = 31

                if existing_day > max_day:

                    existing_day = max_day

                edit_birth_day = st.selectbox(
                    "Birth Day",
                    options=list(
                        range(
                            1,
                            max_day + 1
                        )
                    ),
                    index=existing_day - 1
                )

            # ==================================================
            # YEAR
            # ==================================================

            with dob_col3:

                edit_birth_year = st.selectbox(
                    "Birth Year",
                    options=list(
                        range(
                            current_year,
                            minimum_year - 1,
                            -1
                        )
                    ),
                    index=(
                        current_year
                        - existing_year
                    )
                )

            # ==================================================
            # ADDRESS
            # ==================================================

            address = st.text_area(
                "Address",
                value=patient.get(
                    "address",
                    ""
                ) or ""
            )

            # ==================================================
            # MEDICAL HISTORY
            # ==================================================

            medical_history = st.text_area(
                "Medical History",
                value=patient.get(
                    "medical_history",
                    ""
                ) or ""
            )

            # ==================================================
            # SUBMIT
            # ==================================================

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
                use_container_width=True
            )

        if not submitted:

            return

        # ==================================================
        # NORMALIZE EMAIL
        # ==================================================

        normalized_email = (
            email.strip().lower()
        )

        # ==================================================
        # VALIDATION - FIRST NAME
        # ==================================================

        if not first_name.strip():

            st.error(
                "First name is required."
            )

            return

        # ==================================================
        # VALIDATION - LAST NAME
        # ==================================================

        if not last_name.strip():

            st.error(
                "Last name is required."
            )

            return

        # ==================================================
        # VALIDATION - EMAIL
        # ==================================================

        if not normalized_email:

            st.error(
                "Email is required."
            )

            return

        # ==================================================
        # EMAIL FORMAT
        # ==================================================

        if (
            "@" not in normalized_email
            or "." not in normalized_email.split("@")[-1]
        ):

            st.error(
                "Please enter a valid email address."
            )

            return

        # ==================================================
        # PHONE VALIDATION
        # ==================================================

        phone = phone.strip()

        if not phone:

            st.error(
                "Phone number is required."
            )

            return

        if not re.fullmatch(r"\d+", phone):

            st.error(
                "Phone number must contain numbers only."
            )

            return

        # ==================================================
        # VALIDATE DATE
        # ==================================================

        try:

            date_of_birth = datetime.date(
                edit_birth_year,
                edit_birth_month,
                edit_birth_day
            )

        except ValueError:

            st.error(
                "Please select a valid date of birth."
            )

            return

        # ==================================================
        # PREVENT FUTURE DATE
        # ==================================================

        if date_of_birth > today:

            st.error(
                "Date of birth cannot be in the future."
            )

            return

        # ==================================================
        # PROFILE DATA
        # ==================================================

        profile_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": normalized_email
        }

        # ==================================================
        # PATIENT DATA
        # ==================================================

        patient_data = {

            "address": address.strip(),

            "phone": phone,

            "date_of_birth": (
                date_of_birth.isoformat()
            ),

            "medical_history": (
                medical_history.strip()
            )
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

        # ==================================================
        # ERROR
        # ==================================================

        if error:

            error_text = str(error).lower()

            if (
                "duplicate" in error_text
                or "unique" in error_text
                or "profiles_email_key" in error_text
                or "email" in error_text
            ):

                st.error(
                    "This email address is already taken. "
                    "Please enter a different email address."
                )

            else:

                st.error(
                    f"Unable to update patient:\n\n{error}"
                )

            return

        # ==================================================
        # SUCCESS
        # ==================================================

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
    def delete_patient_modal(
        self,
        patient
    ):

        profile = (
            patient.get("profiles")
            or {}
        )

        name = (
            f"{profile.get('first_name', '')} "
            f"{profile.get('last_name', '')}"
        ).strip()

        # ==================================================
        # CONFIRMATION
        # ==================================================

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

                # ==========================================
                # SUCCESS NOTIFICATION
                # ==========================================

                st.session_state[
                    "patient_notification"
                ] = (
                    f"Patient <strong>{name}</strong> "
                    f"has been deleted successfully."
                )

                st.rerun()