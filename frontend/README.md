# Enterprise AI Voice Agent React UI

## Run
```powershell
npm install
npm run dev
```

Open the Vite URL, usually `http://localhost:5173`.

The UI calls:
`POST http://127.0.0.1:8000/api/voice-chat?session_id=<id>`

It sends the selected WAV as multipart field `file` and reads the returned:
`audio/wav`, `X-Transcript`, `X-Answer`, `X-Sources`, `X-Escalated`, `X-Session-ID`.

If the browser reports CORS, add the middleware shown below to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID", "X-Transcript", "X-Answer", "X-Escalated", "X-Sources"],
)
```

