from typing import Optional
import os, toml
import json
from openai import OpenAI
from backend.catalog_manager import TrainingManager
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



def main():
    #Creating and calling the agent
    agent = ToolCallingAgent(tools=[get_training_list,get_all_training_summary_for_field,create_training,subscribe_user_to_training], model=model)

    request = ["J'aimerais me former encore davantage en Sociologie et j'ai déjà suivi les cours ici présents. Peux tu créer un cours qui n'existe pas déjà ?",
        
        "Je suis Colin, mon numéro est le 01234567 et j'aimerais m'inscrire à un cours de Médecine déjà existant et m'inscrire immédiatement. Pouvez-vous le faire ?",  
        # 1-> get_all_training_summary_for_field("Science") + subscribe_user_to_training(nom, téléphone, program_id)

        "J'aimerais en savoir plus sur les formations en économie et en Médecine. Pouvez-vous me donner les programmes disponibles ?",  
        # 2-> get_all_training_summary_for_field("Économie") + get_all_training_summary_for_field("Sociologie")

        "Je veux créer un programme sur la cybersécurité dans le domaine de l'informatique et m'y inscrire immédiatement. Pouvez-vous le faire ?",  
        # 3-> create_training("Cybersécurité", "Informatique") + subscribe_user_to_training(nom, téléphone, program_id)

        "Quels sont tous les programmes disponibles ? J'aimerais m'inscrire à un en histoire.",  
        # 4-> get_training_list() + subscribe_user_to_training(nom, téléphone, program_id)

        "Pouvez-vous me lister les formations en histoire et géographie et créer une nouvelle formation sur l'archéologie ?",  
        # 5-> get_all_training_summary_for_field("Histoire") + get_all_training_summary_for_field("Géographie") + create_training("Archéologie", "Histoire")
    ]




    print("ToolCallingAgent:", agent.run(request[1]))

if __name__ == "__main__":
    main()