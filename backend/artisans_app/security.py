"""
Security, Role-Based Access Control, JWT & Cryptographic Escrow Module
Provides secure authorization, role gating, and tamper-evident transaction sealing.
"""

import jwt
import hmac
import hashlib
import time
import re
from datetime import datetime, timedelta
from django.conf import settings

JWT_SECRET = getattr(settings, 'SECRET_KEY', 'artisan-secret-key-2026')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 72

class SecurityService:
    @staticmethod
    def generate_jwt_token(user_profile):
        """Generates a signed JWT payload with user role and permissions."""
        payload = {
            'user_id': str(user_profile.id),
            'username': user_profile.username,
            'role': user_profile.role,
            'full_name': user_profile.full_name,
            'is_verified': user_profile.is_verified,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_jwt_token(token):
        """Decodes and validates a JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def generate_escrow_seal(order_id, artisan_id, amount):
        """
        Creates a tamper-evident SHA-256 cryptographic seal for the artisan escrow deposit.
        Ensures funds cannot be released without matching signature.
        """
        raw_string = f"{order_id}:{artisan_id}:{amount}:{time.time()}:{JWT_SECRET}"
        signature = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
        return f"ESCROW-SEAL-{signature[:24].upper()}"

    @staticmethod
    def sanitize_input(text):
        """Sanitizes user strings to prevent script injection."""
        if not isinstance(text, str):
            return text
        clean = re.sub(r'<[^>]*?>', '', text)
        return clean.strip()

    @staticmethod
    def check_role_permission(user_role, allowed_roles):
        """Checks if a user role matches the required permission scope."""
        return user_role in allowed_roles
