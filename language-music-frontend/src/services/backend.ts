import axios from "axios";
import { Song } from "@/models/song";
import { initializeApp } from "firebase/app";
import {
  getFirestore,
  collection,
  getDocs,
  query,
  where,
  limit,
} from "firebase/firestore";

/**
 * GitLeaks complains about this key, but in fact it's fine if it is public. It has to be shared with the user anyway
 * for the app to work, and it is restricted to access only cloud firestore.
 *
 * More details: https://stackoverflow.com/questions/37482366/is-it-safe-to-expose-firebase-apikey-to-the-public
 */
const firebaseConfig = {
  apiKey: "AIzaSyD86mT3nUupXb5dHFsU7UiBfKPza0HGDSQ",
  authDomain: "stracensus.firebaseapp.com",
  projectId: "stracensus",
  storageBucket: "stracensus.appspot.com",
  messagingSenderId: "45713463861",
  appId: "1:45713463861:web:5ea8396fbe6002181eaf7c",
};

initializeApp(firebaseConfig);

class BackendService {
  private readonly baseUrl: string =
    process.env.BACKEND_URL || "http://localhost:8000";

  public getSong = async (language: string): Promise<Song> => {
    const db = getFirestore();

    const songDoc = await getDocs(
      query(
        collection(db, "songs"),
        where("language", "==", language),
        limit(1),
      ),
    );
    return songDoc.docs[0].data() as Song;
  };
}

const backendService = new BackendService();

export default backendService;
