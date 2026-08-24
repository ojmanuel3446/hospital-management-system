from config.database import Database
from models.profile import Profile


class ProfileService:

    def __init__(self):
        self.supabase = Database().get_client()

    # CREATE
    def create(self, profile: Profile):
        try:
            response = (
                self.supabase
                .table("profiles")
                .insert(profile.to_dict())
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to create profile."

        except Exception as e:
            return None, str(e)

    # READ ALL
    def get_all(self):
        try:
            response = (
                self.supabase
                .table("profiles")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            return response.data, None

        except Exception as e:
            return None, str(e)

    # READ BY ID
    def get_by_id(self, profile_id):
        try:
            response = (
                self.supabase
                .table("profiles")
                .select("*")
                .eq("id", profile_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Profile not found."

        except Exception as e:
            return None, str(e)

    # UPDATE
    def update(self, profile_id, data):
        try:
            response = (
                self.supabase
                .table("profiles")
                .update(data)
                .eq("id", profile_id)
                .execute()
            )

            if response.data:
                return response.data[0], None

            return None, "Failed to update profile."

        except Exception as e:
            return None, str(e)

    # DELETE
    def delete(self, profile_id):
        try:
            response = (
                self.supabase
                .table("profiles")
                .delete()
                .eq("id", profile_id)
                .execute()
            )

            return True, None

        except Exception as e:
            return False, str(e)