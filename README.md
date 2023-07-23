# ai-journal
Tool for a command line journal with GPT and bash compilation tools, Python for PDFs etc.

Need to configure Pinecone API and OpenAI API key into .env file. Then, edit names of index and your Pinecone region in files.
Can start by moving text files into /journals, and then 
```
cd embeddings
python3 create_embeddings.py
```

Then, 
```
cd ..
python3 journal_bot.py
```

And you should be able to speak to your journals in the command line. 
