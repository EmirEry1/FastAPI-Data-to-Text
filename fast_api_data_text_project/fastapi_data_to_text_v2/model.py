import os
import io
import re
import numpy as np
import DataBase
import bcrypt
from docx import Document
import PyPDF2
import Entity
import nlp
import magic

def verify_user(user_name, password):
    password_db = DataBase.get_password_by_user_name(user_name)
    if bcrypt.checkpw(password = password.encode('utf-8'), hashed_password = password_db):
        return True
    else:
        return False

async def extract_text_from_txt(file_content):
    return str(file_content)

async def extract_text_from_docx(file_content):
    doc = Document(io.BytesIO(file_content))
    doc_text = "\n".join([para.text for para in doc.paragraphs])
    return str(doc_text)

async def extract_text_from_pdf(file_content):
    pdf = PyPDF2.PdfReader(io.BytesIO(file_content))
    pdf_text = ""
    for page in pdf.pages:
        pdf_text += page.extract_text()
    return str(pdf_text)

def process_data(pure_txt: str , language):
    language_nlp : str
    if language == "not-provided":
        language_nlp = nlp.language_identification(pure_txt)
    else:
        language_nlp = language 
    output = nlp.ner(language_nlp, pure_txt)
    numbers = regex_finder(pure_txt)
    output.extend(numbers)
    for result in output:
        for entity in result:
            if (type(result[entity]) == np.float32):
                result[entity] = float(result[entity])
    entities = [] 
    for result in output:
        print(result)
        entity_new = Entity.Entity(entity_type = result["entity"], score = result["score"], index = result["index"], start = result["start"], end = result["end"], word = result["word"])
        entities.append(entity_new)
    return entities

def regex_finder(pure_txt):
    numbers = re.finditer("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]", pure_txt)
    dates = re.finditer("[0-3][0-9]\.[0-1][0-9]\.[0-9][0-9][0-9][0-9]", pure_txt)
    output = []
    for number in numbers:
        entity = {"score" : "100", "index": -1, "start":  number.start(), "end": number.end(), "word": number.group()}
        if number.group()[0] == "0":
            entity["entity"] = "B-TEL_NO"
        else:
            entity["entity"] = "B-TCKN"
        output.append(entity)
    for date in dates:
        entity = {"score" : "100", "index": -1, "start":  date.start(), "end": date.end(), "word": date.group()}
        entity["entity"] = "B-DATE"
        output.append(entity)
    return output
def find_file_type(file_content):
    mgc = magic.Magic(magic_file=os.environ["MAGIC"])
    file_type = mgc.from_buffer(file_content)
    acceptable_types = {
        "ASCII text": {"short_name": "txt", "string_miner": extract_text_from_txt},
        "PDF": {"short_name": "pdf", "string_miner": extract_text_from_pdf},
        "Microsoft Word": {"short_name": "docx", "string_miner": extract_text_from_docx},
        "UTF-8": {"short_name": "txt", "string_miner": extract_text_from_txt},
    }
        
    for key in acceptable_types.keys():
        if key in file_type:
            file_type_data = acceptable_types[key]
            break
    return file_type_data 
    
def get_data_from_file(file_content, file_type_data):
  text_miner = file_type_data.get("string_miner", None)
  if text_miner is None:
    raise Exception("File type you have provided is not supported.")
  return text_miner(file_content)

def ner_alternative(pure_txt: str, language):
    if language == "not-provided":
        language_nlp = nlp.language_identification(pure_txt)
    else:
        language_nlp = language
    output = nlp.ner_alternative(pure_txt, language_nlp)
    entities = []
    for entity in output:
        entities.append(Entity.EntityAlternative(entity_type = entity[1], word = entity[0]))
    return entities

def ner_post_processing(ner_output):
    full_word = ""
    entity_t = ""
    end_index = 0
    entity = Entity.EntityPostProcessed()
    entities = []
    for output in ner_output:
        position, entity_type = output.entity_type.split("-")  
        word = output.word
        if "##" == output.word[:2]:
            word = output.word[2:]
        if position == "B":
            entity.end = end_index
            entity.entity_type = entity_t
            entity.word = full_word
            entities.append(entity)
            entity = Entity.EntityPostProcessed()
            full_word = word
            entity_t = entity_type
            entity.start = output.start
        else:
            if end_index != output.start:
                full_word += " "
            full_word += word
        end_index = output.end
    entity.end = end_index
    entity.entity_type = entity_t
    entity.word = full_word
    entities.append(entity)
    entities = entities[1:]
    return entities