import reflex as rx
import os

config = rx.Config(
    app_name="SpyGlass",
    db_url="sqlite:///spyglass.db",
    env=rx.Env.DEV,
    frontend_packages=[
        "framer-motion",
    ],
    tailwind={
        "theme": {
            "extend": {
                "colors": {
                    "background": "#0a0a0f",
                }
            }
        }
    },
    static_dir=os.path.join(os.path.dirname(__file__), "assets"),
)