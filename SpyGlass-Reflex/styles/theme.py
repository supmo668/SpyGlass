"""Application theme and styling constants."""
import reflex as rx

# Color scheme
colors = {
    "primary": "blue.400",
    "secondary": "gray.600",
    "background": "gray.50",
    "text": "gray.800",
    "border": "gray.200",
}

# Typography
typography = {
    "fonts": {
        "body": "Inter, system-ui, sans-serif",
        "heading": "Inter, system-ui, sans-serif",
    },
    "fontSizes": {
        "xs": "0.75rem",
        "sm": "0.875rem",
        "md": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
    },
}

# Component styles
styles = {
    "global": {
        "body": {
            "bg": colors["background"],
            "color": colors["text"],
        }
    }
}

# Create theme
theme = rx.theme(
    colors=colors,
    fonts=typography["fonts"],
    styles=styles,
)
