from models.base_model import BaseModel


class Diagnosis(BaseModel):

    def __init__(
        self,
        appointment_id,
        diagnosis_description,
        treatment_plan=None,
        diagnosis_id=None,
        created_at=None
    ):
        super().__init__(created_at)

        self.diagnosis_id = diagnosis_id
        self.appointment_id = appointment_id
        self.diagnosis_description = diagnosis_description
        self.treatment_plan = treatment_plan

    def to_dict(self):
        return {
            "appointment_id": self.appointment_id,
            "diagnosis_description": self.diagnosis_description,
            "treatment_plan": self.treatment_plan
        }