from vector_search import connect_pinecone, pinecone_search 
from color_print import cyan_print

import openai, os
from dotenv import load_dotenv

openai.api_key = os.getenv("OPENAI_API_KEY")

def journal_chat(prompt, messages):
    
    conversation = []
    
    # If there are no messages, append the system prompt
    if len(messages) < 1:
        system_message = """You are a helpful AI journaling assistant. Please answer questions the user has about their journals and writings from the search results provided, if needed. Respond briefly, around 50 words."""
        conversation.append({"role": "system", "content": system_message})
    
    # Append the previous messages and prompt/question
    conversation += messages 
    conversation.append({"role": "user", "content": prompt})

    print("CONVERSATION:")
    for message in conversation:
        print(message)

    print('\n')

    # Get context from vector searching journal knowledge
    index = connect_pinecone("journals")
    namespace = "journal-data"
    query = prompt
    matches = pinecone_search(index, query, namespace) 
    
    context_string = "\n".join(matches)

    # Append context as an assistant message
    context = [{"role":"assistant", "content": "CONTEXT FOUND: " + context_string}]
    combined = conversation + context 

    # Feed the whole message array with only most recent context
    # To get the GPT-4 response (change to gpt-3.5-turbo if you don't have access)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        max_tokens = 512,
        messages=combined
    )

    completion = response["choices"][0]["message"]["content"]
    conversation.append({"role":"assistant", "content": completion})   

    # Print reply and question
    print(6*"\n")
    print('PROMPT:')
    cyan_print(prompt)
    print("\n")
    print('ASSISTANT:', completion)
    print(2*'\n')
    
    
    # Return conversation (without context) for loop
    return conversation 
    
if __name__ == "__main__":
    # Load env and set up empty variables
    load_dotenv()

    prompt = ""
    conversation = []
    
    # Run a loop, adding user prompt to workout chat function with new conversation array
    while True:
        prompt = input("Ask a question for Assistant (type 'quit' to exit): \n")
        if prompt.lower() == "quit":
            print('\n\nGLOW: Goodbye! \n')
            break
        else:
            conversation = journal_chat(prompt, conversation)
