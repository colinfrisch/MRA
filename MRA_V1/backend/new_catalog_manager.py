# training_manager.py
from backend.db import DBConnection
import json
from enum import Enum
from typing import *


class Answer:
    def __init__(self, text: str, valid: bool):
        self.text = text
        self.valid = valid

    def to_dict(self):
        return {"text": self.text, "valid": self.valid}

class Chapter:
    def __init__(self, chapter_id: int, subject: str, content: str, question: str, answers: list[Answer],training_id:int):
        self.id = chapter_id
        self.subject = subject
        self.content = content
        self.question = question
        self.answers = answers
        self.training_id = training_id

    def get_answers(self) -> list[Answer]:
        return self.answers

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "content": self.content,
            "question": self.question,
            "answers": [answer.to_dict() for answer in self.answers],
            "training_id": self.training_id
        }

class Training:
    def __init__(self, training_id: int, subject: str, field: str, description: str, chapters: Optional[List['Chapter']] = None):
        self.id = training_id
        self.subject = subject
        self.field = field
        self.description = description
        self.chapters = chapters if chapters is not None else []

    def get_subject(self) -> str:
        return self.subject

    def get_field(self) -> str:
        return self.field

    def get_description(self) -> str:
        return self.description

    def get_chapters(self) -> list[Chapter]:
        return self.chapters

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "field": self.field,
            "description": self.description,
            "chapters": [chapter.to_dict() for chapter in self.chapters]
        }




class TrainingManager:
    def create_training(self, subject: str, field: str, description: str) -> Training:
        '''
        chapters est maintenant une table de la forme (id, subject, content, question(json), answer, training_id(fk) )
        chapters est donc ici donné en liste 
        '''

        with DBConnection() as db:
            
            db.execute("INSERT INTO trainings (subject, field, description) VALUES (?, ?, ?)", 
                       (subject, field, description))
            db.commit()

        return Training(db.cursor.lastrowid, subject, field, description, [])
        

    def add_chapter_to_training(self, subject: str, content: str, question: str, answers: list[dict], training_id: int) -> Chapter:
        answers_json = json.dumps(answers)
        
        with DBConnection() as db: # Insert the chapter into the database
            db.execute(
                "INSERT INTO chapters (subject, content, question, answers, training_id) VALUES (?, ?, ?, ?, ?)", 
                (subject, content, question, answers_json, training_id)
            )
            db.commit()

        return Chapter(
            db.cursor.lastrowid, 
            subject, 
            content, 
            question, 
            [Answer(ans["text"], ans["valid"]) for ans in answers], 
            training_id
        )


    def get_all_chapters_from_training(self, training_id):
        
        with DBConnection() as db:
            db.execute("SELECT * FROM chapters WHERE training_id = ?", (training_id,))
            chapters = db.fetchall()
        
        chapter_list = []
        
        for chapter in chapters:
            answers = json.loads(chapter["answers"])
            chapter_list.append(Chapter(
                chapter["id"], 
                chapter["subject"], 
                chapter["content"], 
                chapter["question"],
                [Answer(ans["text"], ans["valid"]) for ans in answers],
                chapter['training_id']
            ))

        return chapter_list
        

    def get_all_trainings(self) -> list[Training]:
        with DBConnection() as db:
            db.execute("SELECT * FROM trainings")
            rows = db.fetchall()
            trainings = []
            for row in rows:
                training_id = row['id']
                chapter_list = self.get_all_chapters_from_training(training_id)

                training = Training(row["id"], row["subject"], row["field"], row["description"],chapter_list)
                trainings.append(training)
            return trainings


    def get_all_training_summaries(self) -> list[dict]:
        with DBConnection() as db:
            db.execute("SELECT id, subject, field, description FROM trainings")
            rows = db.fetchall()
            training_summaries = []
            for row in rows:
                training_summary = {
                    "id": row["id"],
                    "subject": row["subject"],
                    "field": row["field"],
                    "description": row["description"]
                }
                training_summaries.append(training_summary)
            return training_summaries


    def get_all_training_summary_for_field(self, field: str) -> list[dict]:
        all_summaries = self.get_all_training_summaries()
        return [summary for summary in all_summaries if summary["field"] == field]


    def get_training_by_id(self, training_id: int) -> Training:
        with DBConnection() as db:
            db.execute("SELECT * FROM trainings WHERE id = ?", (training_id,))
            training_row = db.fetchone()
            
            if training_row:
                chapters = self.get_all_chapters_from_training(training_id)
                return Training(
                            training_row["id"], 
                            training_row["subject"], 
                            training_row["field"], 
                            training_row["description"], 
                            chapters
                        )
            return None

    def modify_chapter_section(self, chapter_id: int,section:str, new_content:str):
        with DBConnection() as db:
            db.execute("UPDATE chapters SET ? = ? WHERE id = ?", (section,new_content,chapter_id))
            db.commit()




def main():
    training_manager = TrainingManager()
    new_training = training_manager.create_training("Training 1", "history", "Description 1")
    training_id = new_training.to_dict()['id']
    print('training added')

    new_chap1 = training_manager.add_chapter_to_training("Chapter 1", "Content 1", "Question 1", [{"text": 'qtxt1', "valid": True},{"text": 'qtxt2', "valid": False}],training_id)
    
    print('chapter added : ',new_chap1.to_dict()['subject'])
    

if __name__ == "__main__":
    main()
