import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="SpyGlass",
    db_url="sqlite:///spyglass.db",
    env=rx.Env.DEV,
    frontend_packages=[
        "react-icons",
    ],
)