from models.profile import Profile


class Doctor(Profile):

    def __init__(
        self,
        first_name,
        last_name,
        email,
        password_hash,
        specialization=None,
        contact_info=None,
        id=None,
        profile_id=None,
        doctor_id=None,
        created_at=None
    ):
        super().__init__(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash,
            role="doctor",
            id=id,
            created_at=created_at
        )

        self.profile_id = profile_id
        self.doctor_id = doctor_id
        self.specialization = specialization
        self.contact_info = contact_info

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
            "specialization": self.specialization,
            "contact_info": self.contact_info
        }