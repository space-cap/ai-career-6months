import { BrowserRouter, Routes, Route } from "react-router-dom";
import ChatPage from "./pages/ChatPage";
import Dashboard from "./pages/Dashboard";
import SentimentTrend from "./pages/SentimentTrend";
import Navigation from "./components/Navigation";

function App() {
  return (
    <BrowserRouter>
      <Navigation />
      <Routes>
        <Route path="/" element={<ChatPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/trend" element={<SentimentTrend />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
