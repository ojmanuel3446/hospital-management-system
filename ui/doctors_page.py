import streamlit as st

from models.doctor import Doctor
from services.doctor_service import DoctorService


class DoctorsPage:

    def __init__(self):
        self.service = DoctorService()

    def show(self):

        st.title("Doctors")

        # ==================================================
        # SHOW SUCCESS NOTIFICATION
        # ==================================================

        self.show_notification()

        # ==================================================
        # ADD DOCTOR BUTTON
        # ==================================================

        if st.button(
            "Add Doctor",
            type="primary",
            key="add_doctor_button"
        ):
            self.add_doctor_modal()

        st.divider()

        # ==================================================
        # DOCTOR LIST
        # ==================================================

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
            key="notification_ok"
        ):

            st.session_state[
                "doctor_notification"
            ] = None

            st.rerun()

    # ======================================================
    # SHOW NOTIFICATION
    # ======================================================

    def show_notification(self):

        message = st.session_state.get(
            "doctor_notification"
        )

        if message:

            self.notification_modal(
                message
            )

    # ======================================================
    # ADD DOCTOR MODAL
    # ======================================================

    @st.dialog("Add Doctor")
    def add_doctor_modal(self):

        st.subheader(
            "Create New Doctor"
        )

        with st.form(
            "doctor_add_form",
            clear_on_submit=True
        ):

            col1, col2 = st.columns(2)

            with col1:

                first_name = st.text_input(
                    "First Name"
                )

                email = st.text_input(
                    "Email"
                )

                specialization = st.text_input(
                    "Specialization"
                )

            with col2:

                last_name = st.text_input(
                    "Last Name"
                )

                password = st.text_input(
                    "Password",
                    type="password"
                )

                contact_info = st.text_input(
                    "Contact Information"
                )

            submitted = st.form_submit_button(
                "Create Doctor",
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

        if not password:

            st.error(
                "Password is required."
            )
            return

        if not specialization.strip():

            st.error(
                "Specialization is required."
            )
            return

        # ==================================================
        # CREATE DOCTOR OBJECT
        # ==================================================

        doctor = Doctor(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email.strip(),
            password_hash=password,
            specialization=specialization.strip(),
            contact_info=contact_info.strip()
        )

        # ==================================================
        # DATABASE
        # ==================================================

        created_doctor, error = (
            self.service.create(doctor)
        )

        # ==================================================
        # ERROR
        # ==================================================

        if error:

            st.error(
                f"Unable to add doctor:\n\n{error}"
            )

            return

        # ==================================================
        # SUCCESS NOTIFICATION
        # ==================================================

        st.session_state[
            "doctor_notification"
        ] = (
            f"Doctor <strong>"
            f"{first_name.strip()} "
            f"{last_name.strip()}"
            f"</strong> has been added successfully."
        )

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

            profile = doctor.get(
                "profiles"
            ) or {}

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

            col1, col2 = st.columns(
                [7, 2]
            )

            with col1:

                st.subheader(
                    f"{full_name}"
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
                    f"**Contact:** "
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

        profile = doctor.get(
            "profiles"
        ) or {}

        st.write(
            "Update the doctor's information."
        )

        with st.form(
            "doctor_edit_form"
        ):

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

                specialization = st.text_input(
                    "Specialization",
                    value=doctor.get(
                        "specialization",
                        ""
                    )
                )

            with col2:

                last_name = st.text_input(
                    "Last Name",
                    value=profile.get(
                        "last_name",
                        ""
                    )
                )

                contact_info = st.text_input(
                    "Contact Information",
                    value=doctor.get(
                        "contact_info",
                        ""
                    )
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

        if not specialization.strip():

            st.error(
                "Specialization is required."
            )
            return

        # ==================================================
        # UPDATE DATA
        # ==================================================

        profile_data = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip()
        }

        doctor_data = {
            "specialization": specialization.strip(),
            "contact_info": contact_info.strip()
        }

        result, error = (
            self.service.update(
                doctor["doctor_id"],
                doctor["profile_id"],
                profile_data,
                doctor_data
            )
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

        st.session_state[
            "doctor_notification"
        ] = (
            f"Doctor <strong>"
            f"{first_name.strip()} "
            f"{last_name.strip()}"
            f"</strong> has been updated successfully."
        )

        st.rerun()

    # ======================================================
    # DELETE DOCTOR MODAL
    # ======================================================

    @st.dialog("Delete Doctor")
    def delete_doctor_modal(self, doctor):

        profile = doctor.get(
            "profiles"
        ) or {}

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
                    f"Doctor <strong>"
                    f"{name}"
                    f"</strong> has been deleted successfully."
                )

                st.rerun()