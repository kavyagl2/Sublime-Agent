import streamlit as st
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate a poem from a prompt
def generate_poem(prompt, style=None, mood=None, purpose=None, tone=None):
    prompt_details = f"Create a {style} poem with a {mood} mood for {purpose} in a {tone} tone:\n{prompt}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a creative poet."},
            {"role": "user", "content": prompt_details}
        ]
    )
    poem = response.choices[0].message.content.strip()
    return poem, "This poem is an original creation by GPT-3.5"

# Function to trim the poem
def trim_poem(poem):
    lines = poem.split('\n')
    trimmed_poem = []
    for i in range(0, len(lines) - 1, 2):
        trimmed_poem.append(lines[i] + " " + lines[i + 1])
    if len(lines) % 2 != 0:
        trimmed_poem.append(lines[-1])
    return '\n'.join(trimmed_poem)

# Function to convert text to lowercase
def convert_to_lowercase(text):
    return text.lower()

# Function to recapitalize text
def recapitalize(text):
    sentences = text.split('. ')
    recapitalized_text = '. '.join(sentence.capitalize() for sentence in sentences)
    return recapitalized_text

# Function to apply themes based on poem characteristics
def apply_theme(poem):
    keywords = ["happy", "sad", "romantic", "inspirational", "nostalgic"]
    for keyword in keywords:
        if keyword in poem.lower():
            if keyword == "happy":
                st.markdown(
                    """
                    <style>
                    .reportview-container {
                        background: linear-gradient(to right, #7F00FF, #E100FF);
                        color: white;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            elif keyword == "sad":
                st.markdown(
                    """
                    <style>
                    .reportview-container {
                        background: linear-gradient(to right, #C9D6FF, #E2E2E2);
                        color: black;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            elif keyword == "romantic":
                st.markdown(
                    """
                    <style>
                    .reportview-container {
                        background: linear-gradient(to right, #FF6B6B, #FFE66D);
                        color: black;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            elif keyword == "inspirational":
                st.markdown(
                    """
                    <style>
                    .reportview-container {
                        background: linear-gradient(to right, #5F939A, #F7F7F7);
                        color: black;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
            elif keyword == "nostalgic":
                st.markdown(
                    """
                    <style>
                    .reportview-container {
                        background: linear-gradient(to right, #FFB6B9, #FFEE93);
                        color: black;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )

# Main Streamlit app
def main():
    st.title("Poetic to Pheonix, I can do it all!")

    selected_service = st.selectbox("Choose a service:", ["Generate Poem", "Recapitalize Text", "None of the above"])

    if selected_service == "Generate Poem":
        style = st.selectbox("Select poem style:", ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"])
        mood = st.selectbox("Select the mood of the poem:", ["happy", "sad", "romantic", "inspirational", "nostalgic"])
        tone = st.selectbox("Select the tone of the poem:", ["formal", "informal", "serious", "humorous", "sentimental", "playful"])
        purpose = st.selectbox(
            "Select the purpose of the poem:",
            [
                "a gift", "personal reflection", "a celebration", "a memorial", "a story", 
                "parents", "siblings", "lovers", "friends", "children", 
                "colleagues", "a special occasion", "a wedding", "an anniversary", 
                "a birthday", "a graduation", "a farewell", "encouragement", 
                "appreciation", "apology", "condolence", "retirement",
                "a boss", "a team manager", "professional recognition", "a work anniversary", "leisure time"
            ]
        )

        user_prompt = st.text_input("Enter your prompt:")
        if st.button("Generate Poem"):
            poem, source = generate_poem(user_prompt, style=style, mood=mood, purpose=purpose, tone=tone)
            st.subheader("Generated Poem:")
            st.write(poem)
            st.caption(f"Source: {source}")

            apply_theme(poem)

            next_option = st.radio("Would you like to:", ["Generate another poem", "Trim the existing poem", "None of the above"])
            if next_option == "Generate another poem":
                poem, source = generate_poem(user_prompt, style=style, mood=mood, purpose=purpose, tone=tone)
                st.subheader("Generated Poem:")
                st.write(poem)
                st.caption(f"Source: {source}")

            elif next_option == "Trim the existing poem":
                trimmed_poem = trim_poem(poem)
                st.subheader("Trimmed Poem:")
                st.write(trimmed_poem)

            else:
                st.write("Thank you for using the Poem Generator! Have a lovely day!")

    elif selected_service == "Recapitalize Text":
        text = st.text_area("Enter the text to recapitalize:")
        if text and st.button("Recapitalize"):
            recapitalized_text = recapitalize(text)
            st.subheader("Recapitalized Text:")
            st.write(recapitalized_text)
    
    elif selected_service == "None of the above":
        user_query = st.text_input("Enter you query: ")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", 
                 "content": "You are a helpful assistant. Take user query and output relevant answer. If you don't know the answer, like a good AI assitant say, 'Sorry! I don't know the answer!'"},
                {"role": "user", "content": user_query}
            ]
        )
        st.subheader("Response from GPT:")
        st.write(response.choices[0].message.content.strip())

if __name__ == "__main__":
    main()
