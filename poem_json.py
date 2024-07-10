import streamlit as st
import openai
from dotenv import load_dotenv
import os
import uuid
import json

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define tools for each function
tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_poem",
            "description": "Generate a poem with specified details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "style": {"type": "string"},
                    "mood": {"type": "string"},
                    "purpose": {"type": "string"},
                    "tone": {"type": "string"}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "trim_poem",
            "description": "Trim a given poem by merging alternate lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "poem": {"type": "string"}
                },
                "required": ["poem"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recapitalize",
            "description": "Capitalize text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "decapitalize",
            "description": "Decapitalize text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_poem_query",
            "description": "Handle queries about the generated poem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "poem": {"type": "string"},
                    "user_query": {"type": "string"}
                },
                "required": ["poem", "user_query"]
            }
        }
    }
]

# Function to generate a poem from a prompt with specified details
def generate_poem(prompt, style=None, mood=None, purpose=None, tone=None):
    prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative poet."},
            {"role": "user", "content": prompt_details}
        ],
        tools=tools,
        response_format={"type": "json_object"},
        tool_choice="required"
    )
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return (function_args.get("content")), "This poem is an original creation by GPT-4"

# Function to manually trim the poem by merging alternate lines
def trim_poem(poem):
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that trims poems."},
            {"role": "user", "content": poem}
        ],
        tools=tools,
        response_format={"type": "json_object"},
        tool_choice= "required"
    )
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return (function_args.get("trimmed_poem"))

# Function to capitalize text following "capitalize text"
def recapitalize(text):
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that capitalizes text."},
            {"role": "user", "content": text}
        ],
        tools=tools,
        response_format={"type": "json_object"},
        tool_choice="required"
    )
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return (function_args.get("capitalized_text"))

# Function to decapitalize text following "decapitalize text"
def decapitalize(text):
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that decapitalizes text."},
            {"role": "user", "content": text}
        ],
        tools=tools,
        response_format={"type": "json_object"},
        tool_choice="required"
    )
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return (function_args.get("decapitalized_text"))

# Function to handle queries about the generated poem
def handle_poem_query(poem, user_query):
    prompt = f"Here is a poem:\n\n{poem}\n\nThe user has a question about the poem: {user_query}\n\nAnswer the question in a helpful manner:"
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes poems."},
            {"role": "user", "content": prompt}
        ],
        tools=tools,
        response_format={"type": "json_object"},
        tool_choice="required"
    )
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return (function_args.get("content"))

# Function to determine the intents of the user's query using function calling
def determine_intent(user_query):
    function_name = "classify_intent"
    classify_tool = {
        "type": "function",
        "function": {
            "name": function_name,
            "description": "Classify the user's query into one or more categories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of categories for the query."
                    }
                },
                "required": ["categories"]
            }
        }
    }

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that classifies user queries into categories.",
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        tools=[classify_tool],
        tool_choice="required"
    )
    
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return (function_args.get("categories"))

# Main Streamlit app
def main():
    st.title("Sublime Agent: A Versatile AI Poet")

    # Initialize session state variables
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    if "intents" not in st.session_state:
        st.session_state.intents = None
    if "generated_poem" not in st.session_state:
        st.session_state.generated_poem = None
    if "poem_state" not in st.session_state:
        st.session_state.poem_state = "original"
    if "actions_done" not in st.session_state:
        st.session_state.actions_done = []

    # User input for query
    user_query = st.text_input("You:", key="user_query")

    # Handle user submission
    if st.button("Send", key="submit_button"):
        unique_id = str(uuid.uuid4())
        st.session_state.conversation_log.append({"id": unique_id, "role": "user", "content": user_query})
        st.session_state.intents = determine_intent(user_query)

    # Handle intents
    if st.session_state.intents:
        if "generate a poem" in st.session_state.intents and "generate a poem" not in st.session_state.actions_done:
            st.write("Sublime Agent: Processing your request to generate a poem...")
            st.write("Please specify the poem details below:")
            # Dropdowns for poem details
            st.session_state.style = st.selectbox("Style:", ["classic", "modern", "haiku", "free verse", "sonnet"], key="style")
            st.session_state.mood = st.selectbox("Mood:", ["happy", "sad", "angry", "romantic", "melancholic"], key="mood")
            st.session_state.purpose = st.selectbox("Purpose:", ["personal", "professional", "celebration", "reflection", "gift"], key="purpose")
            st.session_state.tone = st.selectbox("Tone:", ["formal", "informal", "serious", "light-hearted", "mysterious"], key="tone")

            if st.button("Generate Poem", key="generate_poem_button"):
                poem = generate_poem(user_query, st.session_state.style, st.session_state.mood, st.session_state.purpose, st.session_state.tone)
                st.session_state.generated_poem = poem
                st.session_state.actions_done.append("generate a poem")

        if st.session_state.generated_poem:
            st.write("Sublime Agent: Here is your generated poem:")
            st.write(st.session_state.generated_poem)

        if "trim the poem" in st.session_state.intents and st.session_state.generated_poem and "trim the poem" not in st.session_state.actions_done:
            st.write("Sublime Agent: Trimming the poem...")
            trimmed_poem = trim_poem(st.session_state.generated_poem)
            st.session_state.generated_poem = trimmed_poem
            st.session_state.actions_done.append("trim the poem")

        if "recapitalize" in st.session_state.intents and st.session_state.generated_poem and "recapitalize" not in st.session_state.actions_done:
            st.write("Sublime Agent: Recapitalizing the text...")
            recapitalized_text = recapitalize(st.session_state.generated_poem)
            st.session_state.generated_poem = recapitalized_text
            st.session_state.actions_done.append("recapitalize")

        if "decapitalize" in st.session_state.intents and st.session_state.generated_poem and "decapitalize" not in st.session_state.actions_done:
            st.write("Sublime Agent: Decapitalizing the text...")
            decapitalized_text = decapitalize(st.session_state.generated_poem)
            st.session_state.generated_poem = decapitalized_text
            st.session_state.actions_done.append("decapitalize")

        if "handle poem query" in st.session_state.intents and st.session_state.generated_poem and "handle poem query" not in st.session_state.actions_done:
            st.write("Sublime Agent: Handling your query about the poem...")
            response = handle_poem_query(st.session_state.generated_poem, user_query)
            st.write(response)
            st.session_state.actions_done.append("handle poem query")

    # Display conversation log
    st.header("Conversation Log")
    for message in st.session_state.conversation_log:
        if message['role'] == "user":
            st.text_area("You:", message['content'], key=message['id'])
        elif message['role'] == "system":
            st.text_area("Sublime Agent:", message['content'], key=message['id'])

if __name__ == "__main__":
    main()
