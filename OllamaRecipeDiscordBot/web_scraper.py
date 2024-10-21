# web_scrape.py

import logging
logging.basicConfig(level=logging.INFO)

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup

def scrape_website(website):
    logging.info("Launching firefox browser ...")
    firefox_driver_path = "./geckodriver.exe"
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=Service(firefox_driver_path), options=options)
    
    try:
        # Navigate to the specified website
        driver.get(website)
        logging.info("Page loaded...")
        
        # Get the HTML source of the page
        html = driver.page_source
        return html
    finally:
        # Close the browser
        driver.quit()

def extract_body_content(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract the body content
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    # Parse the body content using BeautifulSoup
    soup = BeautifulSoup(body_content, "html.parser")
    
    # Remove script and style tags
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get the text content of the remaining HTML
    cleaned_content = "\n".join(
        line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()
        )
    
    return cleaned_content

def split_dom_content(dom_content, max_length=8000):
    # Split the content into chunks of the specified max length
    return {
        dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)
    }
