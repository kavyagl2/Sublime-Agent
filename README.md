### Overview
This Streamlit application leverages OpenAI's GPT-3.5 model to provide several text-related services, including generating poems, recapitalizing text, and responding to user queries. Users can interactively select options to generate poems of different styles, moods, tones, and purposes, recapitalize text, or get responses to their queries.

### Services Offered
1. **Generate Poem**
- Description: Allows users to generate poems based on specified style, mood, tone, and purpose.
- Options:
  
-- Choose from poem styles such as classic, modern, haiku, free verse, etc.
  
-- Select mood (happy, sad, romantic, inspirational, nostalgic).

-- Choose tone (formal, informal, serious, humorous, etc.).

-- Specify the purpose of the poem (e.g., gift, personal reflection, celebration).

2. **Recapitalize Text**
Description: Provides a function to recapitalize text input by the user.
Functionality: Users can input text and have it recapitalized according to sentence boundaries.

3. **User Query Response**
Description: Answers user queries using the GPT-3.5 model.
Usage: Users input their query, and the model provides relevant responses or informs when it cannot answer.

### Usage Instructions
1. **Selection:** Choose the service you want to use from the dropdown menu (Generate Poem, Recapitalize Text, None of the above).
2. **Options:**
- For Generate Poem: Select style, mood, tone, and purpose, then input a prompt and click Generate Poem.
- For Recapitalize Text: Input text to recapitalize and click Recapitalize.
- For None of the above: Input a query to get a response from the model.

### Technologies Used
- Streamlit: Interactive app framework.
- OpenAI GPT-3.5: Language model for generating text and answering queries.
- Python: Backend scripting language.

### Setup
- Clone the repository.
- Install dependencies using pip install -r requirements.txt.
- Create a .env file with your OpenAI API key (OPENAI_API_KEY=your_api_key).
- Run the app locally with streamlit run app.py.

### Future Enhancements
- Improve poem generation quality by fine-tuning style and coherence.
- Expand services to include more sophisticated text manipulation tasks.
- Enhance user interface and responsiveness.

### Credits
Developed by **Kavya Agrawal**.

Powered by OpenAI GPT-3.5.
