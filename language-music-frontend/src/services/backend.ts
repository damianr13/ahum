import axios from 'axios';
import {Song} from "@/models/song";

class BackendService {

  private readonly baseUrl: string = process.env.BACKEND_URL || 'http://localhost:8000';

  public getLyrics = async (song: string) => {
    const response = await axios.get(`${this.baseUrl}/lyrics`, {
      params: {
        q: song
      },

    })
    return response.data;
  }

  public getSong = async (language: string): Promise<Song> => {
    const response = await axios.get(`${this.baseUrl}/song`, {
        params: {
            language
        },
    })

    return response.data;
  }
}

const backendService = new BackendService()

export default backendService;