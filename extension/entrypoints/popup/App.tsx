import { useState } from 'react';
import { decodeBrief, type RunRead, type BriefDecodeResult } from './api';
import './App.css';

type UiState =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'success'; run: RunRead; result: BriefDecodeResult }
  | { kind: 'error'; message: string };

function App() {
  const [text, setText] = useState('');
  const [ui, setUi] = useState<UiState>({ kind: 'idle' });
  const [copied, setCopied] = useState(false);

  async function handleDecode() {
    setUi({ kind: 'loading' });
    setCopied(false);
    try {
      const run = await decodeBrief(text);
      if (run.status === 'succeeded' && run.result) {
        setUi({ kind: 'success', run, result: run.result });
      } else {
        setUi({ kind: 'error', message: run.error_message ?? 'Decode failed' });
      }
    } catch (e) {
      setUi({ kind: 'error', message: e instanceof Error ? e.message : 'Request failed' });
    }
  }

  async function handleCopy() {
    if (ui.kind !== 'success') return;
    await navigator.clipboard.writeText(JSON.stringify(ui.result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="app">
      <h1>AI Brief Decoder</h1>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste a client brief here…"
        rows={6}
      />

      <button
        onClick={handleDecode}
        disabled={ui.kind === 'loading' || text.trim().length === 0}
      >
        {ui.kind === 'loading' ? 'Decoding…' : 'Decode brief'}
      </button>

      {ui.kind === 'error' && <div className="error">{ui.message}</div>}

      {ui.kind === 'success' && (
        <div className="result">
          <div className="result-header">
            <span className="run-id">run #{ui.run.run_id}</span>
            <button className="copy" onClick={handleCopy}>
              {copied ? 'Copied!' : 'Copy JSON'}
            </button>
          </div>

          <section>
            <h2>Summary</h2>
            <p>{ui.result.summary}</p>
          </section>

          <ListSection title="Goals" items={ui.result.goals} />
          <ListSection title="Deliverables" items={ui.result.deliverables} />
          <ListSection title="Constraints" items={ui.result.constraints} />

          <section>
            <h2>Risks</h2>
            <ul className="risks">
              {ui.result.risks.map((risk, i) => (
                <li key={i}>
                  <span className={`severity ${risk.severity}`}>{risk.severity}</span>
                  <div>
                    <strong>{risk.risk}</strong>
                    <p>{risk.reason}</p>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <ListSection title="Clarifying questions" items={ui.result.clarifying_questions} />

          <section>
            <h2>Next action</h2>
            <p>{ui.result.recommended_next_action}</p>
          </section>
        </div>
      )}
    </div>
  );
}

function ListSection({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <section>
      <h2>{title}</h2>
      <ul>
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export default App;
