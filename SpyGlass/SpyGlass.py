"""Main SpyGlass application module."""
import reflex as rx
import pages.index
import pages.demo
from state import State

# Create the app and add routes
app = rx.App(state=State)
app.add_page(pages.index.index)
app.add_page(pages.demo.demo)
