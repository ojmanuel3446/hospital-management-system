import bcrypt

from config.database import Database


class AuthService:

    def __init__(self):

        self.supabase = Database().get_client()

    # ======================================================
    # LOGIN
    # ======================================================

    def login(self, email, password):

        try:

            response = (
                self.supabase
                .table("profiles")
                .select("*")
                .eq("email", email.strip())
                .limit(1)
                .execute()
            )

            if not response.data:
                return None, "Invalid email or password."

            profile = response.data[0]

            password_hash = profile.get("password_hash")

            if not password_hash:
                return None, "Password is not configured."

            password_matches = bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8")
            )

            if not password_matches:
                return None, "Invalid email or password."

            return profile, None

        except Exception as e:

            return None, str(e)

    # ======================================================
    # GET USER BY ID
    # Used to restore login after browser refresh
    # ======================================================

    def get_user_by_id(self, profile_id):

        try:

            response = (
                self.supabase
                .table("profiles")
                .select("*")
                .eq("id", profile_id)
                .limit(1)
                .execute()
            )

            if not response.data:
                return None, "User not found."

            return response.data[0], None

        except Exception as e:

            return None, str(e)
