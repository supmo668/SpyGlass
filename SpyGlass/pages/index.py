"""The main page of the SpyGlass application."""
import reflex as rx
import state
import components

@rx.page(route="/")
def index() -> rx.Component:
    """The main page of the application."""
    return rx.center(
        rx.vstack(
            rx.heading("SpyGlass", size="1"),
            rx.text("Your Business Intelligence Assistant", color="gray.500"),
            components.progress_indicator(),
            rx.form(
                rx.input(
                    placeholder="Ask me anything about your business...",
                    on_change=state.State.set_query,
                    value=state.State.query,
                    width="100%",
                ),
                rx.button(
                    "Ask",
                    type="submit",
                    is_loading=state.State.is_processing,
                    width="100%",
                ),
                on_submit=state.State.start_processing,
                width="100%",
            ),
            rx.cond(
                state.State.error_message != "",
                rx.text(state.State.error_message, color="red.500"),
            ),
            rx.foreach(
                state.State.public_reports,
                components.report_card,
            ),
            width="100%",
            max_width="600px",
            padding="4",
            spacing="4",
        ),
        width="100%",
    )
