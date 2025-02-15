import reflex as rx
from .components import progress_indicator, report_card
from .state import State
from .workflow import AnalysisWorkflow


def index() -> rx.Component:
    return rx.container(
        rx.heading("SpyGlass Analytics", size="8", margin_bottom="2rem"),
        rx.hstack(
            rx.input(
                placeholder="Enter business trend query...",
                on_change=State.set_query,
                width="70%",
                size="3"
            ),
            rx.button("Analyze", on_click=AnalysisWorkflow.trigger_analysis),
            justify="center",
            margin_bottom="2rem"
        ),
        progress_indicator(),
        rx.grid(
            rx.foreach(
                State.public_reports,
                lambda report: report_card(report)
            ),
            columns="3",
            spacing="4",
            margin_top="2rem"
        ),
        padding="2rem",
        max_width="1200px"
    )
