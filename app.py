from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import hashlib
import os
from datetime import datetime
from tqdm import tqdm

from bs4 import BeautifulSoup
import requests
import re
from utils import *
from dotenv import load_dotenv # type: ignore
load_dotenv()

# Retrieve the Pinecone API key from user data
pinecone_key = os.environ.get('PINECONE_API_KEY')

# Initialize the OpenAI client with the API key from user data
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Define constants for the Pinecone index, namespace, and engine
ENGINE = 'text-embedding-3-small'  # The embedding model to use (vector size 1,536)

# Initialize the Pinecone client with the retrieved API key
pc = Pinecone(api_key=pinecone_key)

INDEX_NAME = 'incometax'  # The name of the Pinecone index
NAMESPACE = 'faq'  # The namespace to use within the index

if INDEX_NAME not in pc.list_indexes().names():  # need to create the index
    print(f'Creating index {INDEX_NAME}')
    pc.create_index(
        name=INDEX_NAME,  # The name of the index
        dimension=1536,  # The dimensionality of the vectors for our OpenAI embedder
        metric='cosine',  # The similarity metric to use when searching the index
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

index = pc.Index(name=INDEX_NAME)

base_url = 'https://faq.ssa.gov'
pattern = r'^/en-US'

matching_links = find_links_with_pattern(base_url, pattern)
print(matching_links)

urls = []

for matching_link in tqdm(matching_links):
    r = requests.get(base_url + matching_link)
    soup = BeautifulSoup(r.content, 'html.parser')
    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            if link['href'].startswith('/') and 'article' in link['href']:
                urls.append(base_url + link['href'])
    
urls = list(set([u.lower().strip() for u in urls]))
len(urls)
print(urls[:])

government_docs = []
for url in tqdm(urls):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    body = clean_string(soup.find('body').get_text())
    government_docs.append(dict(text=body, url=url))

BATCH_SIZE = 16
upload_texts_to_pinecone(
    texts=[g['text'] for g in government_docs],
    batch_size=BATCH_SIZE, show_progress_bar=True, 
    urls=[g['url'] for g in government_docs]
)

index.describe_index_stats()

query = 'I am not born citizen'

results = query_from_pinecone(query, top_k=10)
for result in results:
    print(result['metadata']['url'], result['score'], result['metadata']['text'][-50:])