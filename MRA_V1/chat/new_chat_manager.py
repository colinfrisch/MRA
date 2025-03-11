from typing import Optional
import os, toml
import json
from openai import OpenAI
from backend.new_catalog_manager import TrainingManager
from backend.user_manager import UserManager
from backend.training_creator import TrainingCreator
import toml
import re

#from openai import OpenAI
from smolagents import HfApiModel, LiteLLMModel, TransformersModel, tool
from smolagents.agents import CodeAgent, ToolCallingAgent


#Short config
with open("../MRA_V1/.streamlit/secrets.toml", "r") as file:
    conf = toml.load(file)
os.environ["OPENAI_API_KEY"] = conf['general']['OPENAI_API_KEY']
model = LiteLLMModel(model_id="gpt-4o")

training_manager = TrainingManager()
user_manager = UserManager()
training_creator = TrainingCreator()




#Defining the tools
@tool
def get_training_list() -> list:
    """
    Obtenir la liste de tous les programmes d'apprentissage disponibles.

    Returns:
        Une liste de dictionnaires contenant les détails des programmes disponibles.
    """
    return json.dumps(training_manager.get_all_training_summaries())


@tool
def get_all_training_summary_for_field(field: str) -> list:
    """
    Obtenir la liste des programmes d'apprentissage disponibles pour un domain particulier donné.

    Args:
        field: Le domaine pour lequel on veut obtenir les programmes parmi.

    Returns:
        Une liste de dictionnaires contenant les programmes du domaine spécifié.
    """

    return json.dumps(training_manager.get_all_training_summary_for_field(field))


@tool
def create_training(subject: str, field: str, description : str) -> dict:
    """
    Créer un nouveau programme d'apprentissage à partir de la description fournie.

    Args:
        subject: Sujet du programme.
        field: Domaine du programme.
        description: Description du programme.

    Returns:
        Un dictionnaire contenant les détails du programme créé.
    """
    
    print("...Création d'un programme d'apprentissage avec : ", subject)
    training = training_creator.create_and_add_to_db(field,subject)
    
    return json.dumps(training.to_dict())


@tool
def subscribe_user_to_training(user_name: str, phone: str, program_id: str) -> dict:
    """
    Souscrire un utilisateur à un programme d'apprentissage.

    Args:
        user_name: Le prénom de l'utilisateur.
        phone: Le numéro de téléphone de l'utilisateur.
        program_id: L'identifiant du programme.

    Returns:
        Un dictionnaire confirmant l'inscription.
    """

    user = user_manager.get_user_by_name(user_name)
    if not user:
        print(f"...Creating user {user_name} with phone {phone}")
        user = user_manager.create_user(user_name, phone)
    print(f"...Subscribe user.id {user.id} to training  {program_id}")
    user_manager.set_current_training(user.id, program_id)
    return "Utilisateur inscrit avec succès!"



class ChatAgent:
    def __init__(self):
        # Load the select prompt
        with open("chat/select_prompt.txt", "r") as f:
            self.prompt = f.read()
            
        self.agent = ToolCallingAgent(
            tools=[
                get_training_list,
                get_all_training_summary_for_field,
                create_training,
                subscribe_user_to_training
            ], 
            model=model,
            system_prompt=self.prompt
        )
        self.messages = []
        self.is_finished = False
        
    def get_next_message(self):
        # Initial message to start the conversation
        initial_message = {
            "role": "assistant",
            "content": "Bonjour ! Je suis là pour vous aider à choisir une formation. Quel sujet vous intéresse ?",
            "display": True
        }
        self.messages.append(initial_message)
        return initial_message
        
    def get_messages(self):
        return self.messages
        
    def respond_to_user(self, user_input):
        user_message = {
            "role": "user",
            "content": user_input,
            "display": True
        }
        self.messages.append(user_message)
        
        # Get response from agent
        response = self.agent.run(user_input)
        
        # Check if we should finish the session
        if "user_name" in response and "training_id" in response:
            self.is_finished = True
            # Extract the JSON data
            assistant_message = {
                "role": "assistant",
                "content": f"Parfait ! Vous allez maintenant commencer votre formation.",
                "display": True,
                "json": {
                    "user_name": response["user_name"],
                    "training_id": response["training_id"]
                }
            }
        else:
            assistant_message = {
                "role": "assistant",
                "content": response,
                "display": True
            }
            
        self.messages.append(assistant_message)
        return assistant_message
        
    def is_session_finished(self):
        return self.is_finished

def main():
    #Creating and calling the agent
    agent = ChatAgent()
    agent.get_next_message()
    
    for request in [
        "J'aimerais me former en Sociologie",
        "Je suis Colin, mon numéro est le 01234567 et j'aimerais m'inscrire au cours Introduction à la Sociologie"
    ]:
        print(f"User: {request}")
        response = agent.respond_to_user(request)
        print(f"Assistant: {response['content']}")
        
        if agent.is_session_finished():
            print("Session finished with:", response.get("json", {}))
            break

if __name__ == "__main__":
    main()