import streamlit as st
import re

from models.doctor import Doctor
from services.doctor_service import DoctorService


class DoctorsPage:

    def __init__(self):
        self.service = DoctorService()

    # ======================================================
    # MAIN PAGE
    # ======================================================

    def show(self):

        st.title("Doctors")

        self.show_notification()

        if st.button(
            "Add Doctor",
            type="primary",
            key="add_doctor_button"
        ):
            self.add_doctor_modal()

        st.divider()

        self.show_doctor_list()

    # ======================================================
    # CENTERED NOTIFICATION
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
            key="doctor_notification_ok"
        ):
            st.session_state["doctor_notification"] = None
            st.rerun()

    # ======================================================
    # SHOW NOTIFICATION
    # ======================================================

    def show_notification(self):

        message = st.session_state.get(
            "doctor_notification"
        )

        if message:
            self.notification_modal(message)

    # ======================================================
    # ADD DOCTOR MODAL
    # ======================================================

    @st.dialog("Add Doctor")
    def add_doctor_modal(self):

        st.subheader("Create New Doctor")

        specialization_options = [
            "Cardiology",
            "Dermatology",
            "Emergency Medicine",
            "Family Medicine",
            "Gastroenterology",
            "General Surgery",
            "Internal Medicine",
            "Neurology",
            "Obstetrics and Gynecology",
            "Oncology",
            "Ophthalmology",
            "Orthopedics",
            "Otolaryngology",
            "Pediatrics",
            "Psychiatry",
            "Radiology",
            "Urology",
            "Other"
        ]

        # IMPORTANT:
        # Do NOT use clear_on_submit=True.
        #
        # This keeps all entered information when
        # validation fails.

        with st.form("doctor_add_form"):

            col1, col2 = st.columns(2)

            # ==================================================
            # LEFT COLUMN
            # ==================================================

            with col1:

                first_name = st.text_input(
                    "First Name",
                    key="doctor_add_first_name"
                )

                email = st.text_input(
                    "Email",
                    key="doctor_add_email"
                )

                specialization = st.selectbox(
                    "Specialization",
                    specialization_options,
                    key="doctor_add_specialization"
                )

            # ==================================================
            # RIGHT COLUMN
            # ==================================================

            with col2:

                last_name = st.text_input(
                    "Last Name",
                    key="doctor_add_last_name"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    key="doctor_add_password"
                )

                contact_info = st.text_input(
                    "Phone Number",
                    key="doctor_add_contact",
                    placeholder="e.g. 09171234567"
                )

            submitted = st.form_submit_button(
                "Create Doctor",
                type="primary",
                use_container_width=True
            )

        # ==================================================
        # WAIT FOR SUBMISSION
        # ==================================================

        if not submitted:
            return

        # ==================================================
        # BASIC VALIDATION
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

        if not password:

            st.error(
                "Password is required."
            )

            return

        if not specialization:

            st.error(
                "Specialization is required."
            )

            return

        # ==================================================
        # NORMALIZE EMAIL
        # ==================================================

        normalized_email = email.strip().lower()

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

        phone = contact_info.strip()

        if phone:

            if not phone.isdigit():

                st.error(
                    "Phone number must contain numbers only."
                )

                return

        # ==================================================
        # EMAIL DUPLICATE VALIDATION
        # ==================================================

        email_taken, email_error = (
            self.service.email_exists(
                normalized_email
            )
        )

        if email_error:

            st.error(
                f"Unable to verify email:\n\n{email_error}"
            )

            return

        if email_taken:

            st.error(
                "This email address is already taken. "
                "Please enter a different email address."
            )

            return

        # ==================================================
        # CREATE DOCTOR OBJECT
        # ==================================================

        doctor = Doctor(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=normalized_email,
            password_hash=password,
            specialization=specialization,
            contact_info=phone
        )

        # ==================================================
        # DATABASE
        # ==================================================

        created_doctor, error = (
            self.service.create(doctor)
        )

        # ==================================================
        # DATABASE ERROR
        # ==================================================

        if error:

            st.error(
                f"Unable to add doctor:\n\n{error}"
            )

            return

        # ==================================================
        # SUCCESS NOTIFICATION
        # ==================================================

        full_name = (
            f"{first_name.strip()} "
            f"{last_name.strip()}"
        )

        st.session_state[
            "doctor_notification"
        ] = (
            f"Doctor <strong>{full_name}</strong> "
            f"has been added successfully."
        )

        # ==================================================
        # CLEAR FORM SAFELY
        # ==================================================

        # We do NOT directly modify widget values here.
        #
        # The dialog closes after rerun.
        # When Add Doctor is opened again,
        # the form starts fresh.

        st.session_state[
            "doctor_add_success"
        ] = True

        st.rerun()

    # ======================================================
    # DOCTOR LIST
    # ======================================================

    def show_doctor_list(self):

        doctors, error = self.service.get_all()

        if error:

            st.error(
                f"Unable to load doctors:\n\n{error}"
            )

            return

        if not doctors:

            st.info(
                "No doctors found."
            )

            return

        for doctor in doctors:

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

            full_name = (
                f"{first_name} {last_name}"
            ).strip()

            # ==================================================
            # DOCTOR INFORMATION
            # ==================================================

            col1, col2 = st.columns([7, 2])

            with col1:

                st.subheader(
                    full_name
                )

                st.write(
                    f"**Specialization:** "
                    f"{doctor.get('specialization', 'N/A')}"
                )

                st.write(
                    f"**Email:** "
                    f"{profile.get('email', 'N/A')}"
                )

                st.write(
                    f"**Phone:** "
                    f"{doctor.get('contact_info', 'N/A')}"
                )

            # ==================================================
            # ACTION BUTTONS
            # ==================================================

            with col2:

                st.write("")

                if st.button(
                    "Edit",
                    key=f"edit_{doctor['doctor_id']}",
                    use_container_width=True
                ):

                    self.edit_doctor_modal(
                        doctor
                    )

                if st.button(
                    "Delete",
                    key=f"delete_{doctor['doctor_id']}",
                    use_container_width=True
                ):

                    self.delete_doctor_modal(
                        doctor
                    )

            st.divider()

    # ======================================================
    # EDIT DOCTOR MODAL
    # ======================================================

    @st.dialog("Edit Doctor")
    def edit_doctor_modal(self, doctor):

        profile = (
            doctor.get("profiles")
            or {}
        )

        st.write(
            "Update the doctor's information."
        )

        specialization_options = [
            "Cardiology",
            "Dermatology",
            "Emergency Medicine",
            "Family Medicine",
            "Gastroenterology",
            "General Surgery",
            "Internal Medicine",
            "Neurology",
            "Obstetrics and Gynecology",
            "Oncology",
            "Ophthalmology",
            "Orthopedics",
            "Otolaryngology",
            "Pediatrics",
            "Psychiatry",
            "Radiology",
            "Urology",
            "Other"
        ]

        current_specialization = (
            doctor.get(
                "specialization",
                ""
            )
            or ""
        )

        if (
            current_specialization
            and current_specialization
            not in specialization_options
        ):

            specialization_options.insert(
                0,
                current_specialization
            )

        current_index = 0

        if current_specialization in specialization_options:

            current_index = (
                specialization_options.index(
                    current_specialization
                )
            )

        # ==================================================
        # FORM
        # ==================================================

        with st.form("doctor_edit_form"):

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

                specialization = st.selectbox(
                    "Specialization",
                    specialization_options,
                    index=current_index
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

                contact_info = st.text_input(
                    "Phone Number",
                    value=doctor.get(
                        "contact_info",
                        ""
                    ) or "",
                    placeholder="e.g. 09171234567"
                )

            submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
                use_container_width=True
            )

        # ==================================================
        # WAIT FOR SUBMISSION
        # ==================================================

        if not submitted:
            return

        # ==================================================
        # BASIC VALIDATION
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

        if not specialization:

            st.error(
                "Specialization is required."
            )

            return

        # ==================================================
        # NORMALIZE EMAIL
        # ==================================================

        normalized_email = email.strip().lower()

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

        phone = contact_info.strip()

        if phone:

            if not phone.isdigit():

                st.error(
                    "Phone number must contain numbers only."
                )

                return

        # ==================================================
        # ORIGINAL EMAIL
        # ==================================================

        original_email = (
            profile.get(
                "email",
                ""
            )
            or ""
        ).strip().lower()

        # ==================================================
        # CHECK EMAIL
        # ==================================================

        if normalized_email != original_email:

            email_taken, email_error = (
                self.service.email_exists(
                    normalized_email
                )
            )

            if email_error:

                st.error(
                    f"Unable to verify email:\n\n{email_error}"
                )

                return

            if email_taken:

                st.error(
                    "This email address is already taken. "
                    "Please enter a different email address."
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
        # DOCTOR DATA
        # ==================================================

        doctor_data = {
            "specialization": specialization,
            "contact_info": phone
        }

        # ==================================================
        # UPDATE DATABASE
        # ==================================================

        result, error = self.service.update(
            doctor["doctor_id"],
            doctor["profile_id"],
            profile_data,
            doctor_data
        )

        # ==================================================
        # ERROR
        # ==================================================

        if error:

            st.error(
                f"Unable to update doctor:\n\n{error}"
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
            "doctor_notification"
        ] = (
            f"Doctor <strong>{full_name}</strong> "
            f"has been updated successfully."
        )

        st.rerun()

    # ======================================================
    # DELETE DOCTOR MODAL
    # ======================================================

    @st.dialog("Delete Doctor")
    def delete_doctor_modal(self, doctor):

        profile = (
            doctor.get("profiles")
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
            f"**Dr. {name}**?"
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
                key=f"cancel_{doctor['doctor_id']}",
                use_container_width=True
            ):

                st.rerun()

        # ==================================================
        # DELETE
        # ==================================================

        with col2:

            if st.button(
                "Delete Doctor",
                key=f"confirm_delete_{doctor['doctor_id']}",
                type="primary",
                use_container_width=True
            ):

                success, error = (
                    self.service.delete(
                        doctor["doctor_id"],
                        doctor["profile_id"]
                    )
                )

                # ==========================================
                # ERROR
                # ==========================================

                if error:

                    st.error(
                        f"Unable to delete doctor:\n\n{error}"
                    )

                    return

                # ==========================================
                # SUCCESS
                # ==========================================

                st.session_state[
                    "doctor_notification"
                ] = (
                    f"Doctor <strong>{name}</strong> "
                    f"has been deleted successfully."
                )

                st.rerun()