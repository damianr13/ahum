import axios from 'axios';

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
}

const backendService = new BackendService()

export default backendService;