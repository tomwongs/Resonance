import os
import json
from ..generation.tools import generate_openrouter, generate_ollama
from .....tools import sql



class Memories:

    def __init__(self, data: dict):
        self.db = data.get("layers").get("memories").get("db")

    def get_memories_w_tags(self, tags: list):
        if not os.path.isfile(self.db) or not tags:
            print(f"FILE \"{self.db}\" DOESN'T EXIST!")
            return []

    
        conditions = " OR ".join(
        ["REPLACE(CONCAT(',', tags, ','), ', ', ',') LIKE CONCAT('%,', ?, ',%')"] * len(tags)
    )
    
        params = tuple(tags)

        query = f"""
        SELECT * FROM Memories
        WHERE {conditions}
        """
    
        return sql.EXEC(self.db, query, params)

    
    def get_memories_w_date(self, date: str, date_type=0) -> list:
        try:
            match date_type:
                case  2:
                    query = """
                    SELECT * FROM Memories
                    WHERE last_accessed = ?
                    """
                case 1:
                    query = """
                    SELECT * FROM Memories
                    WHERE updated_at = ?
                    """
                case _:
                    query = """
                    SELECT * FROM Memories
                    WHERE created_at = ?
                    """
         
            params = date
            result = sql.EXEC(database=self.db, query=query, params=params)

            return result

        except Exception:
            print("Error with self.db.")
            return []
    

#def get_memories(self) -> list:
#    return []

    def create_memories(self, context_target: str, data, ai_response="") -> bool:
        preprompt = """
        Your task is to produce a JSON that summarize what happened in the following conversation, just the pure raw JSON, without any backticks for presentation purposes, only the raw JSON, nothing more, nothing less. 
        The summary must be detailed.
        In your JSON you'll produce memory cards that are made of memories to remember.
        The importance parameter is an integer between 1 and 10.
        It is VERY important that if there's a relation between memories you concatenate the tags of the memories into BOTH memories.
        In the tags NEVER put '_' for spaces and NEVER put multiple words split them e.g. "life style", put "life, style"
    
        Here's what your JSON must look like:
        {
            "day_summary": "detailed_summary_of_context",
            "memory_cards": [
                {
                    "title": "Title for Memory"
                    "tags": "relevant,tags,to,find,memory", 
                    "entities": "entities,objects,clothes,or,accessories,in,memory",
                    "content": "Summary of memory.",
                    "importance": INT,
                }
            ]
            "created_at": "date e.g. 2026-02-12",
        }
    
        Here's the context you must summarize:
        """
        context = [{"role":"user", "content": preprompt+context_target}]
        try: 
            ai_response_dict = {}
            if ai_response == "":
                if data.get("layers").get("memories").get("provider") == "openrouter":
                    ai_response_dict = json.loads(generate_openrouter(context, data.get("layers").get("memories").get("model")))
                elif data.get("layers").get("memories").get("provider") == "ollama":
                    ai_response_dict = json.loads(generate_ollama(context, data.get("layers").get("memories").get("model")))
            else:
                ai_response_dict = json.loads(ai_response)
    
    
            # Send to SQL
            with open("output.txt", 'w') as file:
                file.write(json.dumps(ai_response))
    

            ## Day Summary
            query = """
            INSERT INTO Day_Summary (date, summary)
            VALUES (?, ?)
            """
            params = (ai_response_dict["created_at"], ai_response_dict["day_summary"])
    
            sql.EXEC(database=self.db, query=query, params=params, fetch=False)
    
    
            ## Memory Cards
            query = """
            INSERT INTO Memories (title, tags, entities, content, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """
    
            for card in ai_response_dict["memory_cards"]:
                params = (card["title"], card["tags"], card["entities"], card["content"], card["importance"], ai_response_dict["created_at"])
                sql.EXEC(database=self.db, query=query, params=params, fetch=False)
    
    
            return True 
    
        except json.JSONDecodeError as e:
            print("AI didn't output a JSON format!")
            print(e)
            return False
