"""The main page of the SpyGlass application."""
import reflex as rx
from state import State
import components

def search_bar() -> rx.Component:
    """Search bar with submit button."""
    return rx.form(
        rx.hstack(
            rx.text_field(
                value=State.query,
                on_change=State.set_query,
                placeholder="Search business insights...",
                size="3",
                bg="rgba(255, 255, 255, 0.05)",
                border="2px solid",
                border_color="whiteAlpha.200",
                color="white",
                _placeholder={"color": "whiteAlpha.500"},
                _hover={"border_color": "blue.400"},
                _focus={"border_color": "blue.400", "bg": "rgba(255, 255, 255, 0.1)"},
                flex="1",
            ),
            rx.button(
                rx.cond(
                    State.is_processing,
                    rx.spinner(
                        color="blue.400",
                        size="2",
                    ),
                    rx.text("Search"),
                ),
                type="submit",
                size="3",
                color_scheme="blue",
                disabled=State.is_processing,
            ),
            width="100%",
            max_width="600px",
            spacing="4",
        ),
        on_submit=State.process_query,
    )

def pagination() -> rx.Component:
    """Pagination controls."""
    return rx.hstack(
        rx.button(
            "Previous",
            on_click=State.prev_page,
            size="2",
            variant="ghost",
            color_scheme="blue",
            disabled=State.current_page == 1,
        ),
        rx.hstack(
            rx.foreach(
                rx.range(1, State.total_pages + 1),
                lambda i: rx.button(
                    i,
                    on_click=lambda: State.set_page(i),
                    size="2",
                    variant="ghost" if i != State.current_page else "solid",
                    color_scheme="blue",
                ),
            ),
            spacing="2",
        ),
        rx.button(
            "Next",
            on_click=State.next_page,
            size="2",
            variant="ghost",
            color_scheme="blue",
            disabled=State.current_page == State.total_pages,
        ),
        spacing="4",
    )

@rx.page(route="/")
def index() -> rx.Component:
    """The main page of the application."""
    return rx.box(
        components.navbar(),
        rx.center(
            rx.vstack(
                rx.vstack(
                    rx.heading(
                        "Your AI Start-Up Business Partner",
                        size="1",
                        color="whiteAlpha.800",
                        font_weight="medium",
                    ),
                    rx.text(
                        "Discover market insights and business opportunities with AI-powered analysis",
                        color="whiteAlpha.600",
                        font_size="lg",
                    ),
                    spacing="3",
                    padding_top="8em",
                    padding_bottom="4em",
                    text_align="center",
                ),
                search_bar(),
                rx.grid(
                    rx.foreach(
                        State.reports,
                        components.gallery_card,
                    ),
                    template_columns="repeat(4, 1fr)",
                    gap="6",
                    width="100%",
                    margin_y="6",
                ),
                pagination(),
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
