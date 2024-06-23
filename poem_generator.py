import streamlit as st
import openai
from dotenv import load_dotenv
import os
import uuid

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate a poem from a prompt with specified details
def generate_poem(prompt, style=None, mood=None, purpose=None, tone=None):
    prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a creative poet."},
            {"role": "user", "content": prompt_details}
        ]
    )
    poem = response.choices[0].message.content.strip()
    return poem, "This poem is an original creation by GPT-4"

# Function to manually trim the poem by merging alternate lines
def trim_poem(poem):
    lines = poem.strip().split('\n')
    trimmed_poem = []
    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            trimmed_poem.append(lines[i] + " " + lines[i + 1])
        else:
            trimmed_poem.append(lines[i])
    return '\n'.join(trimmed_poem)

# Function to recapitalize text following "capitalize text"
def recapitalize(text):
    command = "capitalize text"
    text_to_capitalize = text.split(command)[-1].strip()
    return text_to_capitalize.upper()

# Function to decapitalize text following "decapitalize text"
def decapitalize(text):
    command = "decapitalize text"
    text_to_decapitalize = text.split(command)[-1].strip()
    return text_to_decapitalize.lower()

# Function to determine the intent of the user's query
def determine_intent(user_query):
    prompt = f"Classify the following user query into one of these categories: generate a poem, trim a poem, capitalize text, decapitalize text, general query.\n\nUser query: {user_query}\n\nCategory:"
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that classifies user queries."},
            {"role": "user", "content": prompt}
        ]
    )
    intent = response.choices[0].message.content.strip().lower()
    return intent

# Main Streamlit app
def main():
    st.title("Poetic to Phoenix: A Versatile AI Poet")

    # Initialize session state variables
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    if "intent" not in st.session_state:
        st.session_state.intent = None

    # User input for query
    user_query = st.text_input("You:", key="user_query")

    # Handle user submission
    if st.button("Send", key="submit_button"):
        unique_id = str(uuid.uuid4())
        st.session_state.conversation_log.append({"id": unique_id, "role": "user", "content": user_query})
        st.session_state.intent = determine_intent(user_query)

    # Handle intents
    if st.session_state.intent == "generate a poem":
        st.write("Poetic to Phoenix: Processing your request to generate a poem...")
        st.write("Please specify the poem details below:")
        # Dropdowns for poem details
        st.session_state.style = st.selectbox("Style:", ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"], key="select_style")
        st.session_state.mood = st.selectbox("Mood:", ["happy", "sad", "romantic", "inspirational", "nostalgic"], key="select_mood")
        st.session_state.tone = st.selectbox("Tone:", ["formal", "informal", "serious", "humorous", "sentimental", "playful"], key="select_tone")
        st.session_state.purpose = st.selectbox(
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
                poem, source = generate_poem(prompt, style=st.session_state.style, mood=st.session_state.mood,
                                             purpose=st.session_state.purpose, tone=st.session_state.tone)
                unique_id = str(uuid.uuid4())
                st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": poem})
                st.write("Poetic to Phoenix:")
                st.write(poem)
                st.caption(f"Source: {source}")

    elif st.session_state.intent == "trim a poem":
        st.write("Poetic to Phoenix: Trimming the poem as requested...")
        # Find the most recent poem generated in the conversation log
        recent_poem = ""
        for message in reversed(st.session_state.conversation_log):
            if message['role'] == "system" and message['content']:
                recent_poem = message['content']
                break

        if recent_poem:
            trimmed_poem = trim_poem(recent_poem)
            unique_id = str(uuid.uuid4())
            st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": trimmed_poem})
            st.write("Poetic to Phoenix:")
            st.write(trimmed_poem)
        else:
            st.write("Poetic to Phoenix: Sorry, I couldn't find a poem to trim.")

    elif st.session_state.intent == "capitalize text":
        st.write("Poetic to Phoenix: Capitalizing the text as requested...")
        # Find the most recent system message in the conversation log (assumed to be the poem)
        recent_message = None
        for message in reversed(st.session_state.conversation_log):
            if message['role'] == "system":
                recent_message = message
                break
        
        if recent_message:
            capitalized_text = recapitalize(recent_message['content'])
            unique_id = str(uuid.uuid4())
            st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": capitalized_text})
            st.write("Poetic to Phoenix:")
            st.write(capitalized_text)
        else:
            st.write("Poetic to Phoenix: Sorry, I couldn't find text to capitalize.")

    elif st.session_state.intent == "decapitalize text":
        st.write("Poetic to Phoenix: Decapitalizing the text as requested...")
        # Find the most recent system message in the conversation log (assumed to be the poem)
        recent_message = None
        for message in reversed(st.session_state.conversation_log):
            if message['role'] == "system":
                recent_message = message
                break
        
        if recent_message:
            decapitalized_text = decapitalize(recent_message['content'])
            unique_id = str(uuid.uuid4())
            st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": decapitalized_text})
            st.write("Poetic to Phoenix:")
            st.write(decapitalized_text)
        else:
            st.write("Poetic to Phoenix: Sorry, I couldn't find text to decapitalize.")

    elif st.session_state.intent == "general query":
        st.write("Poetic to Phoenix: Routing your query to GPT...")
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant. Take user query and output relevant answer. If you don't know the answer, like a good AI assistant say, 'Sorry! I don't know the answer!'"},
                {"role": "user", "content": user_query}
            ]
        )
        gpt_response = response.choices[0].message.content.strip()
        unique_id = str(uuid.uuid4())
        st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": gpt_response})
        st.write("Poetic to Phoenix:")
        st.write(gpt_response)

    # Display conversation log
    st.header("Conversation Log")
    for message in st.session_state.conversation_log:
        if message['role'] == "user":
            st.text_area("You:", message['content'], key=message['id'])
        elif message['role'] == "system":
            st.text_area("Poetic to Phoenix:", message['content'], key=message['id'])

if __name__ == "__main__":
    main()
