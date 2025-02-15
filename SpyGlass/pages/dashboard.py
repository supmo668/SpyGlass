import reflex as rx
from ..components import query_input, progress_bar, report_card
from ..state import State

def dashboard():
    """Main analysis interface"""
    return rx.chakra.container(
        query_input(),
        rx.chakra.skeleton(
            progress_bar(),
            is_loaded=State.current_step > 0,
            height="50px"
        ),
        rx.chakra.heading("Public Reports", size="lg", margin_y=4),
        rx.chakra.skeleton(
            rx.chakra.responsive_grid(
                *[report_card(report) for report in State.public_reports],
                columns=[1, 2, 3],
                spacing=4
            ),
            is_loaded=len(State.public_reports) > 0,
            height="200px"
        ),
        max_width="1200px",
        padding=4
    )
