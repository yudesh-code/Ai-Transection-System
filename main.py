# ============================================
# AI TRANSACTION SYSTEM 
# ============================================
# Features:
# - AI-like natural command system
# - Voice + Text input (auto fallback)
# - Blockchain-style transaction storage
# - Privacy masking
# - Transaction verification (Txn ID)
# ============================================

import hashlib
import datetime
import re

# -------- VOICE SUPPORT --------
try:
    import speech_recognition as sr
    VOICE = True
except:
    VOICE = False

blockchain = []

# ============================================
# BLOCK CLASS
# ============================================

class Block:
    def __init__(self, data, prev_hash):
        self.timestamp = str(datetime.datetime.now())
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.create_hash()
        self.txn_id = self.hash[:10]

    def create_hash(self):
        text = self.timestamp + self.data + self.prev_hash
        return hashlib.sha256(text.encode()).hexdigest()


# ============================================
# BLOCKCHAIN ADD
# ============================================

def add_block(data):
    prev_hash = blockchain[-1].hash if blockchain else "0000"
    block = Block(data, prev_hash)
    blockchain.append(block)
    return block.txn_id


# ============================================
# PRIVACY
# ============================================

def mask_amount(amount):
    amount = str(amount)
    if len(amount) <= 2:
        return "*" * len(amount)
    return amount[0] + "*" * (len(amount)-2) + amount[-1]


def mask_name(name):
    if len(name) <= 2:
        return "*" * len(name)
    return name[0] + "*" * (len(name)-1)


# ============================================
# UTIL
# ============================================

def extract_numbers(text):
    return list(map(int, re.findall(r'\d+', text)))


# ============================================
# HISTORY
# ============================================

def show_history():
    if not blockchain:
        print("No transactions.")
        return
    
    for i, block in enumerate(blockchain):
        print(f"\nBlock {i+1}")
        print("Txn ID:", block.txn_id)
        print("Data:", block.data)
        print("Hash:", block.hash)


# ============================================
# VERIFY
# ============================================

def verify_transaction(txn_id):
    for block in blockchain:
        if block.txn_id == txn_id:
            print("✅ Valid transaction")
            print("Data:", block.data)
            return
    print("❌ Transaction not found")


# ============================================
# VOICE INPUT
# ============================================

def get_voice_input():
    if not VOICE:
        return None

    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("🎤 Speak...")
            audio = r.listen(source)

        text = r.recognize_google(audio)
        print("You (voice):", text)
        return text.lower()

    except:
        print("⚠️ Voice failed, using text input")
        return None


# ============================================
# MAIN PROCESS LOGIC
# ============================================

def process(user_input):
    text = user_input.lower()
    words = text.split()

    # Greeting
    if any(word in ["hi", "hello", "hey"] for word in words):
        return "Hello 👋, system ready."

    # -------- SEND --------
    if any(word in ["send", "pay", "give"] for word in words):

        nums = extract_numbers(text)

        if len(nums) >= 1:
            amount = nums[0]

            filtered = [w for w in words if w not in ["send", "pay", "give", "to"] and not w.isdigit()]

            if not filtered:
                return "❌ Receiver not found"

            receiver = filtered[-1]

            print(f"\nSend: {amount} → {receiver}")
            confirm = input("Confirm (yes/no): ")

            if confirm.lower() == "yes":
                masked_amount = mask_amount(amount)
                masked_name = mask_name(receiver)
                txn_id = add_block(f"Send {masked_amount} to {masked_name}")
                return f"✅ Done | Txn ID: {txn_id}"
            else:
                return "❌ Cancelled"

        return "❌ Amount missing"

    # -------- SPLIT --------
    if "split" in words:

        nums = extract_numbers(text)

        if len(nums) >= 2:
            amount = nums[0]
            people = nums[1]
            each = amount // people

            print(f"\nSplit: {amount} → {people} people → Each: {each}")
            confirm = input("Confirm (yes/no): ")

            if confirm.lower() == "yes":
                masked_amount = mask_amount(amount)
                txn_id = add_block(f"Split {masked_amount} among {people}")
                return f"✅ Done | Txn ID: {txn_id}"
            else:
                return "❌ Cancelled"

        return "❌ Missing data"

    # -------- HISTORY --------
    if "history" in words:
        show_history()
        return ""

    # -------- VERIFY --------
    if "verify" in words:
        if len(words) >= 2:
            verify_transaction(words[1])
            return ""
        return "❌ Provide Txn ID"

    return "❌ Command not recognized"


# ============================================
# MAIN LOOP
# ============================================

print("🔐 AI Transaction System Ready\n")

mode = input("Mode (voice/text): ").lower()

while True:

    if mode == "voice":
        user = get_voice_input()
        if not user:
            user = input("You (type): ")
    else:
        user = input("You: ")

    if user.lower() == "exit":
        print("System closed.")
        break

    response = process(user)

    if response:
        print("AI:", response)
