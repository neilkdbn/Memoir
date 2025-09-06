import os
import json
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox

# =========================
#  CONFIGURATION
# =========================
BASE_DIR = os.path.expanduser("~")
DATA_FOLDER = os.path.join(BASE_DIR, "MemoirData")
KEY_FILE = os.path.join(DATA_FOLDER, "secret.key")
DATA_FILE = os.path.join(DATA_FOLDER, "memories.json")
PIN_FILE = os.path.join(DATA_FOLDER, "pin.json")
os.makedirs(DATA_FOLDER, exist_ok=True)

# Colors & Fonts
BG_COLOR = "#F9F9E0"   
ACCENT_COLOR = "#2C3639"  
BUTTON_COLOR = "#F7CAC9"
FONT_TITLE = ("Palatino Linotype", 60)
FONT_SUBTITLE = ("Palatino Linotype", 35)
FONT_BUTTON = ("SansSerif", 18)
FONT_TEXT = ("SansSerif", 16)

# =========================
#  ENCRYPTION
# =========================
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

fernet = load_key()

# =========================
#  PIN HANDLING
# =========================
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def is_pin_set():
    return os.path.exists(PIN_FILE)

def check_pin(pin):
    with open(PIN_FILE, "r") as f:
        saved = json.load(f)
    return hash_pin(pin) == saved["pin_hash"]

def save_pin(pin):
    with open(PIN_FILE, "w") as f:
        json.dump({"pin_hash": hash_pin(pin)}, f)

# =========================
#  MEMORY FUNCTIONS
# =========================
def load_memories():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_memories(memories):
    with open(DATA_FILE, "w") as f:
        json.dump(memories, f, indent=4)

# =========================
#  MAIN APP CLASS
# =========================
class MemoirApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MEMOIR - Your Digital Diary")
        self.state("zoomed")  # Fullscreen
        ctk.set_appearance_mode("light")  

        # Set background color
        self.configure(fg_color=BG_COLOR)

        self.container = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (PinScreen, MainMenu, AddMemory, ViewMemory, DeleteMemory):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(PinScreen)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()

# =========================
#  PIN SCREEN
# =========================
class PinScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller

        ctk.CTkLabel(self, text="MEMOIR", font=FONT_TITLE, text_color=ACCENT_COLOR).pack(pady=60)

        self.pin_entry = ctk.CTkEntry(
            self, placeholder_text="Enter PIN", show="*", width=300,
            font=FONT_TEXT, fg_color=BG_COLOR, text_color=ACCENT_COLOR
        )
        self.pin_entry.pack(pady=20)

        self.confirm_entry = None
        if not is_pin_set():
            self.confirm_entry = ctk.CTkEntry(
                self, placeholder_text="Confirm PIN", show="*", width=300,
                font=FONT_TEXT, fg_color=BG_COLOR, text_color=ACCENT_COLOR
            )
            self.confirm_entry.pack(pady=10)

        ctk.CTkButton(
            self, text="Unlock", command=self.verify_pin, width=200, height=50,
            font=FONT_BUTTON, fg_color=BG_COLOR, text_color=ACCENT_COLOR, hover_color=BUTTON_COLOR
        ).pack(pady=30)


    def verify_pin(self):
        pin = self.pin_entry.get()
        if not is_pin_set():
            confirm = self.confirm_entry.get()
            if pin and pin == confirm:
                save_pin(pin)
                messagebox.showinfo("Success", "PIN set successfully!")
                self.controller.show_frame(MainMenu)
            else:
                messagebox.showerror("Error", "PINs do not match.")
        else:
            if check_pin(pin):
                self.controller.show_frame(MainMenu)
            else:
                messagebox.showerror("Error", "Incorrect PIN")

# =========================
#  MAIN MENU
# =========================
class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller

        ctk.CTkLabel(self, text="Welcome to MEMOIR", font=FONT_SUBTITLE, text_color=ACCENT_COLOR).pack(pady=50)

        for text, page in [
            ("Add Memory", AddMemory),
            ("View Memory", ViewMemory),
            ("Delete Memory", DeleteMemory)
        ]:
            ctk.CTkButton(self, text=text, command=lambda p=page: controller.show_frame(p),
                          width=300, height=60, font=FONT_BUTTON,
                          fg_color=BUTTON_COLOR, text_color=ACCENT_COLOR).pack(pady=15)

        ctk.CTkButton(self, text="Exit", command=self.quit,
                      width=300, height=60, font=FONT_BUTTON,
                      fg_color="#FE5050", text_color="white").pack(pady=20)

