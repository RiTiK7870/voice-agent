import React, {useEffect, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function App() {
  const inputRef = useRef(null);
  const [file,setFile]=useState(null), [sessionId,setSessionId]=useState("demo-"+Date.now());
  const [loading,setLoading]=useState(false), [stage,setStage]=useState("idle");
  const [transcript,setTranscript]=useState(""), [answer,setAnswer]=useState("");
  const [sources,setSources]=useState([]), [escalated,setEscalated]=useState(false);
  const [audioUrl,setAudioUrl]=useState(""), [error,setError]=useState("");

  useEffect(()=>()=>{if(audioUrl) URL.revokeObjectURL(audioUrl)},[audioUrl]);

  function choose(f){if(!f)return;setFile(f);setError("");setStage("ready");}
  function reset(){
    setFile(null);setTranscript("");setAnswer("");setSources([]);setEscalated(false);
    setError("");setStage("idle");if(audioUrl)URL.revokeObjectURL(audioUrl);setAudioUrl("");
    setSessionId("demo-"+Date.now());if(inputRef.current)inputRef.current.value="";
  }

  async function processVoice(){
    if(!file){setError("Choose a WAV file first.");return;}
    setLoading(true);setError("");setStage("processing");
    try{
      const fd=new FormData();fd.append("file",file);
      const r=await fetch(`${API_BASE}/api/voice-chat?session_id=${encodeURIComponent(sessionId)}`,{method:"POST",body:fd});
      if(!r.ok){let m=`Backend returned HTTP ${r.status}`;try{const b=await r.json();m=b.detail||m}catch{}throw new Error(m)}
      const blob=await r.blob(), url=URL.createObjectURL(blob);
      if(audioUrl)URL.revokeObjectURL(audioUrl);setAudioUrl(url);
      setTranscript(r.headers.get("x-transcript")||"");
      setAnswer(r.headers.get("x-answer")||"");
      setEscalated((r.headers.get("x-escalated")||"").toLowerCase()==="true");
      setSources((r.headers.get("x-sources")||"").split(",").map(x=>x.trim()).filter(Boolean));
      setStage("complete");
    }catch(e){setError(e.message||"Request failed.");setStage("error")}
    finally{setLoading(false)}
  }

  const done = stage==="complete";
  return <div className="shell">
    <header><div className="brand"><div className="logo">✦</div><div><b>Enterprise AI Voice Agent</b><small>Functional POC · Local Environment</small></div></div><div className="backend"><i/> Backend <strong>127.0.0.1:8000</strong></div></header>

    <main>
      <section className="hero">
        <div><label>◆ GROUNDED ENTERPRISE AI</label><h1>Voice in.<br/><span>Knowledge out.</span></h1>
        <p>Demonstrate speech recognition, semantic retrieval, LangGraph orchestration, grounded answers and voice synthesis in one workflow.</p></div>
        <div className="flow">{["STT","RAG","AGENT","TTS"].map((x,i)=><React.Fragment key={x}><div><em>{i+1}</em>{x}</div>{i<3&&<b>→</b>}</React.Fragment>)}</div>
      </section>

      <section className="grid">
        <div className="card">
          <h2>🎙 Customer Voice</h2><p className="sub">Upload a clear WAV recording for the demonstration.</p>
          <div className={`drop ${file?"selected":""}`} onClick={()=>inputRef.current?.click()}
            onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();choose(e.dataTransfer.files?.[0])}}>
            <input ref={inputRef} hidden type="file" accept=".wav,audio/wav" onChange={e=>choose(e.target.files?.[0])}/>
            <div className="upload">⇧</div>
            <b>{file?file.name:"Drop WAV audio here"}</b>
            <span>{file?`${(file.size/1024).toFixed(1)} KB · WAV audio`:"or click to browse"}</span>
          </div>
          <label className="field-label">Demo session</label>
          <input className="text" value={sessionId} onChange={e=>setSessionId(e.target.value)}/>
          <button className="primary" disabled={!file||loading} onClick={processVoice}>{loading?"◌ Processing voice…":"➤ Process Voice"}</button>
          <button className="secondary" onClick={reset}>↻ Reset demonstration</button>
          {error&&<div className="error">⚠ {error}</div>}
        </div>

        <div className="card">
          <h2>⚡ Live Processing</h2><p className="sub">Pipeline status and grounded response.</p>
          <div className="pipeline">{["STT","RAG","AGENT","TTS"].map((x,i)=><React.Fragment key={x}>
            <div className={(done||stage==="processing"&&i<3)?"node done":"node"}><em>{done||stage==="processing"&&i<3?"✓":i+1}</em><b>{x}</b></div>{i<3&&<div className={(done||stage==="processing"&&i<3)?"line done":"line"}/>}
          </React.Fragment>)}</div>
          <hr/>
          <Section title="CUSTOMER TRANSCRIPT" value={transcript||"Waiting for voice input…"} />
          <div className="result"><label>🤖 AGENT RESPONSE</label><div className="answer">{answer||"The grounded response will appear here."}</div></div>
          <div className="metrics">
            <div><small>KNOWLEDGE SOURCE</small><b>{sources.length?sources.join(", "):"—"}</b></div>
            <div className={escalated?"warn":"ok"}><small>RESOLUTION</small><b>{escalated?"Human escalation":answer?"AI answered":"—"}</b></div>
          </div>
          <div className="audio"><div className="sound">🔊</div><div><b>Agent voice response</b><small>{audioUrl?"Generated WAV response":"Waiting for response audio"}</small></div>
            {audioUrl?<audio controls src={audioUrl}/>:<span className="play">▶</span>}</div>
        </div>
      </section>

      <div className="note">🛡 <span><b>POC boundary:</b> local Whisper, FAISS, LangGraph, local answer provider and pyttsx3 are used here. TCS-approved STT/LLM/TTS, Azure hosting, Genesys AudioHook, authentication and human transfer are later production integrations.</span></div>
    </main>
  </div>
}

function Section({title,value}){return <div className="result"><label>▣ {title}</label><div className="value">{value}</div></div>}
createRoot(document.getElementById("root")).render(<React.StrictMode><App/></React.StrictMode>);

