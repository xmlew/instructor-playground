# Structured Output Generation with Instructor and Claude

This repository demonstrates how to use the Instructor library with Anthropic's Claude AI model to generate structured outputs from natural language inputs. It includes various examples of parsing and structuring complex information.

## Overview

The Instructor library allows us to define Pydantic models that specify the structure we want our output data to have. We then use these models with Claude to parse natural language inputs and return structured, typed data.

## Prerequisites

- Python 3.7+
- An Anthropic API key

## Installation

1. Clone this repository
2. Install the required dependencies
3. Create a `.env` file in the root directory and add your Anthropic API key

## Usage

Each example in this repository follows a similar pattern:

1. Define Pydantic models to specify the desired output structure.
2. Create an Instructor-patched Anthropic client.
3. Send a prompt to Claude, specifying the response model.
4. Process and validate the structured output.

Further documentation can be found at https://python.useinstructor.com/. Many thanks to the team.
