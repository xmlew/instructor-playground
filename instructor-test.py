import instructor
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, time

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
    delivery_date: datetime
    delivery_time: time
    order_list: List[Pizza]

class Address(BaseModel):
    building_name: str
    street_name: str
    area_name: str
    city: str
    emirate: str
    country: str
    makani_number: int

class UserInfo(BaseModel):
    chain_of_thought: str = Field(
        ..., description="""
            From the order details, obtain their name, whether this is a repeat order, their order (denoted by Order class) and their address (denoted by Address).
            If they did not indicate if it is a repeat order, put False.
            Store the pizza orders in list format of Pizza Classes. The Pizza class has the following limitations:
            Name will always have the first letter capitalized and everything else in lowercase.
            Size will always be either small, medium or large. All lowercase.
            Quantity will always be a non-negative integer.
            For address, break the info down to the following: Building name, Street Name, Area Name, City, Emirate, Country, Makani Number.
            If none of these are provided, try to infer those possible without using hallucinations. E.g. if United Arab Emirates is not provided for Country
            but Dubai is the city, you can fill in that as the country name. For missing data, put 'None'. If the Makani Number is missing, put -1.
            Convert the delivery date to a datetime object and the delivery time to a time object.
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
            "content": "Jason has ordered 5 pizzas to be delivered on 4th July 2024 at 4pm: 2 large Hawaiian pizzas, 3 medium Pepperoni pizzas. He is staying in Marina Pearl Tower Unit 1204, Al Marsa Street, Makani: 1234567890",
        }
    ],
    response_model=UserInfo,
)

# 1. Check if the name is correct
assert resp.name == "Jason"
print(f"1. Name: {resp.name}")

# 2. Check if is_repeat_order is a boolean
assert isinstance(resp.is_repeat_order, bool)
print(f"2. Is repeat order: {resp.is_repeat_order}")

# 3. Check if delivery_date is correct
assert isinstance(resp.order.delivery_date, datetime)
print(f"3. Delivery date: {resp.order.delivery_date}")

# 4. Check if delivery_time is correct
assert isinstance(resp.order.delivery_time, time)
print(f"4. Delivery time: {resp.order.delivery_time}")

# 5. Check if the total number of pizzas is correct
assert sum(pizza.quantity for pizza in resp.order.order_list) == 5
print(f"5. Total pizzas: {sum(pizza.quantity for pizza in resp.order.order_list)}")

# 6. Check if the first pizza is Hawaiian
assert resp.order.order_list[0].name == "Hawaiian"
print(f"6. First pizza name: {resp.order.order_list[0].name}")

# 7. Check if the second pizza is Pepperoni
assert resp.order.order_list[1].name == "Pepperoni"
print(f"7. Second pizza name: {resp.order.order_list[1].name}")

# 8. Check if the Hawaiian pizza size is large
assert resp.order.order_list[0].size == "large"
print(f"8. Hawaiian pizza size: {resp.order.order_list[0].size}")

# 9. Check if the Pepperoni pizza size is medium
assert resp.order.order_list[1].size == "medium"
print(f"9. Pepperoni pizza size: {resp.order.order_list[1].size}")

# 10. Check if the Hawaiian pizza quantity is 2
assert resp.order.order_list[0].quantity == 2
print(f"10. Hawaiian pizza quantity: {resp.order.order_list[0].quantity}")

# 11. Check if the Pepperoni pizza quantity is 3
assert resp.order.order_list[1].quantity == 3
print(f"11. Pepperoni pizza quantity: {resp.order.order_list[1].quantity}")

# 12. Check if the building name is correct
assert resp.address.building_name == "Marina Pearl Tower"
print(f"12. Building name: {resp.address.building_name}")

# 13. Check if the street name is correct
assert resp.address.street_name == "Al Marsa Street"
print(f"13. Street name: {resp.address.street_name}")

# 14. Check if the city is Dubai
assert resp.address.city == "Dubai"
print(f"14. City: {resp.address.city}")

# 15. Check if the emirate is Dubai
assert resp.address.emirate == "Dubai"
print(f"15. Emirate: {resp.address.emirate}")

# 16. Check if the country is United Arab Emirates
assert resp.address.country == "United Arab Emirates"
print(f"16. Country: {resp.address.country}")

# 17. Check if the Makani number is correct
assert resp.address.makani_number == 1234567890
print(f"17. Makani number: {resp.address.makani_number}")

# 18. Check if the chain_of_thought is not empty
assert resp.chain_of_thought != ""
print(f"18. Chain of thought: {resp.chain_of_thought[:50]}...")  # Print first 50 characters

# 19. Check if the area_name is not None (it might be inferred)
assert resp.address.area_name is not None
print(f"19. Area name: {resp.address.area_name}")

# 20. Check if all pizza names are capitalized correctly
assert all(pizza.name.istitle() for pizza in resp.order.order_list)
print(f"20. All pizza names are correctly capitalized: {all(pizza.name.istitle() for pizza in resp.order.order_list)}")