from enum import Enum
from pydantic import BaseModel

class EntityType(str, Enum):
    begin_person = 'B-PER'
    inside_person = 'I-PER'
    begin_organization = 'B-ORG'
    inside_organization = 'I-ORG'
    begin_location = 'B-LOC'
    inside_location = 'I-LOC'
    begin_date = 'B-DATE'
    inside_date = 'I-DATE'
    begin_time = 'B-TIME'
    inside_time = 'I-TIME'
    begin_money = 'B-MONEY'
    inside_money = 'I-MONEY'
    begin_percent = 'B-PERCENT'
    inside_percent = 'I-PERCENT'
    begin_number = 'B-NUM'
    inside_number = 'I-NUM'
    begin_miscellaneous = 'B-MISC'
    inside_miscellaneous = 'I-MISC' 
    tckn = "B-TCKN"
    telephone_no ="B-TEL_NO"
    outside = 'O'

class Entity(BaseModel):
    entity_type: EntityType
    score: float
    index: int
    word: str
    start: int
    end: int

class EntityPostProcessed(BaseModel):
    entity_type: EntityType = None
    word: str = None
    start: int = None
    end: int = None

class EntityTypeAlternative(str, Enum):
    person = "PERSON"
    nationality_or_religious_political_group = "NORP"
    structure = "FAC"
    organization = "ORG"
    gpe_location = "GPE"
    non_gpe_location = "LOC"
    product = "PRODUCT"
    event = "EVENT"
    work_of_art = "WORK_OF_ART"
    law = "LAW"
    language = "LANGUAGE"
    date = "DATE"
    time = "TIME"
    percent = "PERCENT"
    money = "MONEY"
    quantity =  "QUANTITY"
    ordinal = "ORDINAL"
    other_numbers = "CARDINAL"

class EntityAlternative(BaseModel):
    word: str
    entity_type: EntityTypeAlternative 