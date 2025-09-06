import os
import json
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime


#  CONFIGURATION

BASE_DIR = os.path.expanduser("~")  # User's home folder
DATA_FOLDER = os.path.join(BASE_DIR, "MemoirData")
KEY_FILE = os.path.join(DATA_FOLDER, "secret.key")
DATA_FILE = os.path.join(DATA_FOLDER, "memories.json")
PIN_FILE = os.path.join(DATA_FOLDER, "pin.json")

# Ensure folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)


#  ENCRYPTION FUNCTIONS

def load_key():
    """Load or create encryption key"""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)


fernet = load_key()


#  PIN HANDLING

def hash_pin(pin: str) -> str:
    """Hash PIN using SHA256 (never store plain PIN)"""
    return hashlib.sha256(pin.encode()).hexdigest()


def setup_pin():
    """Setup master PIN on first run"""
    if not os.path.exists(PIN_FILE):
        print("\nSet up your MEMOIR master PIN:")
        while True:
            pin = input("Enter a new PIN: ")
            confirm = input("Confirm your PIN: ")
            if pin == confirm and pin.strip():
                with open(PIN_FILE, "w") as f:
                    json.dump({"pin_hash": hash_pin(pin)}, f)
                print("PIN set successfully!\n")
                break
            else:
                print("PINs do not match. Try again.")
    else:
        with open(PIN_FILE, "r") as f:
            saved = json.load(f)
        for attempt in range(3):
            pin = input("Enter your MEMOIR PIN: ")
            if hash_pin(pin) == saved["pin_hash"]:
                print("Access granted!\n")
                return
            else:
                print("Wrong PIN.")
        print("Too many wrong attempts. Exiting...")
        exit()


#  MEMORY FUNCTIONS

def load_memories():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_memories(memories):
    with open(DATA_FILE, "w") as f:
        json.dump(memories, f, indent=4)


def add_memory():
    text = input("Enter your memory: ")
    unlock_date = input("Enter unlock date (YYYY-MM-DD): ")

    encrypted_text = fernet.encrypt(text.encode()).decode()

    memories = load_memories()
    memories.append({
        "memory": encrypted_text,
        "unlock_date": unlock_date
    })
    save_memories(memories)
    print("Memory saved!")


def view_specific_memory():
    memories = load_memories()
    today = datetime.today().date()

    if not memories:
        print("No memories saved yet.")
        return

    # Show list of memories with unlock date
    print("\n===== Your Memories =====")
    for i, mem in enumerate(memories, start=1):
        unlock_date = datetime.strptime(mem["unlock_date"], "%Y-%m-%d").date()
        status = "Unlocked" if today >= unlock_date else f"Locked until {unlock_date}"
        print(f"{i}. Memory ({status}) - Unlock date: {unlock_date}")

    try:
        choice = int(input("\nEnter the memory number to view: "))
        if 1 <= choice <= len(memories):
            mem = memories[choice - 1]
            unlock_date = datetime.strptime(mem["unlock_date"], "%Y-%m-%d").date()
            if today >= unlock_date:
                decrypted = fernet.decrypt(mem["memory"].encode()).decode()
                print(f"\nMemory {choice}: {decrypted}")
            else:
                print(f"This memory is locked until {unlock_date}.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")


def delete_memory():
    memories = load_memories()

    if not memories:
        print("No memories to delete.")
        return

    # Show list of memories
    print("\n===== Delete a Memory =====")
    for i, mem in enumerate(memories, start=1):
        print(f"{i}. Unlock date: {mem['unlock_date']}")

    try:
        choice = int(input("\nEnter the memory number to delete: "))
        if 1 <= choice <= len(memories):
            confirm = input(f"Are you sure you want to delete memory {choice}? (y/n): ").lower()
            if confirm == "y":
                deleted = memories.pop(choice - 1)
                save_memories(memories)
                print("Memory deleted successfully.")
            else:
                print("Deletion cancelled.")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")


#  MAIN MENU

def main_menu():
    while True:
        print("\n===== MEMOIR - Your Digital Diary =====")
        print("1. Add a memory")
        print("2. View a memory")
        print("3. Delete a memory")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            add_memory()
        elif choice == "2":
            view_specific_memory()
        elif choice == "3":
            delete_memory()
        elif choice == "4":
            print("Goodbye! Stay safe with your memories.")
            break
        else:
            print("Invalid choice, try again.")


#  PROGRAM START

if __name__ == "__main__":
    setup_pin()
    main_menu()
