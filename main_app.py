import os
import sys
import json
import logging
import atexit
import sqlite3  
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet
import base64

# ---------------- Logger Setup ----------------
logfile = "app.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Logger initialized: Logging to console and app.log")

# ---------------- Secure History Encryption Setup ----------------
SECURE_HISTORY_FILE = "secure_history.enc"
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"

def generate_keys():
    if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        logger.info("RSA key pair generated for secure history.")
    else:
        logger.info("RSA key pair for secure history already exists.")

def load_keys():
    with open(PRIVATE_KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(PUBLIC_KEY_FILE, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return private_key, public_key

def encrypt_history_data(data: bytes) -> bytes:
    """
    Encrypt the history using a generated Fernet key.
    The Fernet key is encrypted using the RSA public key.
    """
    fernet_key = Fernet.generate_key()
    f = Fernet(fernet_key)
    encrypted_data = f.encrypt(data)
    # Encrypt the symmetric key with RSA public key.
    _, public_key = load_keys()
    encrypted_key = public_key.encrypt(
        fernet_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    payload = {
        "encrypted_key": base64.b64encode(encrypted_key).decode('utf-8'),
        "encrypted_data": base64.b64encode(encrypted_data).decode('utf-8')
    }
    return json.dumps(payload).encode('utf-8')

def decrypt_history_data(enc_payload: bytes) -> bytes:
    payload = json.loads(enc_payload.decode('utf-8'))
    encrypted_key = base64.b64decode(payload["encrypted_key"])
    encrypted_data = base64.b64decode(payload["encrypted_data"])
    private_key, _ = load_keys()
    fernet_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    f = Fernet(fernet_key)
    decrypted = f.decrypt(encrypted_data)
    return decrypted

# ---------------- In-Memory Secure History ----------------
secure_history = []  # List that stores all request and response history

def load_secure_history():
    global secure_history
    if os.path.exists(SECURE_HISTORY_FILE):
        try:
            with open(SECURE_HISTORY_FILE, "rb") as f:
                enc_payload = f.read()
            decrypted = decrypt_history_data(enc_payload)
            secure_history = json.loads(decrypted.decode('utf-8'))
            logger.info("Secure history loaded from file.")
        except Exception as e:
            logger.error(f"Error loading secure history: {e}")
            secure_history = []
    else:
        secure_history = []
        logger.info("No secure history file found; starting with empty history.")

def save_secure_history():
    try:
        data = json.dumps(secure_history).encode('utf-8')
        enc_data = encrypt_history_data(data)
        with open(SECURE_HISTORY_FILE, "wb") as f:
            f.write(enc_data)
        logger.info("Secure history saved to file.")
    except Exception as e:
        logger.error(f"Error saving secure history: {e}")

atexit.register(save_secure_history)

# ---------------- Measurement Conversion Logic ----------------
def char_to_value(c):
    if c == '_':
        return 0
    if 'a' <= c <= 'z':
        return ord(c) - ord('a') + 1
    raise ValueError(f"Invalid character '{c}' in input string")

def parse_recursive(s: str):
    logger.info(f"Starting conversion for input string: {s}")
    result = []
    index = 0
    while index < len(s):
        if s[index] == 'z':
            total = 0
            while index < len(s) and s[index] == 'z':
                total += char_to_value(s[index])
                index += 1
            if index < len(s):
                total += char_to_value(s[index])
                index += 1
            count = total
            logger.info(f"Chain segment processed. Derived count: {count}")
            values = []
            for i in range(count):
                if index < len(s):
                    if s[index] == 'z':
                        total = 0
                        while index < len(s) and s[index] == 'z':
                            total += char_to_value(s[index])
                            index += 1
                        if index < len(s):
                            total += char_to_value(s[index])
                            index += 1
                        values.append(total)
                    else:
                        values.append(char_to_value(s[index]))
                        index += 1
            seg_sum = sum(values)
            logger.info(f"Count-based segment processed with sum: {seg_sum}")
            result.append(seg_sum)
        else:
            count = char_to_value(s[index])
            index += 1
            logger.info(f"Processing direct count segment. Count: {count}")
            values1 = []
            for i in range(count):
                if index < len(s):
                    if s[index] == 'z':
                        total = 0
                        while index < len(s) and s[index] == 'z':
                            total += char_to_value(s[index])
                            index += 1
                        if index < len(s):
                            total += char_to_value(s[index])
                            index += 1
                        values1.append(total)
                    else:
                        values1.append(char_to_value(s[index]))
                        index += 1
            seg_sum = sum(values1)
            logger.info(f"Direct count segment processed with sum: {seg_sum}")
            result.append(seg_sum)
    logger.info(f"Conversion result: {result}")
    return result

# ---------------- Domain Model Classes ----------------
class Sequence:
    def __init__(self, value: list):
        self._value = value

    def set_value(self, value: list):
        self._value = value

    def get_value_as_str(self) -> str:
        return "".join(self._value)

    def is_valid(self) -> bool:
        s = self.get_value_as_str()
        valid = all(c.islower() or c == '_' for c in s)
        if not valid:
            logger.warning(f"Sequence validation failed for: {s}")
        return valid

# ---------------- SQLite-Based Request History (unchanged part) ----------------
class SequenceHistory:
    def __init__(self):
        self.db_file = "history.db"
        self.connection = None
        self.create_table()

    def create_table(self):
        self.connection = sqlite3.connect(self.db_file, check_same_thread=False)
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence TEXT,
                processed TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
        logger.info("SQLite history table ensured in history.db")

    def save_curr_seq(self, seq: Sequence, processed: list) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO history (sequence, processed) VALUES (?, ?)",
                       (seq.get_value_as_str(), json.dumps(processed)))
        self.connection.commit()
        logger.info("Sequence and processed result saved to SQLite history.")
        return True

    def get_history(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, sequence, processed, timestamp FROM history ORDER BY id DESC")
        rows = cursor.fetchall()
        history = [{"id": row[0],
                    "sequence": row[1],
                    "processed": json.loads(row[2]),
                    "timestamp": row[3]} for row in rows]
        return history

class SequenceService:
    def __init__(self):
        self.sequence_history = SequenceHistory()
        logger.info("SequenceService initialized.")

    def get_sequence(self, s: str) -> Sequence:
        logger.info(f"Creating sequence from input: {s}")
        return Sequence(list(s))

    def process_sequence(self, seq: Sequence) -> list:
        s = seq.get_value_as_str()
        logger.info(f"Processing sequence: {s}")
        return parse_recursive(s)

class SequenceController:
    def __init__(self, exposed: bool = True):
        self.exposed = exposed
        self.sequence_service = SequenceService()
        logger.info("SequenceController initialized.")

    def GET(self, obj: dict) -> dict:
        input_str = obj.get("input", "")
        logger.info(f"Processing input: {input_str}")
        seq = self.sequence_service.get_sequence(input_str)
        if not seq.is_valid():
            logger.error("Invalid sequence received.")
            return {"error": "Invalid sequence"}
        processed = self.sequence_service.process_sequence(seq)
        # Persist in SQLite.
        self.sequence_service.sequence_history.save_curr_seq(seq, processed)
        # Update secure in-memory history.
        entry = {
            "sequence": seq.get_value_as_str(),
            "processed": processed
        }
        secure_history.append(entry)
        logger.info("Sequence processed and secure history updated.")
        return {"processed": processed, "sequence": seq.get_value_as_str()}

# ---------------- FastAPI Setup ----------------
app = FastAPI()
controller = SequenceController()

@app.get("/convert-measurements")
def convert_measurements(input: str = Query(..., description="Measurement input string")):
    try:
        response = controller.GET({"input": input})
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})

# Dedicated API endpoint to access secure local history.
@app.get("/secure-history")
def get_secure_history():
    return JSONResponse(content={"secure_history": secure_history})

@app.get("/history")
def get_history():
    history = controller.sequence_service.sequence_history.get_history()
    return JSONResponse(content={"history": history})

# ---------------- Main Entry Point ----------------
if __name__ == "__main__":
    generate_keys()
    load_secure_history()  # Load secure history from file on startup.
    default_port = 8080
    port = default_port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception as e:
            logger.error(f"Invalid port argument provided; using default port {default_port}: {e}")
    logger.info(f"Starting FastAPI server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)