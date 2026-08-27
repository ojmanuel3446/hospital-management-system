import bcrypt

from config.database import Database
from models.doctor import Doctor


class DoctorService:

    def __init__(self):
        self.supabase = Database().get_client()

    # ======================================================
    # EMAIL VALIDATION
    # ======================================================

    def email_exists(self, email):
        try:
            normalized_email = email.strip().lower()

            response = (
                self.supabase
                .table("profiles")
                .select("id")
                .eq("email", normalized_email)
                .limit(1)
                .execute()
            )

            return bool(response.data), None

        except Exception as e:
            return False, str(e)

    # ======================================================
    # CREATE
    # ======================================================

    def create(self, doctor: Doctor):
        try:

            # ==================================================
            # CHECK EMAIL BEFORE CREATING PROFILE
            # ==================================================

            normalized_email = (
                doctor.email.strip().lower()
            )

            email_taken, email_error = (
                self.email_exists(
                    normalized_email
                )
            )

            if email_error:
                return None, (
                    f"Unable to verify email: "
                    f"{email_error}"
                )

            if email_taken:
                return None, (
                    "This email address is already taken. "
                    "Please enter a different email address."
                )

            # ==================================================
            # HASH PASSWORD
            # ==================================================

            password_hash = bcrypt.hashpw(
                doctor.password_hash.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # ==================================================
            # CREATE PROFILE
            # ==================================================

            profile_data = doctor.to_profile_dict()

            # Make sure email is normalized
            profile_data["email"] = normalized_email

            # Replace plain password with bcrypt hash
            profile_data["password_hash"] = password_hash

            profile_response = (
                self.supabase
                .table("profiles")
                .insert(profile_data)
                .execute()
            )

            if not profile_response.data:
                return None, (
                    "Failed to create doctor profile."
                )

            profile = profile_response.data[0]

            # ==================================================
            # SAVE GENERATED PROFILE ID
            # ==================================================

            doctor.profile_id = profile["id"]

            # ==================================================
            # CREATE DOCTOR RECORD
            # ==================================================

            doctor_response = (
                self.supabase
                .table("doctors")
                .insert(
                    doctor.to_dict()
                )
                .execute()
            )

            if doctor_response.data:
                return doctor_response.data[0], None

            # ==================================================
            # DOCTOR CREATION FAILED
            # ==================================================

            return None, "Failed to create doctor."

        except Exception as e:

            error_message = str(e)

            # ==================================================
            # HANDLE DATABASE UNIQUE EMAIL ERROR
            # ==================================================

            if (
                "duplicate key" in error_message.lower()
                or "unique constraint" in error_message.lower()
                or "profiles_email_key" in error_message.lower()
            ):
                return None, (
                    "This email address is already taken. "
                    "Please enter a different email address."
                )

            return None, error_message

    # ======================================================
    # READ ALL
    # ======================================================

    def get_all(self):
        try:

            response = (
                self.supabase
                .table("doctors")
                .select("""
                    *,
                    profiles (
                        id,
                        first_name,
                        last_name,
                        email,
                        role
                    )
                """)
                .order(
                    "created_at",
                    desc=True
                )
                .execute()
            )

            return response.data, None

        except Exception as e:

            return None, str(e)

    # ======================================================
    # READ BY ID
    # ======================================================

    def get_by_id(self, doctor_id):
        try:

            response = (
                self.supabase
                .table("doctors")
                .select("""
                    *,
                    profiles (
                        id,
                        first_name,
                        last_name,
                        email,
                        role
                    )
                """)
                .eq(
                    "doctor_id",
                    doctor_id
                )
                .execute()
            )

            if response.data:

                return response.data[0], None

            return None, "Doctor not found."

        except Exception as e:

            return None, str(e)

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        doctor_id,
        profile_id,
        profile_data,
        doctor_data
    ):
        try:

            # ==================================================
            # NORMALIZE EMAIL
            # ==================================================

            if "email" in profile_data:

                normalized_email = (
                    profile_data["email"]
                    .strip()
                    .lower()
                )

                profile_data["email"] = (
                    normalized_email
                )

                # ==================================================
                # CHECK WHETHER EMAIL BELONGS TO SOMEONE ELSE
                # ==================================================

                response = (
                    self.supabase
                    .table("profiles")
                    .select("id")
                    .eq(
                        "email",
                        normalized_email
                    )
                    .neq(
                        "id",
                        profile_id
                    )
                    .limit(1)
                    .execute()
                )

                if response.data:

                    return None, (
                        "This email address is already taken. "
                        "Please enter a different email address."
                    )

            # ==================================================
            # UPDATE PROFILE
            # ==================================================

            profile_response = (
                self.supabase
                .table("profiles")
                .update(profile_data)
                .eq(
                    "id",
                    profile_id
                )
                .execute()
            )

            # ==================================================
            # UPDATE DOCTOR
            # ==================================================

            doctor_response = (
                self.supabase
                .table("doctors")
                .update(doctor_data)
                .eq(
                    "doctor_id",
                    doctor_id
                )
                .execute()
            )

            if doctor_response.data:

                return (
                    doctor_response.data[0],
                    None
                )

            return None, "Failed to update doctor."

        except Exception as e:

            error_message = str(e)

            # ==================================================
            # HANDLE DATABASE UNIQUE EMAIL ERROR
            # ==================================================

            if (
                "duplicate key" in error_message.lower()
                or "unique constraint" in error_message.lower()
                or "profiles_email_key" in error_message.lower()
            ):
                return None, (
                    "This email address is already taken. "
                    "Please enter a different email address."
                )

            return None, error_message

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        doctor_id,
        profile_id
    ):
        try:

            # ==================================================
            # DELETE DOCTOR FIRST
            # ==================================================

            self.supabase \
                .table("doctors") \
                .delete() \
                .eq(
                    "doctor_id",
                    doctor_id
                ) \
                .execute()

            # ==================================================
            # DELETE PROFILE
            # ==================================================

            self.supabase \
                .table("profiles") \
                .delete() \
                .eq(
                    "id",
                    profile_id
                ) \
                .execute()

            return True, None

        except Exception as e:

            return False, str(e)