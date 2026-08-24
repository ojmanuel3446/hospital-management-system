from models.base_model import BaseModel


class Appointment(BaseModel):

    def __init__(
        self,
        patient_id,
        doctor_id,
        appointment_date,
        status=None,
        reason_for_visit=None,
        appointment_id=None,
        created_at=None
    ):
        super().__init__(created_at)

        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.status = status
        self.reason_for_visit = reason_for_visit

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "appointment_date": str(self.appointment_date),
            "status": self.status,
            "reason_for_visit": self.reason_for_visit
        }