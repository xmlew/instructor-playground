import instructor
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
claude_api_key = os.getenv('ANTHROPIC_API_KEY')

# Check if the API key is available
if not claude_api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

class Pizza(BaseModel):
    name: str
    size: str
    quantity: int

class Order(BaseModel):
    delivery_date: str
    delivery_time: str
    order_list: List[Pizza]

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class UserInfo(BaseModel):
    chain_of_thought: str = Field(
        ..., description="""
            From the order details, obtain their name, whether this is a repeat order, their order (denoted by Order class) and their address (denoted by Address).
            If they did not indicate if it is a repeat order, put False.
            Store the pizza orders in list format of Pizza Classes. The Pizza class has the following limitations:
            Name will always have the first letter capitalized and everything else in lowercase.
            Size will always be either small, medium or large. All lowercase.
            Quantity will always be a non-negative integer.
            For address, break the info down to the following: Street, City, State, Zip Code.
            If any of these are not provided, put 'None'.
            Keep the delivery date and time as strings.
        """
    )
    name: str
    is_repeat_order: bool
    order: Order
    address: Address

# Patch the OpenAI client
client = instructor.from_anthropic(Anthropic(api_key=claude_api_key))

# note that client.chat.completions.create will also work
resp = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Jason has ordered 5 pizzas to be delivered on July 4th, 2024 at 4:00 PM: 2 large Hawaiian pizzas, 3 medium Pepperoni pizzas. He is staying at 123 Main St, Apt 4B, New York, NY 10001.",
        }
    ],
    response_model=UserInfo,
)

# 1. Check if the name is correct
assert resp.name == "Jason"
print(f"1. Name: {resp.name}")

# 2. Check if the total number of pizzas is correct
assert sum(pizza.quantity for pizza in resp.order.order_list) == 5
print(f"2. Total pizzas: {sum(pizza.quantity for pizza in resp.order.order_list)}")

# 3. Check if the delivery date is correct
assert resp.order.delivery_date == "July 4th, 2024"
print(f"3. Delivery date: {resp.order.delivery_date}")

# 4. Check if the delivery time is correct
assert resp.order.delivery_time == "4:00 PM"
print(f"4. Delivery time: {resp.order.delivery_time}")

# 5. Check if the address is correct
assert resp.address.street == "123 Main St, Apt 4B" and resp.address.city == "New York" and resp.address.state == "NY" and resp.address.zip_code == "10001"
print(f"5. Address: {resp.address.street}, {resp.address.city}, {resp.address.state} {resp.address.zip_code}")

print(f"Chain of thought: {resp.chain_of_thought[:50]}...")  # Print first 50 characters