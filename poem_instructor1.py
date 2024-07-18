import streamlit as st
import openai
from dotenv import load_dotenv
import os
import uuid
import instructor
from pydantic import BaseModel, ValidationError, field_validator, Field
from instructor.exceptions import InstructorRetryException
from tenacity import Retrying, retry_if_not_exception_type, stop_after_attempt

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

client = instructor.from_openai(openai.OpenAI(), mode=instructor.Mode.TOOLS)

# Pydantic model for poem validation
class PoemDetails(BaseModel):
    style: str = Field(..., description="The style of the poem (e.g., classic, modern, haiku, etc.)")
    mood: str = Field(..., description="The mood of the poem (e.g., happy, sad, romantic, etc.)")
    purpose: str = Field(..., description="The purpose of the poem (e.g., gift, reflection, celebration, etc.)")
    tone: str = Field(..., description="The tone of the poem (e.g., formal, informal, serious, etc.)")
    prompt: str = Field(..., description="The prompt or theme of the poem")

    @field_validator('style')
    def validate_style(cls, v):
        if v.lower() not in ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"]:
            raise ValueError('Invalid poem style. Must be one of: classic, modern, haiku, free verse, sonnet, limerick')
        return v

    @field_validator('mood')
    def validate_mood(cls, v):
        if v.lower() not in ["happy", "sad", "romantic", "inspirational", "nostalgic"]:
            raise ValueError('Invalid poem mood. Must be one of: happy, sad, romantic, inspirational, nostalgic')
        return v

    @field_validator('purpose')
    def validate_purpose(cls, v):
        valid_purposes = [
            "a gift", "personal reflection", "a celebration", "a memorial", "a story",
            "parents", "siblings", "lovers", "friends", "children",
            "colleagues", "a special occasion", "a wedding", "an anniversary",
            "a birthday", "a graduation", "a farewell", "encouragement",
            "appreciation", "apology", "condolence", "retirement",
            "a boss", "a team manager", "professional recognition", "a work anniversary", "leisure time"
        ]
        if v.lower() not in valid_purposes:
            raise ValueError(f'Invalid poem purpose. Must be one of: {", ".join(valid_purposes)}')
        return v

    @field_validator('tone')
    def validate_tone(cls, v):
        if v.lower() not in ["formal", "informal", "serious", "humorous", "sentimental", "playful"]:
            raise ValueError('Invalid poem tone. Must be one of: formal, informal, serious, humorous, sentimental, playful')
        return v

# Function to handle server errors
def handle_server_error(exception):
    st.error("There is some problem with the server. Please retry.")
    if st.button("Retry"):
        st.experimental_rerun()

# Function to determine the intents of the user's query
def determine_intent(user_query):
    prompt = f"Classify the following user query into one or more of these categories: generate a poem, trim a poem, capitalize text, decapitalize text, poem query, general query.\n\nUser query: {user_query}\n\nCategories (comma-separated if multiple):"
    for attempt in Retrying(stop=stop_after_attempt(3), retry=retry_if_not_exception_type(InstructorRetryException)):
        with attempt:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies user queries."},
                    {"role": "user", "content": prompt}
                ],
            )
            intents = response.choices[0].message.content.strip().lower().replace("then", ",").replace("and", ",").split(', ')
            return intents

# Function to generate a poem from a prompt with specified details
def generate_poem(prompt, style=None, mood=None, purpose=None, tone=None):
    prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"
    for attempt in Retrying(stop=stop_after_attempt(3), retry=retry_if_not_exception_type(InstructorRetryException)):
        with attempt:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative poet."},
                    {"role": "user", "content": prompt_details}
                ],
            )
            poem = response.choices[0].message.content.strip()
            return poem, "This poem is an original creation by GPT-4"

