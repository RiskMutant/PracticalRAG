
# Function to get embedding for a single text using the OpenAI API
def get_embedding(text, engine=):
    # Use the get_embeddings function to get the embedding for a single text
    return get_embeddings([text], engine)[0]
	
def get_embedding(text, engine=ENGINE):

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    response = client.embeddings.create(
        input=[text],
        model=engine
    )
    return response.data[0].embedding
