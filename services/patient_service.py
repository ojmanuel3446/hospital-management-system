import bcrypt

from config.database import Database
from models.patient import Patient


class PatientService:

    def __init__(self):
        self.supabase = Database().get_client()

    # ======================================================
    # CREATE
    # ======================================================

    def create(self, patient: Patient):
        try:
            # ==================================================
            # HASH PASSWORD
            # Same method used by DoctorService
            # ==================================================

            password_hash = bcrypt.hashpw(
                patient.password_hash.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # ==================================================
            # CREATE PROFILE
            # ==================================================

            profile_data = patient.to_profile_dict()

            # Replace plain password with bcrypt hash
            profile_data["password_hash"] = password_hash

            profile_response = (
                self.supabase
                .table("profiles")
                .insert(profile_data)
                .execute()
            )

            if not profile_response.data:
                return None, "Failed to create patient profile."

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
            return None, str(e)

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
            # UPDATE PROFILE
            # ==================================================

            self.supabase \
                .table("profiles") \
                .update(profile_data) \
                .eq("id", profile_id) \
                .execute()

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
            return None, str(e)

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