from config.database import Database
from models.diagnosis import Diagnosis


class DiagnosisService:

    def __init__(self):
        self.supabase = Database().get_client()

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(self, diagnosis: Diagnosis):
        try:
            response = (
                self.supabase
                .table("diagnoses")
                .insert(diagnosis.to_dict())
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to create diagnosis."

        except Exception as e:
            return None, str(e)

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all(self):
        try:
            response = (
                self.supabase
                .table("diagnoses")
                .select("""
                    *,
                    appointments (
                        appointment_id,
                        appointment_date,
                        patient_id,
                        doctor_id,
                        status,
                        reason_for_visit,

                        patients (
                            patient_id,
                            profile_id,

                            profiles (
                                id,
                                first_name,
                                last_name,
                                email
                            )
                        ),

                        doctors (
                            doctor_id,
                            profile_id,
                            specialization,

                            profiles (
                                id,
                                first_name,
                                last_name,
                                email
                            )
                        )
                    )
                """)
                .order("created_at", desc=True)
                .execute()
            )

            return response.data or [], None

        except Exception as e:
            return None, str(e)

    # ==========================================================
    # GET FOR LOGGED-IN USER
    #
    # Patient -> own diagnoses
    # Doctor  -> diagnoses from their appointments
    # Admin   -> all diagnoses
    # ==========================================================

    def get_for_user(self, user):
        try:

            if not user:
                return [], "User is not logged in."

            profile_id = user.get("id")
            role = user.get("role")

            if not profile_id:
                return [], "User profile ID is missing."

            if not role:
                return [], "User role is missing."

            role = role.lower()

            # ==================================================
            # ADMIN
            # ==================================================

            if role == "admin":
                return self.get_all()

            # ==================================================
            # PATIENT
            # ==================================================

            if role == "patient":

                response = (
                    self.supabase
                    .table("diagnoses")
                    .select("""
                        *,
                        appointments!inner (
                            appointment_id,
                            appointment_date,
                            patient_id,
                            doctor_id,
                            status,
                            reason_for_visit,

                            patients!inner (
                                patient_id,
                                profile_id,

                                profiles (
                                    id,
                                    first_name,
                                    last_name,
                                    email
                                )
                            ),

                            doctors (
                                doctor_id,
                                profile_id,
                                specialization,

                                profiles (
                                    id,
                                    first_name,
                                    last_name,
                                    email
                                )
                            )
                        )
                    """)
                    .eq(
                        "appointments.patients.profile_id",
                        profile_id
                    )
                    .order(
                        "created_at",
                        desc=True
                    )
                    .execute()
                )

                return response.data or [], None

            # ==================================================
            # DOCTOR
            # ==================================================

            if role == "doctor":

                response = (
                    self.supabase
                    .table("diagnoses")
                    .select("""
                        *,
                        appointments!inner (
                            appointment_id,
                            appointment_date,
                            patient_id,
                            doctor_id,
                            status,
                            reason_for_visit,

                            patients (
                                patient_id,
                                profile_id,

                                profiles (
                                    id,
                                    first_name,
                                    last_name,
                                    email
                                )
                            ),

                            doctors!inner (
                                doctor_id,
                                profile_id,
                                specialization,

                                profiles (
                                    id,
                                    first_name,
                                    last_name,
                                    email
                                )
                            )
                        )
                    """)
                    .eq(
                        "appointments.doctors.profile_id",
                        profile_id
                    )
                    .order(
                        "created_at",
                        desc=True
                    )
                    .execute()
                )

                return response.data or [], None

            return [], f"Unsupported role: {role}"

        except Exception as e:
            return None, str(e)

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(self, diagnosis_id):
        try:

            response = (
                self.supabase
                .table("diagnoses")
                .select("""
                    *,
                    appointments (
                        appointment_id,
                        appointment_date,
                        patient_id,
                        doctor_id,
                        status,
                        reason_for_visit,

                        patients (
                            patient_id,
                            profile_id,

                            profiles (
                                id,
                                first_name,
                                last_name,
                                email
                            )
                        ),

                        doctors (
                            doctor_id,
                            profile_id,
                            specialization,

                            profiles (
                                id,
                                first_name,
                                last_name,
                                email
                            )
                        )
                    )
                """)
                .eq(
                    "diagnosis_id",
                    diagnosis_id
                )
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Diagnosis not found."

        except Exception as e:
            return None, str(e)

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(self, diagnosis_id, data):
        try:

            response = (
                self.supabase
                .table("diagnoses")
                .update(data)
                .eq(
                    "diagnosis_id",
                    diagnosis_id
                )
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to update diagnosis."

        except Exception as e:
            return None, str(e)

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(self, diagnosis_id):
        try:

            (
                self.supabase
                .table("diagnoses")
                .delete()
                .eq(
                    "diagnosis_id",
                    diagnosis_id
                )
                .execute()
            )

            return True, None

        except Exception as e:
            return False, str(e)