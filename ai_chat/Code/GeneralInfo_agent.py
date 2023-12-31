# general_info_agent.py

from retriever import retrieve 
from chain import run_chain
from logger import setup_logger
import logging

# Set up the logger
logger = setup_logger('general_info_agent', level=logging.INFO)

class GeneralInfoAgent:

    def func(self, query, entities=None):
        try:
            # Retrieve the most relevant chunks
            hits = retrieve(query, k=2)
        
            # Generate a response using the run_chain function
            response = run_chain(hits, query)
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            response = "Sorry, something went wrong. Please try again later."
        
        return response
