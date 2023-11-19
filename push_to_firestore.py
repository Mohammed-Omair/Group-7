import firebase_admin
from firebase_admin import auth, firestore, credentials
import os

if not firebase_admin._apps:
    cred = credentials.Certificate(os.path.join(os.path.dirname(__file__), 'secrets/firebase-adminsdk.json')) 
    default_app = firebase_admin.initialize_app(cred)

db = firestore.client()

#prevous question function 
def prev_ques(email):
   return db.collection(email).stream()

def write_to_firestore(text1, text2, similarity_score, email):
  

  doc_ref = db.collection(email).document()
  doc_ref.set({
    "Sentence_1": text1,
    "Sentence_2": text2,
    "Similarity": similarity_score,
  })
