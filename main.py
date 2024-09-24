import sqlite3
import random

# Base de données
def create_database():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS flashcards
                 (id INTEGER PRIMARY KEY, question TEXT, answer TEXT, score REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS mcq
                 (id INTEGER PRIMARY KEY, question TEXT, options TEXT, correct_answer TEXT, score REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS course_extracts
                 (id INTEGER PRIMARY KEY, text TEXT, score REAL)''')
    
    conn.commit()
    conn.close()

# Fonctions pour ajouter des éléments
def add_flashcard(question, answer):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO flashcards (question, answer, score) VALUES (?, ?, 0)", (question, answer))
    conn.commit()
    conn.close()

def add_mcq(question, options, correct_answer):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO mcq (question, options, correct_answer, score) VALUES (?, ?, ?, 0)", 
              (question, ','.join(options), correct_answer))
    conn.commit()
    conn.close()

def add_course_extract(text):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO course_extracts (text, score) VALUES (?, 0)", (text,))
    conn.commit()
    conn.close()

# Fonction pour obtenir l'élément avec le score le plus bas
def get_lowest_score_item():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    tables = ['flashcards', 'mcq', 'course_extracts']
    lowest_score_items = []
    
    for table in tables:
        c.execute(f"SELECT * FROM {table} WHERE score = (SELECT MIN(score) FROM {table})")
        items = c.fetchall()
        if items:
            lowest_score_items.extend([(table, item) for item in items])
    
    conn.close()
    
    if lowest_score_items:
        return random.choice(lowest_score_items)
    return None

# Fonction pour mettre à jour le score
def update_score(table, item_id, correct):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute(f"SELECT score FROM {table} WHERE id = ?", (item_id,))
    current_score = c.fetchone()[0]
    
    if correct:
        new_score = min(current_score + 0.1, 1)
    else:
        new_score = max(current_score - 0.05, 0)
    
    c.execute(f"UPDATE {table} SET score = ? WHERE id = ?", (new_score, item_id))
    conn.commit()
    conn.close()

# Fonction pour calculer la moyenne des scores
def get_average_score():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    tables = ['flashcards', 'mcq', 'course_extracts']
    total_score = 0
    total_items = 0
    
    for table in tables:
        c.execute(f"SELECT AVG(score) FROM {table}")
        avg_score = c.fetchone()[0]
        if avg_score is not None:
            c.execute(f"SELECT COUNT(*) FROM {table}")
            count = c.fetchone()[0]
            total_score += avg_score * count
            total_items += count
    
    conn.close()
    
    if total_items > 0:
        return total_score / total_items
    return 0

# Fonction principale de l'application
def main():
    create_database()
    
    while get_average_score() < 0.95:
        item = get_lowest_score_item()
        if item is None:
            print("Pas d'éléments à réviser.")
            break
        
        table, (item_id, *item_data) = item
        
        if table == 'flashcards':
            question, answer, score = item_data
            print(f"Flashcard: {question}")
            user_answer = input("Votre réponse: ")
            correct = user_answer.lower() == answer.lower()
            print(f"Correct: {correct}. La réponse était: {answer}")
        
        elif table == 'mcq':
            question, options, correct_answer, score = item_data
            print(f"QCM: {question}")
            options = options.split(',')
            for i, option in enumerate(options):
                print(f"{i+1}. {option}")
            user_answer = input("Votre réponse (numéro): ")
            correct = options[int(user_answer)-1] == correct_answer
            print(f"Correct: {correct}. La bonne réponse était: {correct_answer}")
        
        else:  # course_extracts
            text, score = item_data
            print(f"Extrait de cours: {text}")
            user_input = input("Tapez 'lu' quand vous avez fini de lire: ")
            correct = user_input.lower() == 'lu'
        
        update_score(table, item_id, correct)
        print(f"Score moyen actuel: {get_average_score():.2f}")
        print()

    print("Félicitations ! Vous avez terminé vos révisions.")

if __name__ == "__main__":
    main()