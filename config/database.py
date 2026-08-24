import os

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client


# Load variables from .env when running locally
load_dotenv()


class Database:

    def __init__(self):

        supabase_url = None
        supabase_key = None

        # --------------------------------------------------
        # 1. Try Streamlit Secrets
        #    Used when deployed to Streamlit Cloud
        # --------------------------------------------------
        try:
            supabase_url = st.secrets.get("SUPABASE_URL")
            supabase_key = st.secrets.get("SUPABASE_KEY")
        except Exception:
            pass

        # --------------------------------------------------
        # 2. If Streamlit Secrets are not available,
        #    use local .env variables
        # --------------------------------------------------
        if not supabase_url:
            supabase_url = os.getenv("SUPABASE_URL")

        if not supabase_key:
            supabase_key = os.getenv("SUPABASE_KEY")

        # --------------------------------------------------
        # 3. Check credentials
        # --------------------------------------------------
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY are required."
            )

        # --------------------------------------------------
        # 4. Create Supabase client
        # --------------------------------------------------
        self.client = create_client(
            supabase_url,
            supabase_key
        )

    # ------------------------------------------------------
    # Return Supabase client
    # ------------------------------------------------------
    def get_client(self):
        return self.client