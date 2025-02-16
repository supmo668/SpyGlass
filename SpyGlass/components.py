"""Components for the SpyGlass application."""
import reflex as rx
from typing import Dict, Any

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
            width="100%",
            max_width="1200px",
            padding_x="2em",
            padding_y="1em",
        ),
        position="fixed",
        top="0",
        left="0",
        right="0",
        backdrop_filter="blur(10px)",
        bg="rgba(17, 17, 17, 0.9)",
        border_bottom="1px solid",
        border_color="whiteAlpha.200",
        z_index="1000",
    )

def gallery_card(report: Dict[str, Any]) -> rx.Component:
    """A card displaying a business report in gallery style."""
    return rx.box(
        rx.vstack(
            rx.image(
                src=report["image_url"],
                width="100%",
                aspect_ratio="1",
                object_fit="cover",
                border_radius="xl",
            ),
            rx.heading(
                report["title"],
                size="6",
                color="blue.400",
            ),
            align="stretch",
            spacing="4",
        ),
        padding="5",
        bg="rgba(17, 17, 17, 0.7)",
        border_radius="2xl",
        border="1px solid",
        border_color="whiteAlpha.200",
        _hover={
            "transform": "translateY(-4px)",
            "border_color": "blue.400",
            "box_shadow": "lg",
        },
        transition="all 0.2s",
    )
