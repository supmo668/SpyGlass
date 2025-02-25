"""Main SpyGlass application module."""
import reflex as rx

from state.app_state import State
from styles.theme import theme
import pages.index
import pages.demo

# Create the app with custom theme and state
app = rx.App(
    state=State,
    theme=theme,
    style={
        "font_family": "Inter, system-ui, sans-serif",
        "background": "var(--background)",
    }
)
app.state = State
# Add pages
app.add_page(pages.index.index)
app.add_page(pages.demo.demo)
