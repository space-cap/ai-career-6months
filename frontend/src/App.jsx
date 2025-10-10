import { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("생각 중... 🤔");

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/rag-chat", {
        question,
      });
      setAnswer(res.data.answer);
    } catch (err) {
      setAnswer("⚠️ 서버 연결 오류!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-6">
      <h1 className="text-3xl font-bold mb-4 text-gray-700">💬 AI Career Chatbot</h1>
      <div className="w-full max-w-lg bg-white p-4 rounded-xl shadow-md">
        <textarea
          rows={3}
          className="w-full border p-3 rounded-md"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="무엇이 궁금한가요?"
        />
        <button
          onClick={sendMessage}
          className="w-full bg-blue-500 text-white p-2 mt-2 rounded-md hover:bg-blue-600"
          disabled={loading}
        >
          {loading ? "전송 중..." : "질문 보내기"}
        </button>
        <div className="mt-4 bg-gray-50 p-3 rounded-md min-h-[100px] text-gray-800">
          {answer && <p>{answer}</p>}
        </div>
      </div>
    </div>
  );
}

export default App;
