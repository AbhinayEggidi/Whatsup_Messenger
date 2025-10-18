from app_methods import (
    suggest_replies,
    load_data,
    save_data,
    show_contacts,
    show_chat,
    menu,
    add_contact,
)

def main():
    msgs = load_data()

    while True:
        menu()
        choice = input("Enter your choice: ").strip()

        # Option 1 → Add Message
        if choice == "1":
            show_contacts(msgs)
            contact_name = input("\nEnter contact name: ").strip().lower()

            # Find or create contact
            contact_chat = next(
                (ctct for ctct in msgs if ctct["contact"].lower() == contact_name), None
            )
            if not contact_chat:
                print("Contact not found.")
                continue

            # Show chat history
            show_chat(contact_chat)

            # Input sender
            from_whom = input("\nEnter sender name: ").strip().lower()

            # If "me" → show Gemini suggestions
            if from_whom == "me":
                chat_text = "\n".join(
                    f"{m['from']}: {m['message']}" for m in contact_chat["messages"]
                )
                print("\nGenerating smart replies...")
                replies = suggest_replies(chat_text)

                if replies:
                    print("\nSuggested Replies:")
                    for i, reply in enumerate(replies, start=1):
                        print(f"{i}. {reply}")
                    print("4. Write my own reply")

                    choice = input("\nChoose a reply number (1-4): ").strip()

                    if choice.isdigit() and 1 <= int(choice) <= 3:
                        message = replies[int(choice) - 1]
                    elif choice == "4":
                        message = input("Enter your custom message: ").strip()
                    else:
                        print("Invalid choice, defaulting to custom message.")
                        message = input("Enter your message: ").strip()
                else:
                    print("Could not get suggestions. Please enter your reply manually.")
                    message = input("Enter your message: ").strip()

            else:
                message = input("Enter your message: ").strip()

            # Save message
            contact_chat["messages"].append({"from": from_whom, "message": message})
            save_data(msgs)
            print("\nMessage saved successfully!")
            show_chat(contact_chat)

        # Option 2 → View Messages
        elif choice == "2":
            show_contacts(msgs)
            contact_name = input("\nEnter contact name to view messages: ").strip().lower()
            found = False
            for ctct in msgs:
                if ctct["contact"].lower() == contact_name:
                    show_chat(ctct)
                    found = True
                    break
            if not found:
                print("Contact not found.")

        # Option 3 → Add Contact
        elif choice == "3":
            msgs = add_contact(msgs)

        # Exit
        elif choice == "9":
            print("\nExiting program...")
            break

        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
