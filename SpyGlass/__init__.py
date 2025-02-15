import reflex as rx
from .pages.dashboard import dashboard
from .state import State

# Create app instance
app = rx.App(state=State)

# Add pages
app.add_page(dashboard, route="/")
app.add_page(dashboard, route="/dashboard")