# =========================
#  ADD MEMORY
# =========================
class AddMemory(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller

        ctk.CTkLabel(self, text="Add a Memory", font=FONT_SUBTITLE, text_color=ACCENT_COLOR).pack(pady=20)

        self.text_box = ctk.CTkTextbox(self, width=600, height=200, font=FONT_TEXT, fg_color="white", text_color="black")
        self.text_box.pack(pady=20)

        self.date_entry = ctk.CTkEntry(self, placeholder_text="Unlock date (YYYY-MM-DD)", width=300, font=FONT_TEXT, fg_color="white")
        self.date_entry.pack(pady=10)

        ctk.CTkButton(self, text="Save", command=self.save_memory, width=200, height=50,
                      font=FONT_BUTTON, fg_color=ACCENT_COLOR, text_color="black").pack(pady=20)
        ctk.CTkButton(self, text="⬅ Back", command=lambda: controller.show_frame(MainMenu),
                      width=200, height=50, font=FONT_BUTTON, fg_color="grey", text_color="white").pack(pady=10)

    def save_memory(self):
        text = self.text_box.get("1.0", "end").strip()
        unlock_date = self.date_entry.get().strip()
        if not text or not unlock_date:
            messagebox.showerror("Error", "All fields required!")
            return
        try:
            datetime.strptime(unlock_date, "%Y-%m-%d")
            encrypted_text = fernet.encrypt(text.encode()).decode()
            memories = load_memories()
            memories.append({"memory": encrypted_text, "unlock_date": unlock_date})
            save_memories(memories)
            messagebox.showinfo("Saved", "Memory saved!")
            self.controller.show_frame(MainMenu)
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")

# =========================
#  VIEW MEMORY
# =========================
class ViewMemory(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller

        ctk.CTkLabel(self, text="View Memory", font=FONT_SUBTITLE, text_color=ACCENT_COLOR).pack(pady=20)

        self.memories_list = ctk.CTkOptionMenu(self, values=[], width=400, font=FONT_TEXT, fg_color="white", text_color="black")
        self.memories_list.pack(pady=20)

        ctk.CTkButton(self, text="View", command=self.show_memory, width=200, height=50,
                      font=FONT_BUTTON, fg_color=ACCENT_COLOR, text_color="black").pack(pady=10)
        ctk.CTkButton(self, text="⬅ Back", command=lambda: controller.show_frame(MainMenu),
                      width=200, height=50, font=FONT_BUTTON, fg_color="grey", text_color="white").pack(pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        memories = load_memories()
        self.memories_list.configure(values=[f"{i+1}. Unlock: {m['unlock_date']}" for i, m in enumerate(memories)])

    def show_memory(self):
        idx = self.memories_list.cget("values").index(self.memories_list.get())
        memories = load_memories()
        mem = memories[idx]
        today = datetime.today().date()
        unlock_date = datetime.strptime(mem["unlock_date"], "%Y-%m-%d").date()
        if today >= unlock_date:
            decrypted = fernet.decrypt(mem["memory"].encode()).decode()
            messagebox.showinfo("Memory", decrypted)
        else:
            messagebox.showwarning("Locked", f"This memory is locked until {unlock_date}")

# =========================
#  DELETE MEMORY
# =========================
class DeleteMemory(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=BG_COLOR)
        self.controller = controller

        ctk.CTkLabel(self, text="🗑 Delete Memory", font=FONT_SUBTITLE, text_color=ACCENT_COLOR).pack(pady=20)

        self.memories_list = ctk.CTkOptionMenu(self, values=[], width=400, font=FONT_TEXT, fg_color="white", text_color="black")
        self.memories_list.pack(pady=20)

        ctk.CTkButton(self, text="Delete", command=self.delete_memory, width=200, height=50,
                      font=FONT_BUTTON, fg_color="red", text_color="white").pack(pady=10)
        ctk.CTkButton(self, text="⬅ Back", command=lambda: controller.show_frame(MainMenu),
                      width=200, height=50, font=FONT_BUTTON, fg_color="grey", text_color="white").pack(pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        memories = load_memories()
        self.memories_list.configure(values=[f"{i+1}. Unlock: {m['unlock_date']}" for i, m in enumerate(memories)])

    def delete_memory(self):
        idx = self.memories_list.cget("values").index(self.memories_list.get())
        memories = load_memories()
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this memory?"):
            memories.pop(idx)
            save_memories(memories)
            messagebox.showinfo("Deleted", "Memory deleted successfully")
            self.controller.show_frame(MainMenu)

# =========================
#  RUN APP
# =========================
if __name__ == "__main__":
    app = MemoirApp()
    app.mainloop()
