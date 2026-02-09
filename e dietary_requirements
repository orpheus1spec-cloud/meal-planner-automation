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
- Luch can include any protein, dinner must exclude red meat but can include chicken and fish
- 1300 calories per day target for lunch and dinner only
- High protein preference
- Serves 4 people
- No hot dishes, mild chili only occassionally
- Include fresh salads 5 days a week
- Quick weekday meals (under 30 minutes)
- More elaborate weekend meals allowed
"""

# Create the prompt for Claude
prompt = f"""Create a detailed weekly meal plan for the week of {week_range}.

DIETARY REQUIREMENTS:
{dietary_requirements}

Please provide:
1. A complete lunch, and dinner for each day (Monday-Sunday)
2. Include approximate calories for each meal
3. A comprehensive shopping list organized by category (produce, pantry, etc.)
4. Brief cooking instructions or tips where helpful

Format the response in a clear, easy-to-read way with sections for each day and the shopping list at the end."""

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Call Claude API
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4000,
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Get the meal plan
meal_plan = message.content[0].text

# Send email
def send_email(subject, body):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Send the meal plan
send_email(
    subject=f"Weekly Meal Plan: {week_range}",
    body=meal_plan
)

print("Meal plan generated and sent!")
