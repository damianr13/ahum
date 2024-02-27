import { useState } from "react";
import axios from "axios";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";

const apiUrl = "https://api-inference.huggingface.co/models/your-model-name"; // replace with your model name

function ChatView() {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    [{ role: "system", content: "You are a helpful assistant." }],
  );

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      const response = await axios.post(apiUrl, { inputs: inputValue });
      const newMessage = { role: "assistant", content: response.data };
      setMessages((prevState) => [...prevState, newMessage]);
    } catch (error) {
      console.error(error);
    } finally {
      setInputValue("");
    }
  }

  return (
    <div className="flex h-full flex-col items-end justify-end bg-gray-700">
      <div className="w-full max-w-xl rounded-lg bg-gray-800 text-white p-6 shadow-lg">
        <div className="mb-4 space-y-2 text-sm leading-relaxed">
          {messages.map((message, index) => (
            <p
              key={index}
              className={`break-all ${
                message.role === "assistant" ? "bg-blue-100 p-2" : ""
              }`}
            >
              {message.content}
            </p>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="space-y-2">
          <label htmlFor="user_input" className="sr-only">
            Your message
          </label>
          <div className="flex flex-row gap-4 items-start border text-white border-gray-300 bg-gray-700 px-3 py-2 font-mono outline-none sm:text-sm rounded-lg ">
            <textarea
              id="user_input"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              rows={3}
              placeholder="Type something here..."
              className="min-h-[2rem] w-full bg-transparent resize-none focus:outline-none"
            />
            <button
              type="submit"
              disabled={!inputValue}
              className="inline-block shrink-0 rounded-lg bg-transparent p-2 transition hover:bg-blue-600 active:bg-blue-700 disabled:opacity-50"
            >
              <PaperAirplaneIcon className="w-6 h-6 stroke-blue-200" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ChatView;
