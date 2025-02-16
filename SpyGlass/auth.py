import reflex as rx
from .state import State
import stytch
from sqlmodel import Session
from reflex.state import BaseState
from .database import User, get_engine

class AuthState(BaseState):
    auth_token: str = ""
    
    def handle_auth_callback(self):
        try:
            stytch_client = stytch.Client(
                project_id=os.getenv("STYTCH_PROJECT_ID"),
                secret=os.getenv("STYTCH_SECRET"),
                environment="test"
            )
            session = stytch_client.sessions.authenticate({
                "session_token": self.auth_token
            })
            
            with Session(get_engine()) as db_session:
                user = db_session.get(User, session.user_id)
                if not user:
                    user = User(id=session.user_id)
                    db_session.add(user)
                    db_session.commit()
            
            return rx.redirect("/dashboard")
        except stytch.errors.StytchError as e:
            print(f"Authentication error: {e}")
            return rx.redirect("/?error=auth_failed")

    def logout(self):
        self.auth_token = ""
        return rx.redirect("/")

def auth_component():
    """Stytch authentication UI component"""
    return rx.box(
        rx.script(src="https://js.stytch.com/stytch.js"),
        rx.div(
            id="stytch-auth-container",
            class_name="flex justify-center mt-8",
            style={"min_height": "400px"}
        ),
        rx.script(
            """
            const stytch = Stytch('your_public_token');
            stytch.mount({
                elementId: '#stytch-auth-container',
                config: {
                    products: ['emailMagicLinks'],
                    emailMagicLinksOptions: {
                        loginRedirectURL: window.location.href,
                        signupRedirectURL: window.location.href
                    }
                }
            });
            """
        )
    )

def handle_auth_callback(session_token: str):
    """Handle Stytch auth callback"""
    try:
        session = State.stytch.sessions.authenticate(
            session_token=session_token
        )
        State.user_session = session.__dict__
        return rx.redirect("/dashboard")
    except Exception as e:
        print(f"Authentication error: {e}")
        return rx.window_alert(f"Authentication failed: {str(e)}")
