import openai
import os
import pinecone

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from split_text import preprocess, text_to_chunks 

def create_embeddings(filename:str):
    # Set up OpenAI API
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Load data from file
    with open(filename, "r") as f:
        text = f.read()

    # Preprocess the text
    text = preprocess(text)

    # Create chunks from the text
    texts = [text]
    chunks = text_to_chunks(texts)

    # Create embeddings using OpenAI API
    res = openai.Embedding.create(
        input = chunks, engine='text-embedding-ada-002'
    )

    embeds = [record['embedding'] for record in res['data']]

    return chunks, embeds

def create_pinecone_index(index_name, embeds):
    # Set up Pinecone
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = 'us-east4-gcp'
    
    # Initialize Pinecone
    pinecone.init(
        api_key=pinecone_api_key,
        environment=pinecone_env
    )
    
    embed_dim = len(embeds[0]) if embeds else 0
    
    # Create index if it doesn't exist
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name, dimension=embed_dim)

    print("INDEX CREATED", index_name)
    # Return index instance
    return pinecone.Index(index_name)

def connect_pinecone(index_name):
    # Set up OpenAI
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Set up Pinecone
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_env = 'us-east4-gcp'
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)

    # Connect to the Pinecone index
    return pinecone.Index(index_name)


def upload_embeddings(data_arr, embeds, filename, index, namespace, batch_size=500):
    num_vectors = len(data_arr)
    num_batches = (num_vectors + batch_size - 1) // batch_size

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, num_vectors)

        # Create unique IDs for each data point
        ids = [str(j) for j in range(start_idx, end_idx)]

        # Prepare metadata for each data point
        meta = [{'text': text, 'filename': filename} for text in data_arr[start_idx:end_idx]]

        # Combine IDs, embeddings, and metadata for this batch
        to_upsert = zip(ids, embeds[start_idx:end_idx], meta)

        # Upsert the data into the Pinecone index
        index.upsert(vectors=list(to_upsert), namespace=namespace)

    print("VECTORS UPLOADED")


import glob

if __name__ == "__main__":
    # Connect to a pinecone vector index      
    index_name = "workout-names"
    
    # Create a new pinecone index
    # index = create_pinecone_index(index_name, embeds)
    
    # Use existing pinecone index 
    index = connect_pinecone(index_name)
    
    # Connect to namespace (subsection of the index)
    namespace = "journals"
    
    # Get a list of all files in the "journals" folder
    file_list = glob.glob("../journals/*.txt")

    for filename in file_list:
        chunks, embeds = create_embeddings(filename)
        upload_embeddings(chunks, embeds, filename, index, namespace, batch_size=500)