# Function to handle queries about the generated poem
def handle_poem_query(poem, user_query):
    prompt = f"Here is a poem:\n\n{poem}\n\nThe user has a question about the poem: {user_query}\n\nAnswer the question in a helpful manner:"
    for attempt in Retrying(stop=stop_after_attempt(3), retry=retry_if_not_exception_type(InstructorRetryException)):
        with attempt:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes poems."},
                    {"role": "user", "content": prompt}
                ],
            )
            answer = response.choices[0].message.content.strip()
            return answer

# Function to recapitalize text following "capitalize text"
def recapitalize(text):
    return text.upper()

# Function to decapitalize text following "decapitalize text"
def decapitalize(text):
    return text.lower()

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

    # User input for query using Pydantic
    user_query = st.text_input("You:")

    # Handle user submission
    if st.button("Send"):
        unique_id = str(uuid.uuid4())
        st.session_state.conversation_log.append({"id": unique_id, "role": "user", "content": user_query})
        st.session_state.intents = determine_intent(user_query)

    # Handle intents
    if st.session_state.intents:
        try:
            if "generate a poem" in st.session_state.intents and "generate a poem" not in st.session_state.actions_done:
                st.write("Sublime Agent: Processing your request to generate a poem...")
                st.write("Please specify the poem details below:")
                # Dropdowns for poem details
                st.session_state.style = st.selectbox("Style:", ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"])
                st.session_state.mood = st.selectbox("Mood:", ["happy", "sad", "romantic", "inspirational", "nostalgic"])
                st.session_state.tone = st.selectbox("Tone:", ["formal", "informal", "serious", "humorous", "sentimental", "playful"])
                st.session_state.purpose = st.selectbox(
                    "Purpose:",
                    [
                        "a gift", "personal reflection", "a celebration", "a memorial", "a story",
                        "parents", "siblings", "lovers", "friends", "children",
                        "colleagues", "a special occasion", "a wedding", "an anniversary",
                        "a birthday", "a graduation", "a farewell", "encouragement",
                        "appreciation", "apology", "condolence", "retirement",
                        "a boss", "a team manager", "professional recognition", "a work anniversary", "leisure time"
                    ]
                )

                # Generate poem button
                if st.session_state.style and st.session_state.mood and st.session_state.purpose and st.session_state.tone:
                    if st.button("Generate Poem"):
                        prompt = user_query
                        poem, source = generate_poem(prompt, style=st.session_state.style, mood=st.session_state.mood,
                                                    purpose=st.session_state.purpose, tone=st.session_state.tone)
                        st.session_state.generated_poem = poem
                        st.session_state.poem_state = "original"
                        st.session_state.actions_done.append("generate a poem")
                        unique_id = str(uuid.uuid4())
                        st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": poem})
                        st.write("Sublime Agent:")
                        st.write(poem)
                        st.caption(f"Source: {source}")

            if "trim a poem" in st.session_state.intents and "trim a poem" not in st.session_state.actions_done and st.session_state.generated_poem:
                st.write("Sublime Agent: Trimming the poem as requested...")
                trimmed_poem = trim_poem(st.session_state.generated_poem)
                st.session_state.generated_poem = trimmed_poem  # Update the generated poem with the trimmed version
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

            if "general query" in st.session_state.intents:
                st.write("Sublime Agent: Routing your query to GPT...")
                response = openai.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Take user query and output relevant answer. If you don't know the answer, like a good AI assistant say, 'Sorry! I don't know the answer!'"},
                        {"role": "user", "content": user_query}
                    ]
                )
                gpt_response = response.choices[0].message.content.strip()
                unique_id = str(uuid.uuid4())
                st.session_state.conversation_log.append({"id": unique_id, "role": "system", "content": gpt_response})
                st.write("Sublime Agent:")
                st.write(gpt_response)
                
        except Exception as e:
            handle_server_error(e)
        
        # Display conversation log
    st.header("Conversation Log")
    for message in st.session_state.conversation_log:
        if message['role'] == "user":
            st.text_area("You:", message['content'], key=message['id'])
        elif message['role'] == "system":
            st.text_area("Sublime Agent:", message['content'], key=message['id'])

if __name__ == "__main__":
    main()
