# 🎯 IT·AI 커리어 전환 6개월 로드맵 (자동 진행률 + 시각적 Progress Bar 버전)

> ✅ 목표: 6개월 안에 AI 서비스 완성 → 포트폴리오 공개 → 첫 수익 또는 제안 확보  
> 💻 버전: IT/AI 실무형 (LangChain + FastAPI + React)
> 📊 자동 진행률 계산 + 시각적 Progress Bar 포함

---

## 🧱 Notion 데이터베이스 구조
| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| 단계 | Select | 1단계~4단계 |
| 주차 | Text | 예: 1주차, 5~6주차 |
| 할 일 | Text | 주차별 핵심 작업 |
| 완료여부 | Checkbox | 체크 시 완료 |
| 결과물 | Text | 목표 산출물 |
| 학습 링크 | URL | 공식 문서, 강의, 예시 코드 링크 |
| 완료일 | Date | 완료 날짜 |
| 진행률 | Formula | 전체 완료율 + 시각적 바 자동 계산 |

---

## 🧮 진행률 Formula (시각적 Progress Bar + % 표시)
> 📋 이 수식을 Formula 필드에 복사하면 자동으로 전체 진행률이 표시됩니다.

```text
"📊 " + slice("████████████████████", 0, round((sum(prop(\"완료여부\")) / 24) * 20)) + 
slice("░░░░░░░░░░░░░░░░░░░░", 0, 20 - round((sum(prop(\"완료여부\")) / 24) * 20)) + 
" " + format(round((sum(prop(\"완료여부\")) / 24) * 100)) + "%"
```

💡 예시 출력:  
📊 ████████░░░░░░░░░░ 40%

---

## 📅 주차별 계획표
| 단계 | 주차 | 할 일 | 결과물 | 학습 링크 |
|------|------|--------|----------|------------|
| 1단계 | 1주차 | Python 3.10+ / FastAPI 환경 세팅 | FastAPI 서버 구축 | https://fastapi.tiangolo.com |
| 1단계 | 2주차 | OpenAI API / LangChain 실습 | 첫 AI 챗봇 구현 | https://python.langchain.com |
| 1단계 | 3주차 | Chroma RAG 임베딩 실습 | 내 문서를 읽는 챗봇 | https://docs.trychroma.com |
| 1단계 | 4주차 | FastAPI + LangChain 통합 / GitHub 업로드 | 구조화된 서버 코드 | https://github.com |
| 2단계 | 5~6주차 | Embedding 데이터 구축 / MySQL 연동 | RAG 파이프라인 완성 | https://python.langchain.com |
| 2단계 | 7~8주차 | LangGraph 기반 Workflow 제작 | Graph Workflow 작동 | https://langchain-ai.github.io/langgraph |
| 2단계 | 9~10주차 | React + FastAPI 연결 / Chat UI 구성 | 웹 MVP 완성 | https://vitejs.dev |
| 3단계 | 11~12주차 | Render / Railway 배포 | 실제 서비스 URL 확보 | https://render.com |
| 3단계 | 13~14주차 | GitHub README / 구조도 작성 | 포트폴리오 완성 | https://mermaid.js.org |
| 3단계 | 15~16주차 | Threads/브런치 글 작성 | 첫 브랜딩 노출 | https://www.threads.net |
| 4단계 | 17~18주차 | 크몽/위시켓 등록 | 첫 수익 or 제안 | https://kmong.com |
| 4단계 | 19~20주차 | AI 개발자 면접 준비 | 면접 제안 확보 | https://www.wanted.co.kr |
| 4단계 | 21~22주차 | 인프런/탈잉 강의 기획 | 강의 승인 or 멘토링 | https://inflearn.com |
| 4단계 | 23~24주차 | 회고문 작성 / AI 컨설턴트 브랜딩 | 커리어 스토리 완성 | https://notion.so |

---

## 🧭 사용법
1️⃣ 이 Markdown을 Notion 새 페이지에 붙여넣으세요.  
2️⃣ 표를 “데이터베이스 테이블로 변환” 선택.  
3️⃣ “완료여부” 체크박스를 주차별로 클릭하면 진행률이 자동 갱신됩니다.  
4️⃣ 상단 Formula 필드에 위의 Progress Bar 수식을 입력하세요.  

---

✅ 하루에 하나씩만 체크해도,  
6개월 뒤엔 “AI 개발자”로 완전히 변해 있을 겁니다.
