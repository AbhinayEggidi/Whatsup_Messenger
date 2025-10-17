import json
import os
import requests
from dotenv import load_dotenv
 
#   Setup Gemini API

load_dotenv()
api_key = os.getenv("gemini_api_key")

if not api_key:
    print("Gemini API key not found. Please set 'gemini_api_key' in your .env file.")
    exit()

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

 
#   Generate Smart Replies (via REST API)
 
def suggest_replies(full_chat):
    prompt = f"""
You are chatting casually with a friend.
Here is the chat history:
{full_chat}

Suggest exactly three short, friendly, and natural replies I can send next.
Don't include any introductions or extra text — only the three replies,
each on a separate line.
"""

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        suggestions = text.strip().split("\n")

        clean_suggestions = []
        for s in suggestions:
            s = s.strip("1234567890. •- ")
            if len(s) > 3 and not s.lower().startswith("here are"):
                clean_suggestions.append(s)

        return clean_suggestions[:3]

    except requests.exceptions.RequestException as e:
        print("Error communicating with Gemini API:", e)
        return []


 
# Load / Save Data
 
def load_data():
    try:
        with open("messages.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open("messages.json", "w") as f:
        json.dump(data, f, indent=4)

 
def show_contacts(msgs):
    print("\nContacts List:")
    for i, ctct in enumerate(msgs, start=1):
        print(f"{i}. {ctct['contact']}")
    

def show_chat(contact_chat):
    print(f"\n-- Chat with {contact_chat['contact']} --")
    for msg in contact_chat["messages"]:
        print(f"{msg['from']}: {msg['message']}")

 
def menu():
    print("\n----------------------")
    print(" Message Manager")
    print("1. Add Message / Chat")
    print("2. View Messages")
    print("9. Exit")
    print("----------------------")

# -----------------------------Main Program-----------------------------
msgs = load_data()

while True:
    menu()
    choice = input("Enter your choice: ").strip()

    # Option 1 → Add Message
    if choice == "1":
        show_contacts(msgs)

        contact_name = input("\nEnter contact name: ").strip().lower()

        # Find or create contact
        contact_chat = None
        for ctct in msgs:
            if ctct["contact"].lower() == contact_name:
                contact_chat = ctct
                break

        if not contact_chat:
            print("You don't have the contact.")
            confirm = input("Creating new contact (yes/no): ").strip().lower()
            if confirm == "yes":
                contact_chat = {"contact": contact_name, "messages": []}
                msgs.append(contact_chat)
            else:
                print("Contact not found and not created. Returning to menu.")
                continue

        # Show chat history
        show_chat(contact_chat)

        # Input sender
        from_whom = input("\nEnter sender name: ").strip().lower()

        # If "me" → show Gemini suggestions
        if from_whom == "me":
            chat_text = "\n".join(
                [f"{m['from']}: {m['message']}" for m in contact_chat["messages"]]
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

        # If not me → manual message
        else:
            message = input("Enter your message: ").strip()

        # Save to JSON
        contact_chat["messages"].append({"from": from_whom, "message": message})
        save_data(msgs)

        print("\nMessage saved successfully!")
        show_chat(contact_chat)

    # Option 2 → View Messages
    elif choice == "2":
        show_contacts(msgs)
        contact_name = input("\nEnter contact name to view messages: ").strip().lower()

        for ctct in msgs:
            if ctct["contact"].lower() == contact_name:
                show_chat(ctct)
            else:
                print("Contact not found.")

    # Exit
    elif choice == "9":
        print("\nExiting program...")
        break

    else:
        print("Invalid choice! Try again.")
