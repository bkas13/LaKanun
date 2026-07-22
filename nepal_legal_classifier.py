# Nepal Legal AI Classifier: Legal vs Illegal based on Constitution and Documents
# Tech Stack: Python + Selenium + NLP + Embedding Search

# 1. Dependencies
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from sentence_transformers import SentenceTransformer, util
import time, os, json

# 2. Setup headless browser to scrape Nepali Constitution and Legal Documents
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# 3. Load Sources of Truth (local or online PDFs/texts)
# For demo purposes, we'll scrape Constitution of Nepal from an open source
constitution_url = "https://www.lawcommission.gov.np/en/archives/category/documents/prevailing-law/constitution"
driver.get(constitution_url)
time.sleep(3)

# 4. Collect Texts (Scrape or Load Offline)
links = driver.find_elements(By.TAG_NAME, 'a')
relevant_links = [link.get_attribute('href') for link in links if link.get_attribute('href') and 'constitution-of-nepal' in link.get_attribute('href')]

# You should download and store content locally in production
# Simulating offline documents:
documents = [
    "No one shall be discriminated on the basis of caste, religion, gender.",
    "Every person shall have the right to freedom of speech and expression.",
    "Traffic in human beings, and slavery is prohibited in any form.",
    "No one shall be subjected to torture or to cruel, inhuman or degrading treatment.",
    "The right to privacy of any person is inviolable."
]

# 5. Embed Documents
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Lightweight, replaceable with Nepali-tuned model later
corpus_embeddings = model.encode(documents, convert_to_tensor=True)

# 6. Legal Classification Function
def classify_legality(prompt: str):
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(prompt_embedding, corpus_embeddings)
    top_score = similarities.max().item()
    threshold = 0.45  # You can tune this based on validation
    
    if top_score >= threshold:
        return "LEGAL", top_score
    else:
        return "ILLEGAL", top_score

# 7. Prompt Example
if __name__ == "__main__":
    scenarios = [
        "Can a woman inherit property equally as her brothers in Nepal?",
        "Is it legal to discriminate against someone because of their caste in a public place?",
        "Can the police arrest someone without showing a warrant?",
        "Is it allowed to criticize the government on social media in Nepal?",
        "Can a person be forced to work without pay in Nepal?",
        "Is it legal to conduct a peaceful protest in Kathmandu?",
        "Can the government listen to my private phone calls without my permission?",
        "Is it legal to marry before the age of 18 in Nepal?",
        "Can a journalist be jailed for publishing news about corruption?",
        "Is it legal to deny someone entry to a temple because of their religion?",
        "Can a person be appointed as full time employee in two public companies at one time ?"
    ]
    for prompt in scenarios:
        result, score = classify_legality(prompt)
        print(f"Prompt: {prompt}\nClassification: {result} (Confidence: {round(score, 2)})\n")

    driver.quit()
