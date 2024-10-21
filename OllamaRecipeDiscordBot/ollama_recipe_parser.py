# ollama_recipe_parser.py
import logging
logging.basicConfig(level=logging.INFO)

import os
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Define your template and model
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully:"

    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}."
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response."
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
    "5. **Ignore Advertisements:** Exclude any information that is clearly an advertisement or promotional content."
    "6. **Focus on Recipes:** Only include text related to cooking or baking recipes. Ignore blog comments, personal anecdotes, and non-recipe content."
    "7. **Structured Recipe Components:** Ensure the output is structured with the recipe name, ingredients list, and preparation methods."
    "8. **Preserve Paragraphs:** Maintain the original paragraphs and formatting, including any instructions within parentheses."
    "9. **Exclude Irrelevant Keywords:** Exclude content with keywords like 'blog', 'story', 'personal', 'ad', or 'sponsored'."
    "10. **Example Format:** Here's an example format: Name: [Recipe Name], Ingredients: [List Ingredients], Methods: [List Steps]."
    "11. **Multiple Recipes:** If you detect multiple recipe headings, select the one that matches or is similar to the page title."
    "13. **Length Constraints:** Ensure the extracted content fits within 2000 characters, trimming unnecessary details if necessary."
    "14. **Sequential Extraction:** Follow this sequence: Identify title → Extract ingredients → Extract preparation steps."
    "15. **Accurate Quantities:** Ensure that the quantities of ingredients match exactly as they appear on the webpage."
    "16. **Primary Recipe Focus:** Focus solely on the primary recipe, often indicated by the most prominent heading or the page title."
    "17. **HTML Table Handling:** Extract ingredient quantities and descriptions from HTML table rows (`<tr>`) within `<table>` tags."
    "18. **Central Content Focus:** Prioritize content in the central section of the page, especially for blog posts, to avoid extracting irrelevant side content."
    "19. **Content Density:** Focus on dense sections of text that typically contain the main recipe components, rather than dispersed information across the page."
)

# Description of what to parse
parse_description = (
    "Give me the recipe on this webpage."
    "The Name of the recipe should be bold."
    "Ingredients shouldn't be next to each other."
    "If anything is structured in subparts, those parts should be preserved and they should be given separate paragraphs."
    "Keep everything in the language of the site."
    "Don't create new information, only use what is actualy there. Especially with ingredient quantities!"
    "Focus on dense sections of text that typically contain the main recipe components, rather than dispersed information across the page."
    "Ensure the lenght of the response is no longer than 2000 characters, trimming if needed."
)
 
# Initialize the model and prompt template
load_dotenv()
model_name = os.getenv("LLAMA_MODEL_NAME")
model = OllamaLLM(model=model_name)
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Function to parse content using Ollama
def parse_with_ollama(dom_chunks):
    """
    Parse content chunks using the Ollama model.

    Parameters:
    dom_chunks (list): List of HTML content chunks to parse.

    Returns:
    str: Parsed recipe details as a single string.
    """
    parsed_results = []

    # Iterate over chunks of DOM content
    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            response = chain.invoke(
                {"dom_content": chunk, "parse_description": parse_description}
            )
            logging.info(f"Parsed batch {i} of {len(dom_chunks)}")
            parsed_results.append(response)
        except Exception as e:
            logging.error(f"Error parsing batch {i}: {e}")
    
    return "\n".join(parsed_results)
