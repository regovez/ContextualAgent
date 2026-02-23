import os
import sqlite3
import json

def init_db():

    if os.path.exists("submissions.db"):
        os.remove("submissions.db")

    with sqlite3.connect("submissions.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY,
                document_id INTEGER,
                path TEXT, 
                contact TEXT, 
                status TEXT DEFAULT 'Pending', 
                transcript TEXT DEFAULT '{}'
            )
        """)
        conn.commit()


def approve_submission(id, document_id, filename, contact):
    """Initializes an entry in the database so the agent can start work."""
    with sqlite3.connect("submissions.db") as conn:
        cursor = conn.cursor()

        # We initialize the transcript as an empty JSON object "{}"
        # to avoid JSON decoding errors later.
        cursor.execute("""
            INSERT INTO submissions (id, document_id, path, contact, status, transcript)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id, document_id, filename, contact, 'Pending', '{}'))
        print(f"Saved: {id}, {document_id}, {filename}, {contact}")

        return cursor.lastrowid  # This returns the new sub_id

def save_complete_questioning(sub_id, transcript):
    with sqlite3.connect("submissions.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT transcript FROM submissions WHERE id = ?", (sub_id,))

        row = cursor.fetchone()

        if row is not None:
            conn.execute(
                "UPDATE submissions SET transcript = ?, status = 'In Conversation' WHERE id = ?",
                (json.dumps(transcript), sub_id)
            )
        else:
            # Handle the case where the ID doesn't exist (logging, raising an error, etc.)
            print(f"Error: No submission found with ID {sub_id}")


def save_answer(sub_id, question, answer):
    with sqlite3.connect("submissions.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT transcript FROM submissions WHERE id = ?", (sub_id,))

        row = cursor.fetchone()

        if row is not None:
            # If the row exists, load the JSON from the first column
            transcript = json.loads(row[0])
            transcript[question] = answer

            conn.execute(
                "UPDATE submissions SET transcript = ?, status = 'In Conversation' WHERE id = ?",
                (json.dumps(transcript), sub_id)
            )
        else:
            # Handle the case where the ID doesn't exist (logging, raising an error, etc.)
            print(f"Error: No submission found with ID {sub_id}")

def pptx_created(sub_id):
    # ADD THIS: Update to 'Summary Generated' so the Tracker shows the button
    with sqlite3.connect("submissions.db") as conn:
        conn.execute("UPDATE submissions SET status = 'Summary Generated' WHERE id = ?", (sub_id,))