import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer
} from "recharts";

export default function SentimentTrend() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("/api/insights/sentiment-trend")
      .then((res) => setData(res.data))
      .catch(() => console.error("데이터 불러오기 실패"));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">😊 감정 변화 트렌드</h2>

      {/* 🔹 감정 변화 라인 차트 */}
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data}>
          <CartesianGrid stroke="#eee" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="positive" stroke="#22c55e" name="긍정" strokeWidth={2}/>
          <Line type="monotone" dataKey="neutral" stroke="#facc15" name="중립" strokeWidth={2}/>
          <Line type="monotone" dataKey="negative" stroke="#ef4444" name="부정" strokeWidth={2}/>
        </LineChart>
      </ResponsiveContainer>

      {/* 🔹 감정 데이터 테이블 */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-2">📋 감정 변화 데이터</h3>
        <table className="min-w-full border border-gray-300 text-center">
          <thead className="bg-gray-100">
            <tr>
              <th className="border px-4 py-2">날짜</th>
              <th className="border px-4 py-2 text-green-600">긍정</th>
              <th className="border px-4 py-2 text-yellow-600">중립</th>
              <th className="border px-4 py-2 text-red-600">부정</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="border px-4 py-2">{row.date}</td>
                <td className="border px-4 py-2 text-green-700">{row.positive}</td>
                <td className="border px-4 py-2 text-yellow-700">{row.neutral}</td>
                <td className="border px-4 py-2 text-red-700">{row.negative}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
