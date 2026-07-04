export type Severity = 'low' | 'medium' | 'high';

export interface Risk {
  risk: string;
  severity: Severity;
  reason: string;
}

export interface BriefDecodeResult {
  summary: string;
  goals: string[];
  deliverables: string[];
  constraints: string[];
  risks: Risk[];
  clarifying_questions: string[];
  recommended_next_action: string;
}

export interface RunRead {
  run_id: number;
  status: 'succeeded' | 'failed';
  result: BriefDecodeResult | null;
  error_code: 'provider_error' | 'validation_error' | null;
  error_message: string | null;
  created_at: string;
}

const BASE_URL = 'http://localhost:8000';

export async function decodeBrief(text: string): Promise<RunRead> {
  const response = await fetch(`${BASE_URL}/v1/briefs/decode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    throw new Error(`Backend responded with ${response.status}`);
  }
  return response.json();
}

