import sqlite3
import random
from datetime import datetime

# Base de données
def create_database():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS revision_elements
                 (id INTEGER PRIMARY KEY, 
                  score INTEGER, 
                  type TEXT, 
                  last_revision DATE)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS flashcards
                 (id INTEGER PRIMARY KEY, 
                  question TEXT, 
                  answer TEXT, 
                  FOREIGN KEY(id) REFERENCES revision_elements(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS mcq
                 (id INTEGER PRIMARY KEY, 
                  question TEXT, 
                  options TEXT, 
                  correct_answer TEXT, 
                  FOREIGN KEY(id) REFERENCES revision_elements(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS course_extracts
                 (id INTEGER PRIMARY KEY, 
                  text TEXT, 
                  FOREIGN KEY(id) REFERENCES revision_elements(id))''')
    
    conn.commit()
    conn.close()

# Fonctions pour ajouter des éléments
def add_element(element_type, content):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute("INSERT INTO revision_elements (score, type, last_revision) VALUES (?, ?, ?)", 
              (0, element_type, datetime.now().date()))
    element_id = c.lastrowid
    
    if element_type == 'flashcard':
        c.execute("INSERT INTO flashcards (id, question, answer) VALUES (?, ?, ?)", 
                  (element_id, content['question'], content['answer']))
    elif element_type == 'mcq':
        c.execute("INSERT INTO mcq (id, question, options, correct_answer) VALUES (?, ?, ?, ?)", 
                  (element_id, content['question'], ','.join(content['options']), content['correct_answer']))
    elif element_type == 'course_extract':
        c.execute("INSERT INTO course_extracts (id, text) VALUES (?, ?)", 
                  (element_id, content['text']))
    
    conn.commit()
    conn.close()

# Fonction pour obtenir l'élément avec le score le plus bas
def get_lowest_score_item():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute("""SELECT re.id, re.score, re.type, re.last_revision,
                        f.question, f.answer,
                        m.question, m.options, m.correct_answer,
                        ce.text
                 FROM revision_elements re
                 LEFT JOIN flashcards f ON re.id = f.id
                 LEFT JOIN mcq m ON re.id = m.id
                 LEFT JOIN course_extracts ce ON re.id = ce.id
                 WHERE re.score = (SELECT MIN(score) FROM revision_elements)
                 ORDER BY RANDOM()
                 LIMIT 1""")
    
    item = c.fetchone()
    conn.close()
    
    return item

# Fonction pour mettre à jour le score
def update_score(item_id, correct):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute("SELECT score FROM revision_elements WHERE id = ?", (item_id,))
    current_score = c.fetchone()[0]
    
    if correct:
        new_score = min(current_score + 10, 100)
    else:
        new_score = max(current_score - 5, 0)
    
    c.execute("UPDATE revision_elements SET score = ?, last_revision = ? WHERE id = ?", 
              (new_score, datetime.now().date(), item_id))
    conn.commit()
    conn.close()

# Fonction pour calculer la moyenne des scores
def get_average_score():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute("SELECT AVG(score) FROM revision_elements")
    avg_score = c.fetchone()[0]
    
    conn.close()
    
    return avg_score if avg_score is not None else 0

# Fonction principale de l'application
def main():
    create_database()
    
    while get_average_score() < 95:
        item = get_lowest_score_item()
        if item is None:
            print("Pas d'éléments à réviser.")
            break
        
        item_id, score, item_type, last_revision, *item_data = item
        
        if item_type == 'flashcard':
            question, answer = item_data[:2]
            print(f"Flashcard: {question}")
            user_answer = input("Votre réponse: ")
            correct = user_answer.lower() == answer.lower()
            print(f"Correct: {correct}. La réponse était: {answer}")
        
        elif item_type == 'mcq':
            question, options, correct_answer = item_data[2:5]
            print(f"QCM: {question}")
            options = options.split(',')
            for i, option in enumerate(options):
                print(f"{i+1}. {option}")
            user_answer = input("Votre réponse (numéro): ")
            correct = options[int(user_answer)-1] == correct_answer
            print(f"Correct: {correct}. La bonne réponse était: {correct_answer}")
        
        else:  # course_extract
            text = item_data[5]
            print(f"Extrait de cours: {text}")
            user_input = input("Tapez 'lu' quand vous avez fini de lire: ")
            correct = user_input.lower() == 'lu'
        
        update_score(item_id, correct)
        print(f"Score moyen actuel: {get_average_score():.2f}")
        print(f"Dernière révision: {last_revision}")
        print()

    print("Félicitations ! Vous avez terminé vos révisions.")

if __name__ == "__main__":
    main()