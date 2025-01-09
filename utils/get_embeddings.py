# Function to get embeddings for a list of texts using the OpenAI API
def get_embeddings(texts, engine=):
    # Create embeddings for the input texts using the specified engine
    response = client.embeddings.create(input=texts,model=engine)

    # Extract and return the list of embeddings from the response
    return [d.embedding for d in list(response.data)]
