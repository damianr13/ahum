from functools import lru_cache

import firebase_admin
from firebase_admin import firestore


@lru_cache()
def init_firestore() -> firestore.firestore.Client:
    firebase_app = firebase_admin.initialize_app()
    db = firestore.firestore.Client()

    return db
