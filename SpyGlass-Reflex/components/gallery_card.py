"""Gallery card component for displaying business reports."""
import reflex as rx
from typing import Dict, Any

def gallery_card(report: Dict[str, Any]) -> rx.Component:
    """A card displaying a business report in gallery style."""
    return rx.box(
        rx.vstack(
            rx.heading(report["title"], size="5"),
            rx.text(report["description"], color="gray.600"),
            rx.spacer(),
            rx.hstack(
                rx.text(f"Created: {report['created_at']}", color="gray.500"),
                rx.spacer(),
                rx.button(
                    "View",
                    on_click=lambda: rx.redirect(f"/report/{report['id']}"),
                    color_scheme="blue",
                ),
                width="100%",
            ),
            height="100%",
            align_items="flex-start",
            spacing="4",
        ),
        p="6",
        bg="white",
        border_radius="lg",
        border="1px solid",
        border_color="gray.200",
        width="100%",
        height="100%",
    )
