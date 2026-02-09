import anthropic
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get today's date and calculate the week
today = datetime.now()
start_of_week = today + timedelta(days=(6 - today.weekday()))  # Next Sunday
end_of_week = start_of_week + timedelta(days=6)

# Format dates
week_range = f"{start_of_week.strftime('%B %d')} - {end_of_week.strftime('%B %d, %Y')}"

# Your dietary requirements - CUSTOMIZE THIS
dietary_requirements = """
- Lunch can include any protein, dinner must exclude red meat but can include chicken and fish
- 1300 calories per day target for lunch and dinner only
- High protein preference
- Serves 4 people
- No hot dishes, mild chili only occasionally
- Include fresh salads 5 days a week
- Quick weekday meals (under 30 minutes)
- More elaborate weekend meals allowed
"""

# Create the prompt for Claude with recipe instructions
prompt = f"""Create a detailed weekly meal plan for the week of {week_range}.

DIETARY REQUIREMENTS:
{dietary_requirements}

IMPORTANT: Use ONLY METRIC MEASUREMENTS throughout:
- Grams (g) and kilograms (kg) for weight
- Milliliters (ml) and liters (l) for liquids
- Celsius (°C) for temperatures
- No cups, tablespoons, teaspoons, ounces, pounds, or Fahrenheit

Please provide a beautifully formatted meal plan with:

1. **Daily Meal Plans** - For each day (Monday through Sunday):
   - List lunch and dinner
   - Include approximate calories for each meal
   - Add brief descriptions to make meals sound appealing

2. **Complete Recipes** - For EACH meal, provide:
   - Full ingredient list with exact METRIC measurements (for 4 people)
   - Step-by-step cooking instructions (numbered steps)
   - Prep time and cook time
   - Oven temperatures in Celsius if applicable
   - Any helpful tips or substitutions

3. **Shopping List** - At the end, provide:
   - Organized by category (Produce, Proteins, Pantry Items, Refrigerated, etc.)
   - Include METRIC quantities needed for the entire week for 4 people
   - Use checkbox format (□) for easy printing

FORMAT THE RESPONSE IN A CLEAN, EASY-TO-READ WAY:
- Use clear headers and sections
- Use line breaks between sections
- Make it look like a professional meal planning service
- Use emojis sparingly for visual appeal (🥗 🍗 🥘 etc.)

Make this meal plan exciting, healthy, and easy to follow!"""

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Call Claude API with increased tokens for detailed recipes
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=8000,  # Increased for detailed recipes
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Get the meal plan
meal_plan = message.content[0].text

# Format the email as HTML for better readability
def create_html_email(meal_plan_text):
    """Convert the meal plan to a nicely formatted HTML email"""
    
    # Convert plain text to HTML with basic formatting
    html_content = meal_plan_text.replace('\n\n', '</p><p>')
    html_content = html_content.replace('\n', '<br>')
    
    # Make day headers bold and styled
    for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        html_content = html_content.replace(
            f'**{day_name}',
            f'<h2 style="color: #2c3e50; margin-top: 30px; border-left: 4px solid #27ae60; padding-left: 15px;">{day_name}'
        )
        html_content = html_content.replace(f'{day_name}**', f'{day_name}</h2>')
    
    # Replace **text** with bold
    import re
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Replace numbered lists
    html_content = re.sub(r'(\d+\.)', r'<br>\1', html_content)
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.8;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #27ae60;
                border-bottom: 4px solid #27ae60;
                padding-bottom: 15px;
                margin-bottom: 30px;
                font-size: 32px;
            }}
            h2 {{
                color: #2c3e50;
                margin-top: 35px;
                margin-bottom: 20px;
                border-left: 4px solid #27ae60;
                padding-left: 15px;
                font-size: 24px;
            }}
            h3 {{
                color: #34495e;
                margin-top: 25px;
                margin-bottom: 12px;
                font-size: 20px;
            }}
            p {{
                margin: 12px 0;
                font-size: 15px;
            }}
            strong {{
                color: #2c3e50;
                font-weight: 600;
            }}
            .recipe-section {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 3px solid #3498db;
            }}
            .shopping-list {{
                background-color: #e8f5e9;
                padding: 25px;
                border-radius: 8px;
                margin-top: 40px;
                border: 2px solid #27ae60;
            }}
            .calories {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                text-align: center;
                color: #7f8c8d;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍽️ Your Weekly Meal Plan</h1>
            <p style="font-size: 16px; color: #7f8c8d; margin-bottom: 30px;">
                Week of {week_range} | Serves 4 people | Metric measurements
            </p>
            <div class="content">
                <p>{html_content}</p>
            </div>
            <div class="footer">
                <p>🌟 Enjoy your meals! 🌟</p>
                <p>Generated automatically every Sunday</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

# Send email with both plain text and HTML versions
def send_email(subject, body):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Create both plain text and HTML versions
    text_part = MIMEText(body, 'plain')
    html_part = MIMEText(create_html_email(body), 'html')
    
    # Attach both versions (email clients will show HTML if supported, plain text otherwise)
    msg.attach(text_part)
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Send the meal plan
send_email(
    subject=f"🍽️ Your Weekly Meal Plan: {week_range}",
    body=meal_plan
)

print("Meal plan generated and sent!")
