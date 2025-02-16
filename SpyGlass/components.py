import reflex as rx
from state import State

def query_input():
    """Professional search input component"""
    return rx.stack(
        rx.heading("Industry Trend Analyzer", size="1"),
        rx.text_area(
            placeholder="Enter your industry focus (e.g. 'AI in healthcare')",
            on_change=State.set_query,
            height="120px",
            border="2px solid #e2e8f0",
            border_radius="lg",
            _focus={"border": "2px solid #3182ce"}
        ),
        rx.button(
            "Analyze Trends",
            on_click=State.start_processing,
            color_scheme="blue",
            size="2",
            is_loading=State.current_step > 0
        ),
        spacing="4"
    )

def progress_step(label: str, index: int, is_last: bool) -> rx.Component:
    """A single step in the progress indicator."""
    return rx.flex(
        rx.hstack(
            rx.box(
                rx.cond(
                    State.current_step > index,
                    rx.text("✓", color="white", font_size="14px"),
                    rx.text(str(index + 1), color=rx.cond(
                        State.current_step >= index,
                        "white",
                        "gray.500"
                    ), font_size="14px"),
                ),
                background=rx.cond(
                    State.current_step > index,
                    "green.500",
                    rx.cond(
                        State.current_step >= index,
                        "violet.500",
                        "gray.200"
                    )
                ),
                width="24px",
                height="24px",
                border_radius="full",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
            rx.text(
                label,
                color=rx.cond(
                    State.current_step >= index,
                    "black",
                    "gray.500"
                ),
                font_weight=rx.cond(
                    State.current_step >= index,
                    "bold",
                    "medium"
                ),
            ),
        ),
        rx.cond(
            ~is_last,
            rx.box(
                height="1px",
                flex="1",
                background=rx.cond(
                    State.current_step > index,
                    "green.500",
                    rx.cond(
                        State.current_step >= index,
                        "violet.500",
                        "gray.200"
                    )
                ),
            ),
        ),
        width="100%",
        align="center",
    )

def progress_indicator() -> rx.Component:
    """Progress indicator showing the current analysis step."""
    steps = [
        "Query Analysis",
        "Market Research",
        "Startup Discovery",
        "Report Generation",
    ]
    
    return rx.vstack(
        rx.cond(
            State.error_message != "",
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.button("Error", color_scheme="red")
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("Error"),
                    rx.alert_dialog.description(State.error_message),
                    rx.button(
                        "Retry",
                        on_click=State.start_processing,
                        size="1",
                        margin_top="2",
                    ),
                )
            ),
        ),
        rx.box(
            rx.hstack(
                *[
                    progress_step(
                        label=step,
                        index=i,
                        is_last=(i == len(steps) - 1)
                    )
                    for i, step in enumerate(steps)
                ],
                spacing="4",
                width="100%",
            ),
            padding="4",
            bg="white",
            border_radius="lg",
            shadow="sm",
        ),
        width="100%",
    )

def report_card(report: dict) -> rx.Component:
    """A card displaying a business report."""
    return rx.box(
        rx.vstack(
            rx.heading(report["title"], size="2"),
            rx.text(
                ", ".join(report["sections"]),
                color="gray.600",
                number_of_lines=2,
            ),
            rx.hstack(
                rx.badge(
                    "Public" if report["is_public"] else "Private",
                    color_scheme="green" if report["is_public"] else "gray",
                ),
                rx.spacer(),
                rx.button(
                    "View Details →",
                    variant="ghost",
                    size="1",
                ),
                width="100%",
            ),
            align="stretch",
            spacing="4",
        ),
        padding="6",
        bg="white",
        border_radius="lg",
        shadow="sm",
        _hover={"shadow": "md"},
    )