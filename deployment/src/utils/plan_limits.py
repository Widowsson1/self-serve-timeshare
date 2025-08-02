"""
Plan limits and configuration for SelfServe Timeshare platform
"""

# Plan configuration with limits and features
PLAN_CONFIG = {
    'starter_monthly': {
        'name': 'Starter',
        'price': 7.99,
        'max_listings': 1,
        'max_photos_per_listing': 6,
        'features': [
            'Create 1 listing',
            'Up to 6 photos per listing',
            'Basic listing analytics',
            'Email support'
        ]
    },
    'basic_monthly': {
        'name': 'Basic',
        'price': 14.99,
        'max_listings': 2,
        'max_photos_per_listing': 10,
        'features': [
            'Create 2 listings',
            'Up to 10 photos per listing',
            'Advanced listing analytics',
            'Priority email support',
            'Featured listing option'
        ]
    },
    'premium_monthly': {
        'name': 'Premium',
        'price': 24.99,
        'max_listings': 5,
        'max_photos_per_listing': 20,
        'features': [
            'Create 5 listings',
            'Up to 20 photos per listing',
            'Premium listing analytics',
            'Phone & email support',
            'Featured listings included',
            'Advanced search placement'
        ]
    },
    'unlimited_monthly': {
        'name': 'Unlimited',
        'price': 39.99,
        'max_listings': -1,  # -1 means unlimited
        'max_photos_per_listing': 30,
        'features': [
            'Unlimited listings',
            'Up to 30 photos per listing',
            'Premium analytics & insights',
            'Priority phone & email support',
            'Featured listings included',
            'Top search placement',
            'Bulk listing tools',
            'API access'
        ]
    }
}

# Legacy plan mappings for backward compatibility
LEGACY_PLAN_MAPPING = {
    'basic_monthly': 'basic_monthly',  # Maps to new basic (2 listings)
    'premium_monthly': 'premium_monthly'  # Maps to new premium (5 listings)
}

def get_plan_limits(membership_type):
    """
    Get the limits for a specific membership type
    
    Args:
        membership_type (str): The membership type (e.g., 'basic_monthly')
        
    Returns:
        dict: Plan configuration with limits and features
    """
    # Handle legacy plans
    if membership_type in LEGACY_PLAN_MAPPING:
        membership_type = LEGACY_PLAN_MAPPING[membership_type]
    
    return PLAN_CONFIG.get(membership_type, PLAN_CONFIG['starter_monthly'])

def get_max_listings(membership_type):
    """
    Get the maximum number of listings allowed for a membership type
    
    Args:
        membership_type (str): The membership type
        
    Returns:
        int: Maximum listings (-1 for unlimited)
    """
    plan = get_plan_limits(membership_type)
    return plan['max_listings']

def get_max_photos(membership_type):
    """
    Get the maximum number of photos per listing for a membership type
    
    Args:
        membership_type (str): The membership type
        
    Returns:
        int: Maximum photos per listing
    """
    plan = get_plan_limits(membership_type)
    return plan['max_photos_per_listing']

def is_unlimited_plan(membership_type):
    """
    Check if a membership type has unlimited listings
    
    Args:
        membership_type (str): The membership type
        
    Returns:
        bool: True if unlimited, False otherwise
    """
    return get_max_listings(membership_type) == -1

def get_plan_name(membership_type):
    """
    Get the display name for a membership type
    
    Args:
        membership_type (str): The membership type
        
    Returns:
        str: Display name for the plan
    """
    plan = get_plan_limits(membership_type)
    return plan['name']

def get_plan_price(membership_type):
    """
    Get the price for a membership type
    
    Args:
        membership_type (str): The membership type
        
    Returns:
        float: Plan price
    """
    plan = get_plan_limits(membership_type)
    return plan['price']

def get_all_plans():
    """
    Get all available plans with their configurations
    
    Returns:
        dict: All plan configurations
    """
    return PLAN_CONFIG

def validate_listing_limit(membership_type, current_listings):
    """
    Validate if a user can create another listing based on their plan
    
    Args:
        membership_type (str): The membership type
        current_listings (int): Current number of active listings
        
    Returns:
        tuple: (can_create: bool, error_message: str or None)
    """
    max_listings = get_max_listings(membership_type)
    plan_name = get_plan_name(membership_type)
    
    # Unlimited plan
    if max_listings == -1:
        return True, None
    
    # Check limit
    if current_listings >= max_listings:
        if max_listings == 1:
            error_msg = f'Listing limit reached. Your {plan_name} plan allows {max_listings} active listing.'
        else:
            error_msg = f'Listing limit reached. Your {plan_name} plan allows {max_listings} active listings.'
        return False, error_msg
    
    return True, None

def validate_photo_limit(membership_type, photo_count):
    """
    Validate if a photo count is within the plan limit
    
    Args:
        membership_type (str): The membership type
        photo_count (int): Number of photos to upload
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    max_photos = get_max_photos(membership_type)
    plan_name = get_plan_name(membership_type)
    
    if photo_count > max_photos:
        error_msg = f'Photo limit exceeded. Your {plan_name} plan allows up to {max_photos} photos per listing.'
        return False, error_msg
    
    return True, None

