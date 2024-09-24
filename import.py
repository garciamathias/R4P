from main import create_database, add_flashcard, add_mcq, add_course_extract

def add_items():
    create_database()

    while True:
        print("\nQue voulez-vous ajouter ?")
        print("1. Flashcard")
        print("2. QCM")
        print("3. Extrait de cours")
        print("4. Quitter")

        choice = input("Votre choix (1-4): ")

        if choice == '1':
            question = input("Question: ")
            answer = input("Réponse: ")
            add_flashcard(question, answer)
            print("Flashcard ajoutée.")

        elif choice == '2':
            question = input("Question: ")
            options = []
            for i in range(4):
                option = input(f"Option {i+1}: ")
                options.append(option)
            correct_answer = input("Réponse correcte: ")
            add_mcq(question, options, correct_answer)
            print("QCM ajouté.")

        elif choice == '3':
            text = input("Texte de l'extrait de cours: ")
            add_course_extract(text)
            print("Extrait de cours ajouté.")

        elif choice == '4':
            print("Au revoir!")
            break

        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    add_items()