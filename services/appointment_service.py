from config.database import Database
from models.appointment import Appointment


class AppointmentService:

    def __init__(self):
        self.supabase = Database().get_client()

    # CREATE
    def create(self, appointment: Appointment):
        try:
            response = (
                self.supabase
                .table("appointments")
                .insert(appointment.to_dict())
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to create appointment."

        except Exception as e:
            return None, str(e)

    # READ ALL
    def get_all(self):
        try:
            response = (
                self.supabase
                .table("appointments")
                .select("""
                    *,
                    patients (
                        patient_id,
                        profiles (
                            first_name,
                            last_name
                        )
                    ),
                    doctors (
                        doctor_id,
                        specialization,
                        profiles (
                            first_name,
                            last_name
                        )
                    )
                """)
                .order("appointment_date", desc=True)
                .execute()
            )

            return response.data, None

        except Exception as e:
            return None, str(e)

    # READ BY ID
    def get_by_id(self, appointment_id):
        try:
            response = (
                self.supabase
                .table("appointments")
                .select("*")
                .eq("appointment_id", appointment_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Appointment not found."

        except Exception as e:
            return None, str(e)

    # UPDATE
    def update(self, appointment_id, data):
        try:
            response = (
                self.supabase
                .table("appointments")
                .update(data)
                .eq("appointment_id", appointment_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to update appointment."

        except Exception as e:
            return None, str(e)

    # DELETE
    def delete(self, appointment_id):
        try:
            self.supabase.table(
                "appointments"
            ).delete().eq(
                "appointment_id", appointment_id
            ).execute()

            return True, None

        except Exception as e:
            return False, str(e)