"""Navigation bar component for SpyGlass."""
import reflex as rx

def navbar() -> rx.Component:
    """Navigation bar with logo."""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.image(
                    src="/spyglass_logo.png",
                    height="2.5em",
                    width="auto",
                ),
                rx.heading(
                    "SpyGlass",
                    size="5",
                    color="blue.400",
                    font_weight="bold",
                ),
                spacing="4",
            ),
        ),
        bg="white",
        ps="4",
        pe="4",
        position="fixed",
        width="100%",
        top="0px",
        z_index="500",
    )
