import reflex as rx
from .state import State

def query_input():
    """Professional search input component"""
    return rx.chakra.stack(
        rx.chakra.heading("Industry Trend Analyzer", size="xl"),
        rx.chakra.text_area(
            placeholder="Enter your industry focus (e.g. 'AI in healthcare')",
            on_change=State.set_search_query,
            height="120px",
            border="2px solid #e2e8f0",
            border_radius="lg",
            _focus={"border": "2px solid #3182ce"}
        ),
        rx.chakra.button(
            "Analyze Trends",
            on_click=State.process_query,
            color_scheme="blue",
            size="lg",
            is_loading=State.current_step > 0
        ),
        spacing=4
    )

def progress_bar():
    """Animated progress visualization"""
    return rx.chakra.box(
        rx.chakra.text(State.processing_steps[State.current_step], font_weight="bold"),
        rx.chakra.progress(
            value=(State.current_step + 1) * 20,
            height="8px",
            color_scheme="blue",
            is_animated=True,
            border_radius="full"
        ),
        padding_y=4
    )

def report_card(report: dict):
    """BI Report display card"""
    return rx.chakra.box(
        rx.chakra.heading(report.get("title", "Industry Report"), size="md"),
        rx.chakra.stack(
            *[rx.chakra.text(section) for section in report.get("sections", [])[:2]],
            spacing=2
        ),
        rx.chakra.hstack(
            rx.chakra.badge("Public", color_scheme="green") if report.get("public") else rx.chakra.badge("Private"),
            rx.chakra.text(f"Created: {report.get('created_at', '')}"),
            justify="space-between"
        ),
        border="1px solid #e2e8f0",
        padding=4,
        border_radius="lg",
        _hover={"shadow": "md"}
    )
