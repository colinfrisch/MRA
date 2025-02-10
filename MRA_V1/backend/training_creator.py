import json, re, toml, threading, itertools
from openai import OpenAI
from backend.new_catalog_manager import *
from concurrent.futures import ThreadPoolExecutor



class TrainingCreator():
    def __init__(self):
        # load key from file ".streamlit/secrets.toml"
        with open(".streamlit/secrets.toml", "r") as file:
            conf = toml.load(file)
        self.client = OpenAI(api_key=conf['general']['OPENAI_API_KEY'])
        self.catalog_manager = TrainingManager()
    
    def create_training_json(self,field:str,subject:str) -> str:
        
        messages=[]
        
        with open("data/new_training_json_prompt.txt", "r") as file:
            content = file.read()
        content=content.replace("[[DOMAINE]]",field)
        content=content.replace("[[SUJET]]",subject)
        messages.append( {"role": "user", "content": content})
        
        response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
            )
        
        #on filtre ce qui'il y a entre les deux balises ```json et ``` dans response.choices[0].message.content
        #print(response.choices[0].message.content)
        json_content = re.search(r"```json(.*?)```", response.choices[0].message.content, re.DOTALL).group(1).strip()
        return json.loads(json_content)
        
        
    
    
    
    def complete_chapter(self,chapter,field,training_id,subject):
        
        messages=[]
        
        with open("data/complete_training_json_prompt.txt", "r") as file:
            content = file.read()
        content=content.replace("[[DOMAINE]]",field)
        content=content.replace("[[NOM_CHAPITRE]]",chapter["subject"])
        content=content.replace("[[SUJET]]",subject)
        #print the first two lines of content
        print(content[:300])
        messages.append( {"role": "user", "content": content})
        
        response_complete = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        #print (response_complete.choices[0].message.content)
        
        json_content_complete = re.search(r"```json(.*?)```", response_complete.choices[0].message.content, re.DOTALL).group(1).strip()
        json_content_complete = json_content_complete.replace("\n","")
        

        chapter["content"] = json.loads(json_content_complete)["content"]
        chapter["question"] = json.loads(json_content_complete)["question"]
        chapter["reponses"] = json.loads(json_content_complete)["responses"]
        chapter["training_id"] = training_id

        self.catalog_manager.add_chapter_to_training(chapter["subject"], chapter["content"], chapter["question"], chapter["reponses"], chapter["training_id"])
        print('chapter added to database : ',chapter["subject"])
        
    
    def execute_in_parallel(self,subject,field,training:Training,training_json):
        with ThreadPoolExecutor() as executor:
            print('subject : ',subject, 'field : ',field, 'training : ',training)
            list(executor.map(self.complete_chapter, training_json, itertools.repeat(field), itertools.repeat(training.id),itertools.repeat(subject)))
            
            print('done with all chapters')

            #return self.catalog_manager.modify_chapters(training.id, chapters)



        
    def create_and_add_to_db(self,field:str,subject:str):
        training = self.catalog_manager.create_training(subject, field, 'Un training sur ' + subject) #Training(db.cursor.lastrowid, subject, field, description, chapters)
        print("Training created and saved to database ")

        training_json = self.create_training_json(field,subject)

        thread = threading.Thread(target=self.execute_in_parallel, args=(subject,field,training,training_json))
        thread.start()
        thread.join()
        
        print('Training complete')

        



def main():
    training_creator = TrainingCreator()
    training_creator.create_and_add_to_db("Médecine","Tendinite rotulienne")
if __name__ == "__main__":
    main()
