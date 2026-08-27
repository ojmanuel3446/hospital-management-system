import streamlit as st
import bcrypt
import re

from config.database import Database


class ProfilePage:

    def __init__(self):
        self.supabase = Database().get_client()

    # ======================================================
    # MAIN PAGE
    # ======================================================

    def show(self):

        st.title("My Profile")

        user = st.session_state.get("user", {})
        role = st.session_state.get("role", "").lower()

        profile_id = (
            user.get("profile_id")
            or user.get("id")
        )

        if not profile_id:
            st.error(
                "Unable to identify your profile. "
                "Please log out and log in again."
            )
            return

        # ==================================================
        # LOAD PROFILE
        # ==================================================

        profile, error = self.get_profile(
            profile_id,
            role
        )

        if error:
            st.error(
                f"Unable to load profile:\n\n{error}"
            )
            return

        if not profile:
            st.warning(
                "Profile information not found."
            )
            return

        # ==================================================
        # HEADER
        # ==================================================

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

        st.markdown(
            f"{full_name}"
        )

        st.caption(
            f"{role.capitalize()} Account"
        )

        st.divider()

        # ==================================================
        # PERSONAL INFORMATION
        # ==================================================

        st.subheader(
            "Personal Information"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.text_input(
                "First Name",
                value=first_name,
                disabled=True
            )

        with col2:

            st.text_input(
                "Last Name",
                value=last_name,
                disabled=True
            )

        st.text_input(
            "Email",
            value=profile.get(
                "email",
                ""
            ),
            disabled=True
        )

        st.caption(
            "Your name and email are managed by the hospital administrator."
        )

        # ==================================================
        # DOCTOR PROFILE
        # ==================================================

        if role == "doctor":

            self.show_doctor_profile(
                profile,
                profile_id
            )

        # ==================================================
        # PATIENT PROFILE
        # ==================================================

        elif role == "patient":

            self.show_patient_profile(
                profile,
                profile_id
            )

        # ==================================================
        # SECURITY
        # ==================================================

        self.show_security()

    # ======================================================
    # DOCTOR PROFILE
    # ======================================================

    def show_doctor_profile(
        self,
        profile,
        profile_id
    ):

        st.divider()

        st.subheader(
            "Professional Information"
        )

        st.text_input(
            "Specialization",
            value=profile.get(
                "specialization",
                "N/A"
            ),
            disabled=True
        )

        st.caption(
            "Your specialization is managed by the hospital administrator."
        )

        # ==================================================
        # CONTACT INFORMATION
        # ==================================================

        st.divider()

        st.subheader(
            "Contact Information"
        )

        st.info(
            "You can update your phone number. "
            "Only numbers are allowed."
        )

        with st.form(
            "doctor_phone_form"
        ):

            phone = st.text_input(
                "Phone Number",
                value=profile.get(
                    "contact_info",
                    ""
                ) or "",
                placeholder="Enter your phone number"
            )

            submitted = st.form_submit_button(
                "Save Phone Number",
                type="primary",
                use_container_width=True
            )

        if submitted:

            phone = phone.strip()

            # ==============================================
            # PHONE VALIDATION
            # ==============================================

            valid, message = self.validate_phone(
                phone
            )

            if not valid:

                st.error(message)

                return

            # ==============================================
            # UPDATE DOCTOR
            # ==============================================

            success, error = self.update_doctor_phone(
                profile_id,
                phone
            )

            if error:

                st.error(
                    f"Unable to update phone number:\n\n{error}"
                )

            else:

                st.success(
                    "Phone number updated successfully."
                )

                st.rerun()

    # ======================================================
    # PATIENT PROFILE
    # ======================================================

    def show_patient_profile(
        self,
        profile,
        profile_id
    ):

        st.divider()

        st.subheader(
            "Patient Information"
        )

        # ==================================================
        # DATE OF BIRTH
        # ==================================================

        date_of_birth = profile.get(
            "date_of_birth"
        )

        if date_of_birth:

            st.text_input(
                "Date of Birth",
                value=str(date_of_birth),
                disabled=True
            )

        # ==================================================
        # MEDICAL HISTORY
        # ==================================================

        medical_history = profile.get(
            "medical_history"
        )

        if medical_history:

            st.text_area(
                "Medical History",
                value=str(medical_history),
                disabled=True,
                height=120
            )

        st.caption(
            "Medical information is managed by authorized hospital personnel."
        )

        # ==================================================
        # CONTACT INFORMATION
        # ==================================================

        st.divider()

        st.subheader(
            "Contact Information"
        )

        with st.form(
            "patient_contact_form"
        ):

            phone = st.text_input(
                "Phone Number",
                value=profile.get(
                    "phone",
                    ""
                ) or "",
                placeholder="Enter your phone number"
            )

            address = st.text_area(
                "Address",
                value=profile.get(
                    "address",
                    ""
                ) or "",
                height=100,
                placeholder="Enter your address"
            )

            submitted = st.form_submit_button(
                "Save Contact Information",
                type="primary",
                use_container_width=True
            )

        if submitted:

            phone = phone.strip()
            address = address.strip()

            # ==============================================
            # PHONE VALIDATION
            # ==============================================

            valid, message = self.validate_phone(
                phone
            )

            if not valid:

                st.error(message)

                return

            # ==============================================
            # ADDRESS VALIDATION
            # ==============================================

            if not address:

                st.error(
                    "Please enter your address."
                )

                return

            # ==============================================
            # UPDATE PATIENT
            # ==============================================

            success, error = self.update_patient_contact(
                profile_id,
                phone,
                address
            )

            if error:

                st.error(
                    f"Unable to update contact information:\n\n{error}"
                )

            else:

                st.success(
                    "Contact information updated successfully."
                )

                st.rerun()

    # ======================================================
    # PHONE VALIDATION
    # ======================================================

    def validate_phone(
        self,
        phone
    ):

        # Remove leading/trailing spaces
        phone = phone.strip()

        # ==================================================
        # EMPTY
        # ==================================================

        if not phone:

            return False, (
                "Please enter your phone number."
            )

        # ==================================================
        # NUMBERS ONLY
        # ==================================================

        if not re.fullmatch(
            r"[0-9]+",
            phone
        ):

            return False, (
                "Phone number must contain numbers only. "
                "Do not use letters, spaces, dashes, or symbols."
            )

        # ==================================================
        # MINIMUM LENGTH
        # ==================================================

        if len(phone) < 10:

            return False, (
                "Phone number must contain at least 10 digits."
            )

        # ==================================================
        # MAXIMUM LENGTH
        # ==================================================

        if len(phone) > 15:

            return False, (
                "Phone number must not exceed 15 digits."
            )

        return True, None

    # ======================================================
    # GET PROFILE
    # ======================================================

    def get_profile(
        self,
        profile_id,
        role
    ):

        try:

            # ==================================================
            # PROFILE
            # ==================================================

            profile_response = (
                self.supabase
                .table("profiles")
                .select(
                    """
                    id,
                    first_name,
                    last_name,
                    email,
                    role
                    """
                )
                .eq(
                    "id",
                    profile_id
                )
                .single()
                .execute()
            )

            profile = profile_response.data

            if not profile:

                return None, "Profile not found."

            # ==================================================
            # DOCTOR
            # ==================================================

            if role == "doctor":

                doctor_response = (
                    self.supabase
                    .table("doctors")
                    .select(
                        """
                        doctor_id,
                        specialization,
                        contact_info,
                        created_at
                        """
                    )
                    .eq(
                        "profile_id",
                        profile_id
                    )
                    .single()
                    .execute()
                )

                doctor = doctor_response.data

                if doctor:

                    profile.update(
                        doctor
                    )

            # ==================================================
            # PATIENT
            # ==================================================

            elif role == "patient":

                patient_response = (
                    self.supabase
                    .table("patients")
                    .select(
                        """
                        patient_id,
                        address,
                        phone,
                        date_of_birth,
                        medical_history,
                        created_at
                        """
                    )
                    .eq(
                        "profile_id",
                        profile_id
                    )
                    .single()
                    .execute()
                )

                patient = patient_response.data

                if patient:

                    profile.update(
                        patient
                    )

            return profile, None

        except Exception as e:

            return None, str(e)

    # ======================================================
    # UPDATE DOCTOR PHONE
    # ======================================================

    def update_doctor_phone(
        self,
        profile_id,
        phone
    ):

        try:

            response = (
                self.supabase
                .table("doctors")
                .update(
                    {
                        "contact_info": phone
                    }
                )
                .eq(
                    "profile_id",
                    profile_id
                )
                .execute()
            )

            if not response.data:

                return False, (
                    "No doctor record was updated."
                )

            return True, None

        except Exception as e:

            return False, str(e)

    # ======================================================
    # UPDATE PATIENT CONTACT
    # ======================================================

    def update_patient_contact(
        self,
        profile_id,
        phone,
        address
    ):

        try:

            response = (
                self.supabase
                .table("patients")
                .update(
                    {
                        "phone": phone,
                        "address": address
                    }
                )
                .eq(
                    "profile_id",
                    profile_id
                )
                .execute()
            )

            if not response.data:

                return False, (
                    "No patient record was updated."
                )

            return True, None

        except Exception as e:

            return False, str(e)

    # ======================================================
    # SECURITY
    # ======================================================

    def show_security(self):

        st.divider()

        st.subheader(
            "Security"
        )

        st.write(
            "Change your account password."
        )

        with st.form(
            "change_password_form"
        ):

            current_password = st.text_input(
                "Current Password",
                type="password"
            )

            new_password = st.text_input(
                "New Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm New Password",
                type="password"
            )

            password_submitted = st.form_submit_button(
                "Change Password",
                type="primary",
                use_container_width=True
            )

        if password_submitted:

            self.change_password(
                current_password,
                new_password,
                confirm_password
            )

    # ======================================================
    # CHANGE PASSWORD
    # ======================================================

    def change_password(
        self,
        current_password,
        new_password,
        confirm_password
    ):

        # ==================================================
        # VALIDATION
        # ==================================================

        if not current_password:

            st.error(
                "Please enter your current password."
            )

            return

        if not new_password:

            st.error(
                "Please enter a new password."
            )

            return

        if len(new_password) < 6:

            st.error(
                "New password must be at least 6 characters."
            )

            return

        if new_password != confirm_password:

            st.error(
                "New passwords do not match."
            )

            return

        if current_password == new_password:

            st.error(
                "New password must be different from your current password."
            )

            return

        # ==================================================
        # GET LOGGED-IN PROFILE
        # ==================================================

        user = st.session_state.get(
            "user",
            {}
        )

        profile_id = (
            user.get("profile_id")
            or user.get("id")
        )

        if not profile_id:

            st.error(
                "Unable to identify your profile."
            )

            return

        try:

            # ==================================================
            # GET STORED PASSWORD HASH
            # ==================================================

            response = (
                self.supabase
                .table("profiles")
                .select(
                    "password_hash"
                )
                .eq(
                    "id",
                    profile_id
                )
                .single()
                .execute()
            )

            profile = response.data

            if not profile:

                st.error(
                    "Profile not found."
                )

                return

            stored_hash = profile.get(
                "password_hash"
            )

            if not stored_hash:

                st.error(
                    "No password hash found for this account."
                )

                return

            # ==================================================
            # VERIFY CURRENT PASSWORD
            # ==================================================

            try:

                valid_password = bcrypt.checkpw(
                    current_password.encode("utf-8"),
                    stored_hash.encode("utf-8")
                )

            except ValueError:

                st.error(
                    "The stored password is not a valid bcrypt password."
                )

                return

            if not valid_password:

                st.error(
                    "Current password is incorrect."
                )

                return

            # ==================================================
            # HASH NEW PASSWORD
            # ==================================================

            new_password_hash = bcrypt.hashpw(
                new_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # ==================================================
            # UPDATE DATABASE
            # ==================================================

            update_response = (
                self.supabase
                .table("profiles")
                .update(
                    {
                        "password_hash": new_password_hash
                    }
                )
                .eq(
                    "id",
                    profile_id
                )
                .execute()
            )

            if not update_response.data:

                st.error(
                    "Unable to update password."
                )

                return

            st.success(
                "Password changed successfully."
            )

            st.info(
                "Your new password is now active."
            )

        except Exception as e:

            st.error(
                f"Unable to change password:\n\n{e}"
            )