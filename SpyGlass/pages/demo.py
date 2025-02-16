"""Demo page showing query results."""
import reflex as rx
from state import State
import components

@rx.page(route="/demo")
def demo() -> rx.Component:
    """Demo page component."""
    return rx.box(
        components.navbar(),
        rx.center(
            rx.vstack(
                rx.heading(
                    "Analysis Results",
                    size="3",
                    color="whiteAlpha.800",
                    padding_top="8em",
                ),
                rx.text(
                    "Your query is being processed...",
                    color="whiteAlpha.600",
                ),
                width="100%",
                max_width="1200px",
                padding="2em",
            ),
        ),
        min_height="100vh",
        background="radial-gradient(circle at center, rgba(25, 25, 35, 0.98), rgba(10, 10, 15, 0.98))",
        background_image="url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1500')",
        background_size="cover",
        background_attachment="fixed",
        background_blend_mode="overlay",
        padding="2em",
    )
