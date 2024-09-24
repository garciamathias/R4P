import os
from openai import OpenAI
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field
from typing import List
from main import create_database, add_flashcard, add_mcq, add_course_extract

# Initialisation du client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

class Flashcard(BaseModel):
    question: str
    answer: str

class MCQ(BaseModel):
    question: str
    options: List[str] = Field(min_items=4, max_items=4)
    correct_answer: str

class CourseExtract(BaseModel):
    text: str

class RevisionMaterial(BaseModel):
    flashcards: List[Flashcard] = Field(min_items=5, max_items=5)
    mcq: List[MCQ] = Field(min_items=3, max_items=3)
    course_extracts: List[CourseExtract] = Field(min_items=2, max_items=2)

def generate_revision_cards(text):
    prompt = f"""
    Analysez le texte suivant et générez des éléments de révision structurés en JSON.
    Créez exactement :
    - 5 flashcards
    - 3 QCM avec exactement 4 options chacun
    - 2 extraits de cours

    Retournez le résultat au format JSON suivant :
    {{
        "flashcards": [
            {{"question": "...", "answer": "..."}}
        ],
        "mcq": [
            {{"question": "...", "options": ["...", "...", "...", "..."], "correct_answer": "..."}}
        ],
        "course_extracts": [
            {{"text": "..."}}
        ]
    }}

    Texte à analyser :
    {text[:4000]}
    """

    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Vous êtes un expert en éducation, spécialisé dans la création de matériel de révision efficace. Répondez uniquement avec un objet JSON valide."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
    )

    return RevisionMaterial.model_validate_json(completion.choices[0].message.content)

def parse_and_add_to_database(revision_material):
    for flashcard in revision_material.flashcards:
        add_flashcard(flashcard.question, flashcard.answer)
    
    for mcq in revision_material.mcq:
        add_mcq(mcq.question, mcq.options, mcq.correct_answer)
    
    for extract in revision_material.course_extracts:
        add_course_extract(extract.text)
    
    print("Éléments de révision ajoutés avec succès à la base de données.")

def main():
    create_database()
    pdf_path = "fe.pdf"  # Remplacez par le chemin de votre fichier PDF
    text = extract_text_from_pdf(pdf_path)
    revision_material = generate_revision_cards(text)
    parse_and_add_to_database(revision_material)

if __name__ == "__main__":
    main()