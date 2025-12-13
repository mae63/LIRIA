"""
Authentication service using Supabase Auth.
Handles user signup, login, and session management.
"""

import os
from typing import Optional, Dict
from supabase import create_client, Client
from dotenv import load_dotenv
import httpx

load_dotenv()

class AuthService:
    """Service for authentication operations using Supabase Auth"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # For admin operations
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Store service key and URL for admin operations (auto-confirm emails)
        self.supabase_url = supabase_url
        self.supabase_service_key = supabase_service_key
    
    def sign_up(self, email: str, password: str) -> Dict:
        """Sign up a new user and auto-confirm email if service key is available"""
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": None,
                    "data": {}
                }
            })
            if response.user:
                # Auto-confirm email using admin API (if service key is configured)
                if self.supabase_service_key and not response.user.email_confirmed_at:
                    try:
                        # Use REST API to confirm email via admin endpoint (synchronous)
                        with httpx.Client() as client:
                            admin_response = client.put(
                                f"{self.supabase_url}/auth/v1/admin/users/{response.user.id}",
                                headers={
                                    "apikey": self.supabase_service_key,
                                    "Authorization": f"Bearer {self.supabase_service_key}",
                                    "Content-Type": "application/json"
                                },
                                json={"email_confirm": True}
                            )
                            if admin_response.status_code == 200:
                                # Get a new session after confirmation
                                sign_in_response = self.supabase.auth.sign_in_with_password({
                                    "email": email,
                                    "password": password,
                                })
                                if sign_in_response.session:
                                    return {
                                        "success": True,
                                        "user_id": response.user.id,
                                        "email": response.user.email,
                                        "session": sign_in_response.session,
                                    }
                    except Exception as admin_error:
                        print(f"[AuthService] Warning: Could not auto-confirm email: {admin_error}")
                        # Continue with unconfirmed user if auto-confirmation fails
                
                return {
                    "success": True,
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "session": response.session,
                }
            return {"success": False, "error": "Failed to create user"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_in(self, email: str, password: str) -> Dict:
        """Sign in an existing user"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            if response.user:
                # Check if user is confirmed
                if not response.user.email_confirmed_at:
                    # Try to auto-confirm if service key is available
                    if self.supabase_service_key:
                        try:
                            with httpx.Client() as client:
                                admin_response = client.put(
                                    f"{self.supabase_url}/auth/v1/admin/users/{response.user.id}",
                                    headers={
                                        "apikey": self.supabase_service_key,
                                        "Authorization": f"Bearer {self.supabase_service_key}",
                                        "Content-Type": "application/json"
                                    },
                                    json={"email_confirm": True}
                                )
                                if admin_response.status_code == 200:
                                    # Retry sign in after confirmation
                                    response = self.supabase.auth.sign_in_with_password({
                                        "email": email,
                                        "password": password,
                                    })
                        except Exception as confirm_error:
                            print(f"[AuthService] Warning: Could not auto-confirm email: {confirm_error}")
                    
                    if not response.user.email_confirmed_at:
                        return {
                            "success": False,
                            "error": "Email not confirmed. Please check your email for a confirmation link."
                        }
                
                if response.session:
                    return {
                        "success": True,
                        "user_id": response.user.id,
                        "email": response.user.email,
                        "session": response.session,
                    }
                return {"success": False, "error": "No session created"}
            return {"success": False, "error": "Invalid credentials"}
        except Exception as e:
            error_msg = str(e)
            # Extract more detailed error message if available
            if hasattr(e, 'message'):
                error_msg = e.message
            elif hasattr(e, 'args') and len(e.args) > 0:
                error_msg = str(e.args[0])
            
            # Check for specific Supabase error messages
            if "Invalid login credentials" in error_msg or "invalid_credentials" in error_msg.lower():
                return {"success": False, "error": "Invalid email or password"}
            elif "Email not confirmed" in error_msg or "email_not_confirmed" in error_msg.lower():
                return {"success": False, "error": "Email not confirmed. Please check your email for a confirmation link."}
            else:
                return {"success": False, "error": f"Sign in failed: {error_msg}"}
    
    def sign_out(self) -> bool:
        """Sign out the current user"""
        try:
            self.supabase.auth.sign_out()
            return True
        except Exception as e:
            print(f"[AuthService] Error signing out: {e}")
            return False
    
    def get_user(self, access_token: str) -> Optional[Dict]:
        """Get user from access token"""
        try:
            # Set the session with the access token
            self.supabase.auth.set_session(access_token, "")
            user = self.supabase.auth.get_user(access_token)
            if user:
                return {
                    "user_id": user.user.id,
                    "email": user.user.email,
                }
            return None
        except Exception as e:
            print(f"[AuthService] Error getting user: {e}")
            return None
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify access token and return user_id"""
        try:
            user = self.supabase.auth.get_user(token)
            if user:
                return user.user.id
            return None
        except Exception as e:
            print(f"[AuthService] Error verifying token: {e}")
            return None


