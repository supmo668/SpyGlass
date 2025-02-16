import reflex as rx

def layout(*children, **kwargs):
    """Base layout for all pages."""
    return rx.box(
        *children,
        background_color="white",
        min_height="100vh",
        **kwargs
    )

# Common page metadata
page_meta = {
    "title": "SpyGlass",
    "description": "Discover emerging trends and matching startups",
    "image": "/favicon.ico",  # Add your favicon path
    "meta": [
        {"name": "theme-color", "content": "#7C3AED"},  # Violet theme color
    ],
}
