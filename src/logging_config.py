import logging
import os
from datetime import datetime

def setup_logging(app):
    """Configure logging for the Flask application"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler for general application logs
    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'app.log')
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    
    # File handler for payment-specific logs
    payment_handler = logging.FileHandler(
        os.path.join(log_dir, 'payment.log')
    )
    payment_handler.setLevel(logging.DEBUG)
    payment_handler.setFormatter(log_format)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(log_format)
    
    # Configure Flask app logger
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # Configure payment logger
    payment_logger = logging.getLogger('payment')
    payment_logger.setLevel(logging.DEBUG)
    payment_logger.addHandler(payment_handler)
    payment_logger.addHandler(console_handler)
    
    # Configure Stripe logger
    stripe_logger = logging.getLogger('stripe')
    stripe_logger.setLevel(logging.DEBUG)
    stripe_logger.addHandler(payment_handler)
    stripe_logger.addHandler(console_handler)
    
    return app

def log_payment_attempt(user_id, plan_type, action, details=None):
    """Log payment-related actions"""
    payment_logger = logging.getLogger('payment')
    message = f"User {user_id} - {action} - Plan: {plan_type}"
    if details:
        message += f" - Details: {details}"
    payment_logger.info(message)

def log_stripe_error(error, context=None):
    """Log Stripe-specific errors"""
    stripe_logger = logging.getLogger('stripe')
    message = f"Stripe Error: {str(error)}"
    if context:
        message += f" - Context: {context}"
    stripe_logger.error(message)

def log_authentication_issue(user_id, issue, context=None):
    """Log authentication-related issues"""
    auth_logger = logging.getLogger('authentication')
    message = f"Auth Issue - User: {user_id} - Issue: {issue}"
    if context:
        message += f" - Context: {context}"
    auth_logger.warning(message)
