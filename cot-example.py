import os
from enum import Enum
from typing import List

import instructor
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Constants
MODEL_NAME = "claude-3-5-sonnet-20240620"
MAX_TOKENS = 1024

# Model definitions
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
        ..., 
        description="""
            From the order details, obtain their name, whether this is a repeat order, their order (denoted by Order class) and their address (denoted by Address).
            If they did not indicate if it is a repeat order, put False.
            Store the pizza orders in list format of Pizza Classes. The Pizza class has the following limitations:
            Name will always have the first letter capitalized and everything else in lowercase.
            Size will always be either small, medium or large. All lowercase.
            Quantity will always be a non-negative integer.
            For address, break the info down to the following: Street, City, State, Zip Code.
            If any of these are not provided, put 'None'.
            Convert the delivery date to strings. 
            For date, do it in YYYY-MM-DD format.
            For time, do it in HH:MM AM/PM format.
        """
    )
    name: str
    is_repeat_order: bool
    order: Order
    address: Address

def load_api_key() -> str:
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    return api_key

def create_anthropic_client(api_key: str):
    return instructor.from_anthropic(Anthropic(api_key=api_key))

def process_order(anthropic_client, user_input: str) -> UserInfo:
    return anthropic_client.messages.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": user_input}],
        response_model=UserInfo,
    )

def validate_order(order_info: UserInfo):
    assert order_info.name == "Jason", f"Expected name 'Jason', got '{order_info.name}'"
    assert sum(pizza.quantity for pizza in order_info.order.order_list) == 5, \
        f"Expected 5 pizzas, got {sum(pizza.quantity for pizza in order_info.order.order_list)}"
    assert order_info.order.delivery_date == "2024-07-04", \
        f"Expected delivery date 'July 4th, 2024', got '{order_info.order.delivery_date}'"
    assert order_info.order.delivery_time == "04:00 PM", \
        f"Expected delivery time '04:00 PM', got '{order_info.order.delivery_time}'"
    assert (order_info.address.street == "123 Main St, Apt 4B" and
            order_info.address.city == "New York" and
            order_info.address.state == "NY" and
            order_info.address.zip_code == "10001"), \
        f"Address mismatch: {order_info.address}"

def main():
    api_key = load_api_key()
    anthropic_client = create_anthropic_client(api_key)
    
    user_input = ("Jason has ordered 5 pizzas to be delivered on July 4th, 2024 at 4:00 PM: "
                  "2 large Hawaiian pizzas, 3 medium Pepperoni pizzas. "
                  "He is staying at 123 Main St, Apt 4B, New York, NY 10001.")
    
    order_info = process_order(anthropic_client, user_input)
    validate_order(order_info)
    
    print(f"Order processed successfully for {order_info.name}")
    print(f"Delivery: {order_info.order.delivery_date} at {order_info.order.delivery_time}")
    print(f"Address: {order_info.address.street}, {order_info.address.city}, "
          f"{order_info.address.state} {order_info.address.zip_code}")
    print(f"Chain of thought: {order_info.chain_of_thought[:100]}...")

if __name__ == "__main__":
    main()