from models.profile import Profile


class Patient(Profile):

    def __init__(
        self,
        first_name,
        last_name,
        email,
        password_hash,
        address=None,
        phone=None,
        date_of_birth=None,
        medical_history=None,
        id=None,
        profile_id=None,
        patient_id=None,
        created_at=None
    ):
        super().__init__(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role="patient",
            id=id,
            created_at=created_at
        )

        self.profile_id = profile_id
        self.patient_id = patient_id
        self.address = address
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.medical_history = medical_history

    def to_profile_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role
        }

    def to_dict(self):
        return {
            "profile_id": self.profile_id,
            "address": self.address,
            "phone": self.phone,
            "date_of_birth": (
                str(self.date_of_birth)
                if self.date_of_birth
                else None
            ),
            "medical_history": self.medical_history
        }