import bcrypt

from config.database import Database
from models.doctor import Doctor


class DoctorService:

    def __init__(self):
        self.supabase = Database().get_client()

    # CREATE
    def create(self, doctor: Doctor):
        try:
            password_hash = bcrypt.hashpw(
                doctor.password_hash.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            profile_data = doctor.to_profile_dict()
            profile_data["password_hash"] = password_hash

            profile_response = (
                self.supabase
                .table("profiles")
                .insert(profile_data)
                .execute()
            )

            if not profile_response.data:
                return None, "Failed to create doctor profile."

            profile = profile_response.data[0]

            # 2. Save generated profile ID
            doctor.profile_id = profile["id"]

            # 3. Create doctor record
            doctor_response = (
                self.supabase
                .table("doctors")
                .insert(doctor.to_dict())
                .execute()
            )

            if doctor_response.data:
                return doctor_response.data[0], None

            return None, "Failed to create doctor."

        except Exception as e:
            return None, str(e)

    # READ ALL
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
                .order("created_at", desc=True)
                .execute()
            )

            return response.data, None

        except Exception as e:
            return None, str(e)

    # READ BY ID
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
                .eq("doctor_id", doctor_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Doctor not found."

        except Exception as e:
            return None, str(e)

    # UPDATE
    def update(self, doctor_id, profile_id, profile_data, doctor_data):
        try:
            # Update profile information
            self.supabase.table("profiles").update(
                profile_data
            ).eq(
                "id", profile_id
            ).execute()

            # Update doctor information
            response = (
                self.supabase
                .table("doctors")
                .update(doctor_data)
                .eq("doctor_id", doctor_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to update doctor."

        except Exception as e:
            return None, str(e)

    # DELETE
    def delete(self, doctor_id, profile_id):
        try:
            # Delete doctor first
            self.supabase.table("doctors").delete().eq(
                "doctor_id", doctor_id
            ).execute()

            # Then delete profile
            self.supabase.table("profiles").delete().eq(
                "id", profile_id
            ).execute()

            return True, None

        except Exception as e:
            return False, str(e)