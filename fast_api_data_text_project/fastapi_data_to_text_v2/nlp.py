from transformers import AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM, pipeline
import spacy

language_to_model_mapping = {"tr": "akdeniz27/bert-base-turkish-cased-ner",
                             "en": "dslim/bert-base-NER"}
language_abbreviations = {"tr": "Turkish",
                          "en": "English"}
def ner(language: str, input: str):
    if language in language_to_model_mapping.keys():
        named_entity_recognizer = pipeline("token-classification", model = language_to_model_mapping[language])
        return named_entity_recognizer(input)
    else:
        languages = ", ".join(language_abbreviations.values())
        raise Exception("Please provide a valid language. Supported languages are: " + str(languages))

def ner_alternative(input: str, language: str):
    if language != "en":
        print(language)
        input = translation(input)
    nlp = spacy.load("en_core_web_lg")
    doc = nlp(input)
    entities = []
    for ent in doc.ents:
        entities.append([ent.text, ent.label_])
    return entities

#print(ner_alternative('Call centre users \'lose patience\'\r\n\r\nCustomers trying to get through to call centres are getting impatient and quicker to hang up, a survey suggests.\r\n\r\nOnce past the welcome message, callers on average hang up after just 65 seconds of listening to canned music. The drop in patience comes as the number of calls to call centres is growing at a rate of 20% every year. "Customers are getting used to the idea of an \'always available\' society," says Cara Diemont of IT firm Dimension Data, which commissioned the survey. However, call centres also saw a sharp increase of customers simply abandoning calls, she says, from just over 5% in 2003 to a record 13.3% during last year. When automated phone message systems are taken out of the equation, where customers have to pick their way through multiple options and messages, the number of abandoned calls is even higher - a sixth of all callers give up rather than wait. One possible reason for the lack in patience, Ms Diemont says, is the fact that more customers are calling \'on the move\' using their mobile phones.', 'en'))

def language_identification(input: str):
    language_identification = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")
    return language_identification(input)[0]["label"]

def translation(file_content):
    tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-tr-en")
    model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-tr-en")
    translator = pipeline(task="translation", model = model, tokenizer = tokenizer)
    translated_text = translator(file_content.split("belgenin")[0], src_lang = "tr", tgt_lang = "en")[0]["translation_text"]
    print(translated_text)
    return translated_text

def ner_post_processing(ner_output):
    full_word = ""
    entity_t = ""
    end_index = 0
    entity = {}
    entities = []
    for output in ner_output:
        position, entity_type = output.entity_type.split("-")  
        word = output.word
        if "##" == output.word[:2]:
            word = output.word[2:]
        if position == "B":
            entity["end"] = end_index
            entity["entity_type"] = entity_t
            entity["word"] = full_word
            entities.append(entity)
            entity = {}
            full_word = word
            entity_t = entity_type
            entity["start"] = output["start"]
        else:
            if end_index != output["start"]:
                full_word += " "
            full_word += word
        end_index = output["end"]
    entities.append({"entity_type": entity_t, "word": full_word })
    entities = entities[1:]
    return entities