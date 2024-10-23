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
)

# Description of what to parse
parse_description = (
    "1. List the name of the Recipe found on this web page. If there are multiple recipes, only list the one that is most likely the main recipe, it is often found in <h1> tags, in the page title, or page adress. The main recipe is never found in <h3> or <h4> tags."
    "2. List all ingredients found for the Recipe in step 1, with the correct quantities. The ingredients are often found in <li> tags. Ingredients are food items. If imperial units are used, convert to metric units. Don't make up ingredients or quantities."
    "3. List all stepts for the preparation method found for the Recipe. The preparation method is commonly found after the ingredients. It is also commonly called instructions. If it contains temperature in Fahrenheit, convert to celsius. Don't make up steps. "
    "4. Keep the original language of the website. For example: If it is written in english, your recipe should be english."
    "5. Ignore information that is not part of the main recipe. Especially other recipes on the webpage, that are not complete with ingredients and preparation method. They are usually a linking element to another site."
    "6. Make sure that you response containing the recipe is no longer than 2000 characters, trim if needed, but only trim the steps in the preparation method and if you have to trim, shorten it with keywords, so that no relevant information is getting lost."
    "7. Ignore nutrician facts."
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
