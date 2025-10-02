"""
TEMPORARY: Stripe test configuration for immediate testing
This file provides a fallback Stripe test key for development/testing purposes
DO NOT USE IN PRODUCTION - Set proper environment variables instead
"""

import os
import stripe

def configure_stripe_for_testing():
    """Configure Stripe with test key if no environment key is set"""
    
    # Check if environment variable is already set
    if os.getenv('STRIPE_SECRET_KEY'):
        print("Using Stripe key from environment variable")
        return os.getenv('STRIPE_SECRET_KEY')
    
    # TEMPORARY: Use test key for immediate testing
    # Replace with your actual test key
    test_key = "sk_test_51234567890abcdef"  # PLACEHOLDER - Replace with real test key
    
    print("WARNING: Using temporary test Stripe key")
    print("For production, set STRIPE_SECRET_KEY environment variable")
    
    return test_key

def setup_stripe():
    """Setup Stripe configuration with fallback"""
    api_key = configure_stripe_for_testing()
    stripe.api_key = api_key
    return api_key

# Test function to verify Stripe connection
def test_stripe_connection():
    """Test if Stripe API key is working"""
    try:
        # Try to list customers (minimal API call)
        customers = stripe.Customer.list(limit=1)
        return True, "Stripe connection successful"
    except stripe.error.AuthenticationError:
        return False, "Stripe authentication failed - invalid API key"
    except stripe.error.APIConnectionError:
        return False, "Stripe connection failed - network issue"
    except Exception as e:
        return False, f"Stripe error: {str(e)}"

if __name__ == "__main__":
    # Test the configuration
    api_key = setup_stripe()
    print(f"Stripe API key configured: {api_key[:7]}...")
    
    success, message = test_stripe_connection()
    print(f"Connection test: {message}")
