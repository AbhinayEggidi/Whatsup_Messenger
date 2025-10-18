import json
import os
import requests
from dotenv import load_dotenv

# ------------------ Setup Gemini API ------------------
load_dotenv()
api_key = os.getenv("gemini_api_key")

if not api_key:
    print("Gemini API key not found. Please set 'gemini_api_key' in your .env file.")
    exit()

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"


# ------------------ Gemini Smart Replies ------------------
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
            {"parts": [{"text": prompt}]}
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


# ------------------ Data Operations ------------------
def load_data():
    """Load chat data from messages.json, create file if missing."""
    if not os.path.exists("messages.json"):
        with open("messages.json", "w") as f:
            json.dump([], f)
        return []
    with open("messages.json", "r") as f:
        return json.load(f)


def save_data(data):
    """Save chat data to messages.json."""
    with open("messages.json", "w") as f:
        json.dump(data, f, indent=4)


# ------------------ Contact Operations ------------------
def add_contact(msgs):
    """Add a new contact with an empty messages list."""
    contact_name = input("\nEnter new contact name: ").strip().lower()

    # Check if contact already exists
    exists = any(ctct["contact"].lower() == contact_name for ctct in msgs)
    if exists:
        print("Contact already exists.")
        return msgs

    # Create new contact entry
    new_contact = {"contact": contact_name, "messages": []}
    msgs.append(new_contact)

    # Save updated data
    save_data(msgs)

    print(f"Contact '{contact_name}' added successfully!")
    return msgs


# ------------------ Display Functions ------------------
def show_contacts(msgs):
    print("\nContacts List:")
    if not msgs:
        print("No contacts found.")
    for i, ctct in enumerate(msgs, start=1):
        print(f"{i}. {ctct['contact']}")


def show_chat(contact_chat):
    print(f"\n-- Chat with {contact_chat['contact']} --")

    # If no messages yet
    if not contact_chat["messages"] or len(contact_chat["messages"]) == 0:
        print(f"No messages yet with {contact_chat['contact']}")
        return

    # Otherwise, show all messages
    for msg in contact_chat["messages"]:
        print(f"{msg['from']}: {msg['message']}")



def menu():
    print("\n----------------------")
    print(" Message Manager")
    print("1. Add Message / Chat")
    print("2. View Messages")
    print("3. Add Contact")
    print("9. Exit")
    print("----------------------")
