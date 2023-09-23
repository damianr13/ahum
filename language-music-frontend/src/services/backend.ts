import axios from 'axios';
import {Song} from "@/models/song";
import { initializeApp } from "firebase/app";
import { getFirestore, collection, getDocs, query, where, limit } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyD86mT3nUupXb5dHFsU7UiBfKPza0HGDSQ",
  authDomain: "stracensus.firebaseapp.com",
  projectId: "stracensus",
  storageBucket: "stracensus.appspot.com",
  messagingSenderId: "45713463861",
  appId: "1:45713463861:web:5ea8396fbe6002181eaf7c"
};

initializeApp(firebaseConfig);

class BackendService {

  private readonly baseUrl: string = process.env.BACKEND_URL || 'http://localhost:8000';

  public getSong = async (language: string): Promise<Song> => {
    const db = getFirestore();

    const songDoc = await getDocs(query(collection(db, "songs"), where("language", "==", language), limit(1)));
    return songDoc.docs[0].data() as Song;
  }
}

const backendService = new BackendService()

export default backendService;