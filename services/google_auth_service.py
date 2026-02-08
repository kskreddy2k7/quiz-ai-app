"""
Google OAuth Authentication Service
Handles Google Sign-In token verification and user authentication
"""
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class GoogleAuthService:
    def __init__(self):
        # Get Google OAuth client ID from environment
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        if not self.client_id:
            logger.warning("GOOGLE_CLIENT_ID not set in environment variables")
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify Google ID token and extract user information
        
        Args:
            token: Google ID token from frontend
            
        Returns:
            Dict with user info (google_id, email, name, picture) or None if invalid
        """
        if not self.client_id:
            logger.error("Cannot verify token: GOOGLE_CLIENT_ID not configured")
            return None
            
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            
            # Token is valid, extract user information
            user_info = {
                "google_id": idinfo.get("sub"),
                "email": idinfo.get("email"),
                "name": idinfo.get("name"),
                "picture": idinfo.get("picture"),
                "email_verified": idinfo.get("email_verified", False)
            }
            
            # Validate required fields
            if not user_info["google_id"] or not user_info["email"]:
                logger.error("Missing required fields in Google token")
                return None
                
            return user_info
            
        except ValueError as e:
            # Invalid token
            logger.error(f"Invalid Google token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying Google token: {str(e)}")
            return None
    
    def is_configured(self) -> bool:
        """Check if Google OAuth is properly configured"""
        return bool(self.client_id)

# Singleton instance
google_auth_service = GoogleAuthService()
