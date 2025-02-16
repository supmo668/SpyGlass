"""Main SpyGlass application."""
import reflex as rx
from state import State
from pages import index

# Create app instance
app = rx.App()

# Configure the application
app.state = State
app.style = {
    "font_family": "Inter, sans-serif",
    rx.button: {
        "_hover": {
            "transform": "scale(1.02)",
            "transition": "transform 0.2s ease-in-out",
        }
    }
}