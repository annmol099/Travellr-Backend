"""
Request and response schemas for authentication.
"""
from marshmallow import Schema, fields, validate, ValidationError


class RegisterSchema(Schema):
    """Schema for user registration."""
    
    email = fields.Email(required=True, error_messages={
        "required": "Email is required",
        "invalid": "Invalid email format"
    })
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters"),
        error_messages={"required": "Password is required"}
    )
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={"required": "Name is required"}
    )
    phone = fields.String(allow_none=True, validate=validate.Length(max=20))


class LoginSchema(Schema):
    """Schema for user login."""
    
    email = fields.Email(required=True, error_messages={
        "required": "Email is required",
        "invalid": "Invalid email format"
    })
    password = fields.String(required=True, error_messages={
        "required": "Password is required"
    })


class UserResponseSchema(Schema):
    """Schema for user response."""
    
    id = fields.String()
    email = fields.Email()
    name = fields.String()
    phone = fields.String()
    role = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime()


class TokenResponseSchema(Schema):
    """Schema for token response."""
    
    access_token = fields.String()
    user = fields.Nested(UserResponseSchema)
    message = fields.String()
