import os

# Load product details from the text file
def load_product_details():
    file_path = os.path.join(os.path.dirname(__file__), 'products.txt')
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Product details not available."

PRODUCT_DETAILS = load_product_details()

# Email templates for initial lead discovery
EMAIL_TEMPLATES = [
    {
        "id": 1,
        "name": "Introduction Template",
        "subject": "Introduction to Our Aerial Lift Solutions",
        "body": f"""Dear [Lead Name],

I hope this email finds you well. My name is [Your Name] from [Your Company], and I'm reaching out because I understand you're exploring options for aerial lift equipment.

We specialize in providing high-quality aerial lifts that can help improve safety and efficiency in your operations. Our product line includes:

{PRODUCT_DETAILS}

I'd love to learn more about your specific needs and how we might be able to assist you. Would you be available for a brief call next week to discuss your requirements?

Looking forward to hearing from you.

Best regards,
[Your Name]
[Your Position]
[Your Company]
[Contact Information]
"""
    },
    {
        "id": 2,
        "name": "Value Proposition Template",
        "subject": "How Our Aerial Lifts Can Benefit Your Business",
        "body": f"""Dear [Lead Name],

Thank you for your interest in aerial lift solutions. At [Your Company], we understand the importance of reliable, safe equipment for your team.

Our aerial lifts are designed with productivity and safety in mind. Here are some key benefits:

- Enhanced safety features for operator protection
- Versatile platforms suitable for various applications
- Easy maneuverability in tight spaces
- Durable construction for long-term reliability

Our product range includes:

{PRODUCT_DETAILS}

I'd be happy to provide a customized quote based on your specific requirements. Could we schedule a quick call to discuss how our solutions might fit your needs?

Best regards,
[Your Name]
[Your Position]
[Your Company]
[Contact Information]
"""
    },
    {
        "id": 3,
        "name": "Discovery Questions Template",
        "subject": "Questions to Help Us Find the Right Aerial Lift for You",
        "body": f"""Dear [Lead Name],

I wanted to follow up on our previous conversation about aerial lift equipment. To ensure we recommend the best solution for your needs, I have a few questions:

1. What type of work will the aerial lift be used for?
2. How high do you typically need to reach?
3. What is the terrain like where you'll be operating?
4. How many operators will be using the equipment?
5. Do you have any specific safety requirements?

Our comprehensive product line includes:

{PRODUCT_DETAILS}

Your answers will help us provide a more accurate recommendation. Please reply to this email or give me a call at your convenience.

Thank you for your time.

Best regards,
[Your Name]
[Your Position]
[Your Company]
[Contact Information]
"""
    },
    {
        "id": 4,
        "name": "Product Showcase Template",
        "subject": "Explore Our Range of Aerial Lift Equipment",
        "body": f"""Dear [Lead Name],

We're excited about the possibility of working with you on your aerial lift needs. Our products are engineered for performance and reliability.

Here's an overview of our key products:

{PRODUCT_DETAILS}

Each of our aerial lifts comes with comprehensive training and support to ensure your team can operate them safely and effectively.

Would you like to schedule a demonstration or discuss pricing options?

Best regards,
[Your Name]
[Your Position]
[Your Company]
[Contact Information]
"""
    }
]

def get_templates():
    """Return all email templates"""
    return EMAIL_TEMPLATES

def get_template_by_id(template_id):
    """Return a specific template by ID"""
    for template in EMAIL_TEMPLATES:
        if template['id'] == template_id:
            return template
    return None