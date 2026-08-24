class BaseModel:
    def __init__(self, created_at=None):
        self.created_at = created_at

    def to_dict(self):
        raise NotImplementedError(
            "Each model must implement its own to_dict() method."
        )