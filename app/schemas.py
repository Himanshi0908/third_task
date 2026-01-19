from marshmallow import Schema, fields, validate, ValidationError

class UserRegistrationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=[
        validate.Length(min=8),
        # Custom validation can be added for uppercase, lowercase, number
    ])
    role = fields.Str(load_default='user', validate=validate.OneOf(['user', 'admin']))

def validate_password_complexity(password):
    if not any(char.isdigit() for char in password):
        raise ValidationError("Password must contain at least one number.")
    if not any(char.isupper() for char in password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        raise ValidationError("Password must contain at least one lowercase letter.")

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class TaskSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf(["pending", "in-progress", "completed"]))
    priority = fields.Str(validate=validate.OneOf(["low", "medium", "high"]))
    due_date = fields.DateTime(allow_none=True)
    assignee_id = fields.Integer(allow_none=True)

