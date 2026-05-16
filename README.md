# Super RAG - Cognitive Operating System

🚀 **نظام RAG المعرفي المتطور** - نظام تشغيل معرفي بذاكرة هجينة 5 طبقات

## 📋 نظرة عامة

Super RAG هو نظام RAG إنتاجي متكامل مصمم للعمل على موارد محدودة (8GB RAM, 2 Cores, 100GB SSD) مع تحقيق أقصى أداء ممكن.

### المميزات الرئيسية

- **Hybrid Memory Intelligence**: 5 طبقات ذاكرة تعمل بتناغم كامل
  - WorkingMemory (Redis) - الذاكرة العاملة
  - SemanticMemory (Milvus) - الذاكرة الدلالية مع RaBitQ optimization
  - KnowledgeGraph (Neo4j) - شبكة المعرفة
  - EpisodicMemory (PostgreSQL + pgvector) - الذاكرة العرضية
  - IntuitiveMemory (RedisAI) - الذاكرة الغريزية

- **Autonomous Deep Research**: بحث ذاتي عميق مع اتخاذ قرارات ذكية
- **Adaptive Resource Management**: إدارة ذكية للموارد المحدودة
- **Production-Grade Performance**: أداء إنتاجي مع تعقيد أدنى

## 🏗️ المعمارية التقنية

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (React 18+)                   │
│              Chat Interface + Control Panel             │
└────────────────────┬────────────────────────────────────┘
                     │ WebSocket/REST API
┌────────────────────▼────────────────────────────────────┐
│              Backend (FastAPI + Python)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │        Cognitive Orchestration Engine            │  │
│  │  - Query Classifier                              │  │
│  │  - Parallel Memory Router                        │  │
│  │  - Result Fusion Engine                          │  │
│  │  - Semantic Cache                                │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Hybrid Search Engine                     │  │
│  │  - Keyword Search (BM25)                         │  │
│  │  - Vector Search (Semantic)                      │  │
│  │  - Graph Search (Relational)                     │  │
│  │  - Re-Ranking                                    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────┬──────────────┬──────────────┬────────────────┘
          │              │              │
    ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
    │   Redis   │ │  Milvus   │ │ PostgreSQL│
    │ Working   │ │ Semantic  │ │ Episodic  │
    │  Memory   │ │  Memory   │ │  Memory   │
    └───────────┘ └───────────┘ └───────────┘
```

## 🚀 البدء السريع

### المتطلبات المسبقة

- Docker & Docker Compose
- 8GB RAM كحد أدنى
- 100GB مساحة تخزين
- OpenRouter API Key (اختياري)

### التثبيت

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd super-rag
```

2. **إعداد المتغيرات البيئية**
```bash
cp backend/.env.example backend/.env
# عدل ملف .env وأضف مفاتيح API الخاصة بك
```

3. **تشغيل النظام**
```bash
docker-compose up -d
```

4. **الوصول للواجهة**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 الأداء المستهدف

| المقياس | الهدف |
|---------|-------|
| Latency (ذاكرة فقط) | < 200ms |
| Latency (بحث ويب) | 2-5s |
| Cache Hit Rate | > 70% |
| Concurrent Users | 50+ |
| Memory Usage | < 7GB |

## 🔧 التكوين

### تحسين الذاكرة

تم تكوين جميع طبقات الذاكرة للعمل بكفاءة على 8GB RAM:

- **Redis**: 1GB كحد أقصى
- **Milvus**: 2GB مع RaBitQ quantization (توفير 72%)
- **PostgreSQL**: 1GB
- **Neo4j**: 1GB
- **Backend**: 2GB
- **Frontend**: 512MB

### نموذج Embedding

النظام مُعد لاستخدام Qwen3-Embedding-8B (أفضل نموذج RAG 2026)

### توجيه النماذج

يستخدم النظام استراتيجية Tiered Routing لتوفير 70-85% من التكلفة:

1. **Tier 1** (بسيط): google/gemini-2.0-flash-lite - $0.075/M tokens
2. **Tier 2** (معقد): google/gemini-2.5-flash - $0.30/M tokens
3. **Tier 3** (ممتاز): anthropic/claude-sonnet-4.5 - $3/M input

## 📡 API Endpoints

### Chat
```bash
POST /api/v1/chat
{
  "query": "سؤالك هنا",
  "session_id": "optional-id",
  "depth": "shallow|deep"
}
```

### System Status
```bash
GET /api/v1/status
```

### Memory Stats
```bash
GET /api/v1/memory/stats
```

### n8n Webhook
```bash
POST /api/v1/webhook/n8n/query
{
  "query": "...",
  "context": {}
}
```

## 🛠️ التطوير

### تشغيل في وضع التطوير

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📈 المراقبة

### Prometheus Metrics
```bash
GET /metrics
```

### Health Check
```bash
GET /api/v1/health
```

## 🔐 الأمان

- Rate Limiting: 100 requests/user/hour
- Circuit Breaker Pattern للخدمات الخارجية
- Fallback Strategies متعددة المستويات

## 📝 الترخيص

MIT License

## 🤝 المساهمة

المساهمات مرحب بها! يرجى قراءة إرشادات المساهمة قبل البدء.

---

**ملاحظة**: هذا النظام لا يزال قيد التطوير النشط. بعض الميزات قد تكون غير مكتملة.
