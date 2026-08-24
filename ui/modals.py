import streamlit as st


class ModalManager:

    @staticmethod
    @st.dialog("Success")
    def success(message):
        st.success(message)

        if st.button("OK"):
            st.rerun()

    @staticmethod
    @st.dialog("Confirm Delete")
    def confirm_delete(
        item_name,
        delete_function
    ):

        st.warning(
            f"Are you sure you want to delete "
            f"**{item_name}**?"
        )

        st.write(
            "This action cannot be undone."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Cancel",
                use_container_width=True
            ):
                st.rerun()

        with col2:

            if st.button(
                "Delete",
                type="primary",
                use_container_width=True
            ):

                success, error = delete_function()

                if error:

                    st.error(error)

                else:

                    st.success(
                        f"{item_name} deleted successfully."
                    )

                    if st.button("OK"):
                        st.rerun()