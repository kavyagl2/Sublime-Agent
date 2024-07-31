import streamlit as st
from openai import OpenAI
import openai
import json

client = OpenAI()

# Function to generate poem
def generate_poem(prompt, default_style=None, default_mood=None, default_purpose=None, default_tone=None):
    st.subheader("Customize Your Poem")
    
    style = st.selectbox("Style:", ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"], key = "select_style",
                        index=0 if not default_style else ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"].index(default_style))
    mood = st.selectbox("Mood:", ["happy", "sad", "romantic", "inspirational", "nostalgic"], key = "select_mood",
                        index=0 if not default_mood else ["happy", "sad", "romantic", "inspirational", "nostalgic"].index(default_mood))
    purpose = st.selectbox("Purpose:", [
        "a gift", "personal reflection", "a celebration", "a memorial", "a story",
        "parents", "siblings", "lovers", "friends", "children",
        "colleagues", "a special occasion", "a wedding", "an anniversary",
        "a birthday", "a graduation", "a farewell", "encouragement",
        "appreciation", "apology", "condolence", "retirement",
        "a boss", "a team manager", "professional recognition", "a work anniversary", "leisure time"
    ], key = "select_purpose", index=0 if not default_purpose else [
        "a gift", "personal reflection", "a celebration", "a memorial", "a story",
        "parents", "siblings", "lovers", "friends", "children",
        "colleagues", "a special occasion", "a wedding", "an anniversary",
        "a birthday", "a graduation", "a farewell", "encouragement",
        "appreciation", "apology", "condolence", "retirement",
        "a boss", "a team manager", "professional recognition", "a work anniversary", "leisure time"
    ].index(default_purpose))
    tone = st.selectbox("Tone:", ["formal", "informal", "serious", "humorous", "sentimental", "playful"],key = "select_tone",
                        index=0 if not default_tone else ["formal", "informal", "serious", "humorous", "sentimental", "playful"].index(default_tone))
    
    if st.button("Generate Poem", key="generate_button"):
        if all([style, mood, purpose, tone]):
            prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative poet."},
                    {"role": "user", "content": prompt_details}
                ]
            )
            poem = response.choices[0].message.content.strip()
            st.session_state.last_poem = poem
            st.session_state.conversation_log.append({"role": "assistant", "content": poem})

        else:
            st.warning("Please select all customization options before generating the poem.")

# Function to trim the poem
def trim_poem():
    if st.session_state.last_poem:
        poem = st.session_state.last_poem
        lines = poem.strip().split('\n')
        trimmed_poem = [
            lines[i] + " " + lines[i + 1] if i + 1 < len(lines) else lines[i]
            for i in range(0, len(lines), 2)
        ]
        trimmed_poem = '\n'.join(trimmed_poem)
        st.session_state.last_poem = trimmed_poem
        st.session_state.conversation_log.append({"role": "assistant", "content": trimmed_poem})
    else:
        st.session_state.conversation_log.append({"role": "assistant", "content": "No poem available to trim."})

# Function to recapitalize text
def recapitalize():
    if st.session_state.last_poem:
        recapitalized_text = st.session_state.last_poem.upper()
        st.session_state.last_poem = recapitalized_text
        st.session_state.conversation_log.append({"role": "assistant", "content": recapitalized_text})
    else:
        st.session_state.conversation_log.append({"role": "assistant", "content": "No poem text to recapitalize!"})

# Function to decapitalize text
def decapitalize():
    if st.session_state.last_poem:
        decapitalized_text = st.session_state.last_poem.lower()
        st.session_state.last_poem = decapitalized_text
        st.session_state.conversation_log.append({"role": "assistant", "content": decapitalized_text})
    else:
        st.session_state.conversation_log.append({"role": "assistant", "content": "No poem text to decapitalize!"})

# Function to handle queries about the generated poem
def handle_poem_query(user_query):
    if st.session_state.last_poem:
        poem = st.session_state.last_poem
        prompt = f"Here is a poem:\n\n{poem}\n\nThe user has a question about the poem: {user_query}\n\nAnswer the question in a helpful manner."
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes poems."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
        st.session_state.conversation_log.append({"role": "assistant", "content": answer})
    else:
        st.session_state.conversation_log.append({"role": "assistant", "content": "No poem available to analyze."})

def conversation(user_query):
    messages = [
        {"role": "system", "content": "You are a poetic agent who analyzes the user query and then accordingly routes their query to available functions and generates the output."},
        {"role": "user", "content": user_query}
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_poem",
                "description": "Generate a poem with specified details: style, mood, purpose, tone.",
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
                "description": "Trim a poem by merging alternate lines.",
            }
        },
        {
            "type": "function",
            "function": {
                "name": "recapitalize",
                "description": "Capitalize the text as required and turn it into uppercase.",
            }
        },
        {
            "type": "function",
            "function": {
                "name": "decapitalize",
                "description": "Decapitalize the text as required and turn it into lowercase.",
            }
        },
        {
            "type": "function",
            "function": {
                "name": "handle_poem_query",
                "description": "Handles user query when user prompts a different action to be performed apart from trimming, capitalizing, decapitalizing, and generating a poem.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_query": {"type": "string"}
                    },
                    "required": ["user_query"]
                }
            }
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        tools=tools,
        tool_choice="required"
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    available_functions = {
        "generate_poem": generate_poem,
        "trim_poem": trim_poem,
        "recapitalize": recapitalize,
        "decapitalize": decapitalize,
        "handle_poem_query": handle_poem_query
    }

    if not tool_calls:
        st.write("No tool calls were made.")
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)

    return function_to_call, function_args

# Streamlit app
def main():
    st.title("Poetic AI Agent")

    # Initialize session state variables
    if 'last_poem' not in st.session_state:
        st.session_state.last_poem = ""
    if 'conversation_log' not in st.session_state:
        st.session_state.conversation_log = []

    user_query = st.text_input("Enter your query:")

    if user_query:
        function_to_call, function_args = conversation(user_query)
        st.session_state.conversation_log.append({"role": "user", "content": user_query})

        if function_to_call == generate_poem:
            default_style = function_args.get("style")
            default_mood = function_args.get("mood")
            default_purpose = function_args.get("purpose")
            default_tone = function_args.get("tone")
            prompt = function_args.get("prompt")
            generate_poem(prompt, default_style, default_mood, default_purpose, default_tone)

        elif function_to_call == trim_poem:
            trim_poem()

        elif function_to_call == recapitalize:
            recapitalize()

        elif function_to_call == decapitalize:
            decapitalize()

        elif function_to_call == handle_poem_query:
            handle_poem_query(user_query)

    # Display conversation log
    st.header("Conversation Log")
    for i, message in enumerate(st.session_state.conversation_log):
        key = f"message_{i}"
        if message['role'] == "user":
            st.text_area(f"You:", message['content'], key=key)
        elif message['role'] == "assistant":
            st.text_area(f"Assistant:", message['content'], key=key)

if __name__ == "__main__":
    main()
