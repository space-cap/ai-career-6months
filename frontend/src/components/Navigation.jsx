import { Link } from "react-router-dom";

function Navigation() {
  return (
    <nav className="bg-blue-600 p-4 shadow-md">
      <div className="max-w-7xl mx-auto flex gap-6">
        <Link
          to="/"
          className="text-white hover:text-blue-200 font-semibold transition"
        >
          💬 챗봇
        </Link>
        <Link
          to="/dashboard"
          className="text-white hover:text-blue-200 font-semibold transition"
        >
          📊 대시보드
        </Link>
      </div>
    </nav>
  );
}

export default Navigation;
