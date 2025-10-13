# AI Career 6 Months - Frontend

React + Vite 기반의 AI 챗봇 프론트엔드 애플리케이션입니다.

## 🚀 기술 스택

- **React 18** - UI 라이브러리
- **Vite** - 빌드 도구 및 개발 서버
- **React Router** - 클라이언트 사이드 라우팅
- **Tailwind CSS** - 유틸리티 우선 CSS 프레임워크
- **Recharts** - React 차트 라이브러리
- **Axios** - HTTP 클라이언트

## 📁 프로젝트 구조

```
frontend/
├── src/
│   ├── components/      # 재사용 가능한 컴포넌트
│   │   └── Navigation.jsx
│   ├── pages/           # 페이지 컴포넌트
│   │   ├── ChatPage.jsx       # 챗봇 페이지
│   │   ├── Dashboard.jsx      # 통계 대시보드
│   │   └── SentimentTrend.jsx # 감정 트렌드
│   ├── App.jsx          # 라우터 설정
│   ├── main.jsx         # 앱 진입점
│   └── index.css        # Tailwind 설정
├── public/              # 정적 파일
├── package.json
└── vite.config.js       # Vite 설정
```

## 🎯 주요 기능

### 1. 챗봇 페이지 (`/`)
- RAG 기반 AI 챗봇
- 개인화 모드 지원
- 대화 기록 조회

### 2. 대시보드 (`/dashboard`)
- **일별 대화 통계**: LineChart로 시각화
- **주제별 비율**: PieChart로 시각화

### 3. 감정 트렌드 (`/trend`)
- **날짜별 감정 분포**: 긍정/중립/부정 LineChart
- **감정 데이터 테이블**: 수치 데이터 표시

## 🛠️ 설치 및 실행

### 개발 환경 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행 (http://localhost:5173)
npm run dev
```

### 프로덕션 빌드

```bash
# 빌드 (dist/ 폴더에 생성)
npm run build

# 빌드 결과 미리보기
npm run preview
```

## ⚙️ 환경 설정

### Vite 프록시 설정

개발 환경에서 백엔드 API 요청을 프록시합니다:

```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
})
```

### Tailwind CSS

`tailwind.config.js`에서 커스터마이징 가능합니다.

## 🔌 API 연동

### 백엔드 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/rag-chat` | RAG 챗봇 응답 |
| POST | `/api/personal-chat` | 개인화 챗봇 응답 |
| GET | `/api/conversation/logs` | 대화 기록 조회 |
| GET | `/api/insights/stats` | 일별 대화 통계 |
| GET | `/api/insights/topics` | 주제별 통계 |
| GET | `/api/insights/sentiment-trend` | 감정 트렌드 |

### 예시 코드

```javascript
import axios from "axios";

// RAG 챗봇 호출
const res = await axios.post("/api/rag-chat", {
  question: "질문 내용"
});
console.log(res.data.answer);

// 통계 조회
const stats = await axios.get("/api/insights/stats");
console.log(stats.data);
```

## 📊 차트 라이브러리 (Recharts)

### LineChart 예시

```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

<LineChart width={600} height={300} data={data}>
  <XAxis dataKey="date" />
  <YAxis />
  <CartesianGrid stroke="#ccc" />
  <Line type="monotone" dataKey="count" stroke="#3b82f6" />
  <Tooltip />
</LineChart>
```

### PieChart 예시

```jsx
import { PieChart, Pie, Cell, Legend } from "recharts";

<PieChart width={600} height={300}>
  <Pie
    data={topics}
    dataKey="count"
    nameKey="topic"
    cx="50%"
    cy="50%"
    outerRadius={100}
    label
  >
    {topics.map((_, i) => (
      <Cell key={i} fill={colors[i % colors.length]} />
    ))}
  </Pie>
  <Legend />
</PieChart>
```

## 🎨 스타일링 (Tailwind CSS)

### 자주 사용하는 클래스

```jsx
// 카드 스타일
<div className="bg-white p-6 rounded-xl shadow-md">
  ...
</div>

// 버튼 스타일
<button className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600">
  클릭
</button>

// 레이아웃
<div className="min-h-screen bg-gray-100 p-6">
  <div className="max-w-4xl mx-auto space-y-6">
    ...
  </div>
</div>
```

## 🔍 개발 팁

### React Router 네비게이션

```jsx
import { Link } from "react-router-dom";

<Link to="/dashboard">대시보드로 이동</Link>
```

### Axios 에러 처리

```javascript
try {
  const res = await axios.get("/api/data");
  setData(res.data);
} catch (err) {
  console.error("데이터 조회 실패:", err);
}
```

### Promise.all로 병렬 API 호출

```javascript
const [statsRes, topicsRes] = await Promise.all([
  axios.get("/api/insights/stats"),
  axios.get("/api/insights/topics")
]);
```

## 📦 배포

프로덕션 빌드 후 FastAPI StaticFiles로 서빙:

```python
# backend/app/main.py
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License.

## 📞 문의

프로젝트 관련 문의사항은 GitHub Issues를 이용해주세요.
