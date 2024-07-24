import streamlit as st
from openai import OpenAI
import openai
import json

client = OpenAI()

# Function to generate poem
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
    return poem

# Function to trim the poem
def trim_poem(poem):
    lines = poem.strip().split('\n')
    trimmed_poem = []
    for i in range(0, len(lines), 2):
        if i + 1 < len(lines):
            trimmed_poem.append(lines[i] + " " + lines[i + 1])
        else:
            trimmed_poem.append(lines[i])
    return '\n'.join(trimmed_poem)

# Function to recapitalize text
def recapitalize(text):
    return text.upper()

# Function to decapitalize text
def decapitalize(text):
    return text.lower()

# Function to handle queries about the generated poem
def handle_poem_query(poem, user_query):
    prompt = f"Here is a poem:\n\n{poem}\n\nThe user has a question about the poem: {user_query}\n\nAnswer the question in a helpful manner:"
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes poems."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response.choices[0].message.content.strip()
    return answer

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
                "description": "Handles user query when user prompts a different action to be performed apart from trimming, recapitalizing, decapitalizing, and generating a poem.",
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
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
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
        print("tool call broke")
    results = []
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        result = function_to_call(**function_args)
        results.append({"function": function_name, "result": result})

    return results

# Streamlit app
def main():
    st.title("Poetic AI Agent")
    
    # State management for the last generated poem
    if 'last_poem' not in st.session_state:
        st.session_state.last_poem = ""

    user_query = st.text_input("Enter your query:")

    if user_query:
        conversation_results = conversation(user_query)
        for result in conversation_results:
            function_name = result['function']
            result_content = result['result']
            
            if function_name == "generate_poem":
                st.session_state.last_poem = result_content
                st.write("Generated Poem:")
                st.write(result_content)
                
            elif function_name == "trim_poem":
                st.session_state.last_poem = result_content
                st.write("Trimmed Poem:")
                st.write(result_content)
                
            elif function_name == "recapitalize":
                st.session_state.last_poem = result_content
                st.write("Recapitalized Text:")
                st.write(result_content)
                
            elif function_name == "decapitalize":
                st.session_state.last_poem = result_content
                st.write("Decapitalized Text:")
                st.write(result_content)
                
            elif function_name == "handle_poem_query":
                st.write("Answer to Query:")
                st.write(result_content)

    if 'generate_poem' in user_query:
        st.subheader("Customize Your Poem")
        style = st.selectbox("Style:", ["classic", "modern", "haiku", "free verse", "sonnet", "limerick"], key="select_style")
        mood = st.selectbox("Mood:", ["happy", "sad", "romantic", "inspirational", "nostalgic"], key="select_mood")
        purpose = st.selectbox("Purpose:",
                              [
                                  "a gift", "personal reflection", "a celebration", "a memorial", "a story",
                                  "parents", "siblings", "lovers", "friends", "children",
                                  "colleagues", "a special occasion", "a wedding", "an anniversary",
                                  "a birthday", "a graduation", "a farewell", "encouragement",
                                  "appreciation", "apology", "condolence", "retirement",
                                  "a boss", "a team manager", "professional recognition", "a work anniversary", "leisure time"
                              ], key="select_purpose")
        tone = st.selectbox("Tone:", ["formal", "informal", "serious", "humorous", "sentimental", "playful"], key="select_tone")
        prompt = st.text_area("Enter the poem prompt:")

        if st.button("Generate Poem"):
            poem = generate_poem(prompt, style, mood, purpose, tone)
            st.session_state.last_poem = poem
            st.write("Generated Poem:")
            st.write(poem)

    if 'trim_poem' in user_query:
        st.subheader("Trim the Poem")
        if st.button("Trim Poem"):
            if st.session_state.last_poem:
                trimmed_poem = trim_poem(st.session_state.last_poem)
                st.session_state.last_poem = trimmed_poem
                st.write("Trimmed Poem:")
                st.write(trimmed_poem)
            else:
                st.write("No poem available to trim.")

    if 'recapitalize' in user_query:
        st.subheader("Recapitalize Text")
        text = st.session_state.last_poem
        if st.button("Recapitalize"):
            recapitalized_text = recapitalize(text)
            st.session_state.last_poem = recapitalized_text
            st.write("Recapitalized Text:")
            st.write(recapitalized_text)

    if 'decapitalize' in user_query:
        st.subheader("Decapitalize Text")
        text = st.session_state.last_poem
        if st.button("Decapitalize"):
            decapitalized_text = decapitalize(text)
            st.session_state.last_poem = decapitalized_text
            st.write("Decapitalized Text:")
            st.write(decapitalized_text)

    if 'handle_poem_query' in user_query:
        st.subheader("Handle Poem Query")
        poem = st.session_state.last_poem
        if st.button("Handle Query"):
            answer = handle_poem_query(poem, user_query)
            st.write("Answer to Query:")
            st.write(answer)

if __name__ == "__main__":
    main()
