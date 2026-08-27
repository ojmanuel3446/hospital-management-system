import bcrypt

from config.database import Database
from models.patient import Patient


class PatientService:

    def __init__(self):
        self.supabase = Database().get_client()

    # ======================================================
    # EMAIL VALIDATION
    # ======================================================

    def email_exists(self, email, exclude_profile_id=None):
        """
        Check whether an email is already registered.

        When exclude_profile_id is provided, that profile is ignored.
        This allows a patient to keep their existing email while editing.
        """
        try:
            email = email.strip().lower()

            query = (
                self.supabase
                .table("profiles")
                .select("id")
                .ilike("email", email)
            )

            if exclude_profile_id:
                query = query.neq(
                    "id",
                    exclude_profile_id
                )

            response = query.execute()

            return bool(response.data), None

        except Exception as e:
            return False, str(e)

    # ======================================================
    # CREATE
    # ======================================================

    def create(self, patient: Patient):
        try:
            # ==================================================
            # CHECK EMAIL
            # ==================================================

            email_exists, email_error = self.email_exists(
                patient.email
            )

            if email_error:
                return None, (
                    "Unable to verify the email address.\n\n"
                    f"{email_error}"
                )

            if email_exists:
                return None, (
                    "This email address is already registered. "
                    "Please use a different email address."
                )

            # ==================================================
            # HASH PASSWORD
            # ==================================================

            password_hash = bcrypt.hashpw(
                patient.password_hash.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # ==================================================
            # CREATE PROFILE
            # ==================================================

            profile_data = patient.to_profile_dict()

            # Normalize email
            profile_data["email"] = (
                patient.email.strip().lower()
            )

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
                    "Failed to create patient profile."
                )

            profile = profile_response.data[0]

            # Save generated profile ID
            patient.profile_id = profile["id"]

            # ==================================================
            # CREATE PATIENT RECORD
            # ==================================================

            patient_response = (
                self.supabase
                .table("patients")
                .insert(patient.to_dict())
                .execute()
            )

            if patient_response.data:
                return patient_response.data[0], None

            return None, "Failed to create patient."

        except Exception as e:

            # Handle database UNIQUE constraint as an
            # additional layer of protection.
            error_message = str(e)

            if (
                "duplicate key" in error_message.lower()
                or "unique constraint" in error_message.lower()
                or "profiles_email_key" in error_message.lower()
            ):
                return None, (
                    "This email address is already registered. "
                    "Please use a different email address."
                )

            return None, error_message

    # ======================================================
    # READ ALL
    # ======================================================

    def get_all(self):
        try:
            response = (
                self.supabase
                .table("patients")
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
                .order("created_at", desc=True)
                .execute()
            )

            return response.data, None

        except Exception as e:
            return None, str(e)

    # ======================================================
    # READ BY ID
    # ======================================================

    def get_by_id(self, patient_id):
        try:
            response = (
                self.supabase
                .table("patients")
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
                .eq("patient_id", patient_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Patient not found."

        except Exception as e:
            return None, str(e)

    # ======================================================
    # COMPLETE MEDICAL RECORD
    # ======================================================

    def get_medical_record(self, patient_id):
        try:
            response = (
                self.supabase
                .table("patients")
                .select("""
                    *,
                    profiles (
                        id,
                        first_name,
                        last_name,
                        email,
                        role
                    ),
                    appointments (
                        appointment_id,
                        appointment_date,
                        status,
                        reason_for_visit,
                        doctors (
                            doctor_id,
                            specialization,
                            profiles (
                                first_name,
                                last_name
                            )
                        ),
                        diagnoses (
                            diagnosis_id,
                            diagnosis_description,
                            treatment_plan,
                            created_at
                        )
                    )
                """)
                .eq("patient_id", patient_id)
                .single()
                .execute()
            )

            if response.data:
                return response.data, None

            return None, "Medical record not found."

        except Exception as e:
            return None, str(e)

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        patient_id,
        profile_id,
        profile_data,
        patient_data
    ):
        try:
            # ==================================================
            # CHECK EMAIL
            # ==================================================

            email = (
                profile_data.get("email", "")
                .strip()
                .lower()
            )

            if not email:
                return None, "Email is required."

            email_exists, email_error = self.email_exists(
                email,
                exclude_profile_id=profile_id
            )

            if email_error:
                return None, (
                    "Unable to verify the email address.\n\n"
                    f"{email_error}"
                )

            if email_exists:
                return None, (
                    "This email address is already registered "
                    "to another account. "
                    "Please use a different email address."
                )

            # Normalize email before saving
            profile_data["email"] = email

            # ==================================================
            # UPDATE PROFILE
            # ==================================================

            profile_response = (
                self.supabase
                .table("profiles")
                .update(profile_data)
                .eq("id", profile_id)
                .execute()
            )

            # ==================================================
            # UPDATE PATIENT
            # ==================================================

            response = (
                self.supabase
                .table("patients")
                .update(patient_data)
                .eq("patient_id", patient_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to update patient."

        except Exception as e:

            error_message = str(e)

            if (
                "duplicate key" in error_message.lower()
                or "unique constraint" in error_message.lower()
                or "profiles_email_key" in error_message.lower()
            ):
                return None, (
                    "This email address is already registered. "
                    "Please use a different email address."
                )

            return None, error_message

    # ======================================================
    # DELETE
    # ======================================================

    def delete(self, patient_id, profile_id):
        try:
            # ==================================================
            # DELETE PATIENT
            # ==================================================

            self.supabase \
                .table("patients") \
                .delete() \
                .eq("patient_id", patient_id) \
                .execute()

            # ==================================================
            # DELETE PROFILE
            # ==================================================

            self.supabase \
                .table("profiles") \
                .delete() \
                .eq("id", profile_id) \
                .execute()

            return True, None

        except Exception as e:
            return False, str(e)