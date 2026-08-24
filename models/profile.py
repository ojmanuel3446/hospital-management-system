from models.base_model import BaseModel


class Profile(BaseModel):

    def __init__(
        self,
        first_name,
        last_name,
        email,
        password_hash,
        role,
        id=None,
        created_at=None
    ):
        super().__init__(created_at)

        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.role = role

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password_hash": self.password_hash,
            "role": self.role
        }