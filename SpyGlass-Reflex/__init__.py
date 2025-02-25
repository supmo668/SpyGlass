"""Main SpyGlass application."""
import reflex as rx
import state
import components
from pages import index, dashboard

# Expose modules
__all__ = ['state', 'components']

# Create app instance
app = rx.App(state=state.State)

# Add pages
app.add_page(index.index, route="/")
app.add_page(dashboard.dashboard, route="/dashboard")
