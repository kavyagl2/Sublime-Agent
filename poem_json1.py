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

# Define tools for poem generator
poem_generator = "poemgenerator"
tools = [
    {
        "type": "function",
        "function":{
        "name": poem_generator,
        "description": f"Generate a poem with specified details.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "style": {"type": "string"},
                "mood": {"type": "string"},
                "purpose": {"type": "string"},
                "tone": {"type": "string"},
                "content": {
                    "type": "string",
                    "description": "You generate the poem as per the specification above."}
            },
            "required": ["content"]
        }
    },
    }
]

def generate_poem(prompt, style, mood, purpose, tone):
    """Generate a poem with specified details."""
    prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative poet."},
            {"role": "user", "content": prompt_details + " Respond in json format."}
        ],
        response_format={"type": "json_object"},
        tools=tools,
        tool_choice="auto",
    )
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)["content"]
    return function_args

def trim_poem(function_args):
    """Trim a poem by merging alternate lines."""
    lines = function_args.split("\n")
    trimmed_lines = [lines[i] + " " + lines[i+1] for i in range(0, len(lines), 2)]
    trimmed_poem = "\n".join(trimmed_lines)
    return trimmed_poem

def recapitalize(text):
    """Capitalize text."""
    capitalized_text = text.upper()
    return capitalized_text

def decapitalize(text):
    """Decapitalize text."""
    decapitalized_text = text.lower()
    return decapitalized_text

# Define tools for handling poem query
poem_query = "poemquery"
tools = [
    {
        "type": "function",
        "function":{
        "name": poem_query,
        "description": f"Handle queries about the generated poem.",
        "parameters": {
            "type": "object",
            "properties": {
                "poem": {"type": "string"},
                "user_query": {"type": "string"},
                "content": {
                    "type": "string",
                    "description": "You handle the queries aprt from trimming, generating, capitalizing or decapitalizing the poem and returns back the answer.",
                    },
            },
            "required": ["content"]
        }
    },
    }
]

def handle_poem_query(poem: str, user_query: str) -> str:
    """Handle a poem query."""
    prompt = f"Here is a poem:\n\n{poem}\n\nThe user has a question about the poem: {user_query}\n\nAnswer the question in a helpful manner:"
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes poems."},
            {"role": "user", "content": prompt+ "Respond in json format."}
        ],
        response_format={"type": "json_object"},
        tools=tools,
        tool_choice="auto",
    )
    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return (function_args["content"])

def determine_intent(user_query: str) -> list:
    determineintent = "intentdetermination"
    """Determine the intent of the user's query."""
    tools = [
        {
            "type": "function",
            "name": determineintent,
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
    ]
    messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant that classifies user queries into categories.
            Available categories: 'poem generation', 'trimming poem', 'capitalize','decapitalize','poem query'""",
        },
        {
            "role": "user",
            "content": user_query + "Respond in json format.",
        },
    ]

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        response_format={"type": "json_object"},
        tools=tools,
        tool_choice="auto",
    )

    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)["categories"]
    return (function_args)

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
            style = st.selectbox("Style:", ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"], key="select_style")
            mood = st.selectbox("Mood:", ["happy", "sad", "romantic", "inspirational", "nostalgic"], key="select_mood")
            tone = st.selectbox("Tone:", ["formal", "informal", "serious", "humorous", "sentimental", "playful"], key="select_tone")
            purpose = st.selectbox(
                "Purpose:",
                [
                    "a gift", "personal reflection", "a celebration", "a memorial", "a story",
                    "parents", "siblings", "lovers", "friends", "children",
                    "colleagues", "a special occasion", "a wedding", "an anniversary",
                    "a birthday", "a graduation", "a farewell", "encouragement",
                    "appreciation", "apology", "condolence", "retirement",
                    "a boss", "a team manager", "professional recognition", "a work anniversary", "leisure time"
                ], key="select_purpose"
            )

            # Generate poem button
            if st.session_state.style and st.session_state.mood and st.session_state.purpose and st.session_state.tone:
                if st.button("Generate Poem", key="generate_button"):
                    prompt = user_query
                    poem = generate_poem(prompt, style, mood, purpose, tone)
                    st.session_state.generated_poem = poem
                    st.session_state.poem_state = "original"
                    st.session_state.actions_done.append("generate a poem")
                    unique_id = str(uuid.uuid4())
                    st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": poem})
                    st.write("Sublime Agent:")
                    st.write(poem)

        if "trim a poem" in st.session_state.intents and "trim a poem" not in st.session_state.actions_done and st.session_state.generated_poem:
            st.write("Sublime Agent: Trimming the poem as requested...")
            trimmed_poem = trim_poem(st.session_state.generated_poem)
            st.session_state.generated_poem = trimmed_poem
            st.session_state.poem_state = "trimmed"
            st.session_state.actions_done.append("trim a poem")
            unique_id = str(uuid.uuid4())
            st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": trimmed_poem})
            st.write("Sublime Agent:")
            st.write(trimmed_poem)

        if "capitalize text" in st.session_state.intents and "capitalize text" not in st.session_state.actions_done and st.session_state.generated_poem:
            st.write("Sublime Agent: Capitalizing the text as requested...")
            capitalized_text = recapitalize(st.session_state.generated_poem)
            st.session_state.generated_poem = capitalized_text
            st.session_state.poem_state = "capitalized"
            st.session_state.actions_done.append("capitalize text")
            unique_id = str(uuid.uuid4())
            st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": capitalized_text})
            st.write("Sublime Agent:")
            st.write(capitalized_text)

        if "decapitalize text" in st.session_state.intents and "decapitalize text" not in st.session_state.actions_done and st.session_state.generated_poem:
            st.write("Sublime Agent: Decapitalizing the text as requested...")
            decapitalized_text = decapitalize(st.session_state.generated_poem)
            st.session_state.generated_poem = decapitalized_text
            st.session_state.poem_state = "decapitalized"
            st.session_state.actions_done.append("decapitalize text")
            unique_id = str(uuid.uuid4())
            st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": decapitalized_text})
            st.write("Sublime Agent:")
            st.write(decapitalized_text)

        if "poem query" in st.session_state.intents and st.session_state.generated_poem:
            st.write("Sublime Agent: Answering your poem query...")
            poem_query_response = handle_poem_query(st.session_state.generated_poem, user_query)
            unique_id = str(uuid.uuid4())
            st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": poem_query_response})
            st.write("Sublime Agent:")
            st.write(poem_query_response)

    # Display conversation log
        st.header("Conversation Log")
        for message in st.session_state.conversation_log:
            if message['role'] == "user":
                st.text_area("You:", message['content'], key=message['id'])
            elif message['role'] == "system":
                st.text_area("Sublime Agent:", message['content'], key=message['id'])

if __name__ == "__main__":
    main()
