from cryptography.fernet import Fernet
import datetime
import json
import os

# Create a fixed safe folder for MEMOIR files inside Documents
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "MEMOIR")
os.makedirs(BASE_DIR, exist_ok=True)

DATA_FILE = os.path.join(BASE_DIR, "memories.json")
KEY_FILE = os.path.join(BASE_DIR, "secret.key")

# Generate encryption key (do this once and reuse)
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as f:
        f.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as f:
    key = f.read()

cipher = Fernet(key)

# Load existing memories
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        memories = json.load(f)
else:
    memories = []

def save_memory():
    message = input("Write your memory: ")
    date_str = input("Unlock date (YYYY-MM-DD): ")
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    encrypted = cipher.encrypt(message.encode()).decode()

    memories.append({"date": date_str, "memory": encrypted})

    with open(DATA_FILE, "w") as f:
        json.dump(memories, f, indent=4)

    print("✅ Memory saved & encrypted!")

def view_memories():
    today = datetime.date.today()
    print("\n--- Your Memories ---")
    for m in memories:
        unlock_date = datetime.datetime.strptime(m["date"], "%Y-%m-%d").date()
        if today >= unlock_date:
            decrypted = cipher.decrypt(m["memory"].encode()).decode()
            print(f"📖 [{m['date']}] {decrypted}")
        else:
            print(f"🔒 [{m['date']}] Locked until this date!")

def delete_memory():
    if not memories:
        print("⚠ No memories saved yet.")
        return

    print("\n--- Delete a Memory ---")
    for i, m in enumerate(memories):
        print(f"{i+1}. {m['date']}")

    choice = input("Enter the number of the memory to delete (or press Enter to cancel): ")

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(memories):
            removed = memories.pop(index)
            with open(DATA_FILE, "w") as f:
                json.dump(memories, f, indent=4)
            print(f"🗑 Deleted memory from {removed['date']}")
        else:
            print("❌ Invalid choice")
    else:
        print("❌ Cancelled")

def delete_all_memories():
    confirm = input("⚠ Are you sure you want to delete ALL memories? (yes/no): ")
    if confirm.lower() == "yes":
        memories.clear()
        with open(DATA_FILE, "w") as f:
            json.dump(memories, f, indent=4)
        print("🗑 All memories deleted!")
    else:
        print("❌ Cancelled")

# Main Menu Loop
while True:
    print("\n1. Save Memory")
    print("2. View Memories")
    print("3. Delete Memory")
    print("4. Delete All Memories")
    print("5. Exit")
    choice = input("Choose: ")
    if choice == "1":
        save_memory()
    elif choice == "2":
        view_memories()
    elif choice == "3":
        delete_memory()
    elif choice == "4":
        delete_all_memories()
    elif choice == "5":
        break
