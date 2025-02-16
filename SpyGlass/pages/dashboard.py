"""Dashboard page for SpyGlass application."""
import reflex as rx
import state
import components

@rx.page(route="/dashboard")
def dashboard():
    """Main analysis interface"""
    return rx.container(
        components.query_input(),
        rx.skeleton(
            components.progress_bar(),
            is_loaded=state.State.current_step > 0,
            height="50px"
        ),
        rx.heading("Public Reports", size="2xl", margin_y="4"),
        rx.skeleton(
            rx.responsive_grid(
                *[components.report_card(report) for report in state.State.public_reports],
                columns=[1, 2, 3],
                spacing="4"
            ),
            is_loaded=len(state.State.public_reports) > 0,
            min_height="200px"
        ),
        max_width="1200px",
        margin="0 auto",
        padding="4"
    )
