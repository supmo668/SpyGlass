import reflex as rx
from .state import State
from .auth import AuthState
from .pages import index, dashboard

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="violet",
        radius="large",
    )
)

app.add_page(index.index, route="/")
app.add_page(dashboard.dashboard, route="/dashboard")
app.add_page(AuthState.auth_callback, route="/auth/callback")

if __name__ == "__main__":
    app.run()
