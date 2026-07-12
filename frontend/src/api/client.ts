import type { MacroRiskRequest, MacroRiskResult, FinancialRiskRequest, FinancialRiskResult, DocumentRiskResponse, DocumentRiskResult } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function authHeaders(): Record<string, string> {
  return { 'Authorization': 'Bearer risk_engineer_token' };
}

export async function evaluateMacroRisk(data: MacroRiskRequest, signal?: AbortSignal): Promise<MacroRiskResult> {
  const res = await fetch(`${API_BASE}/api/macro-risk/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
    signal,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(detail.detail || `Macro risk failed: ${res.status}`);
  }
  return res.json();
}

export async function evaluateFinancialRisk(data: FinancialRiskRequest, signal?: AbortSignal): Promise<FinancialRiskResult> {
  const res = await fetch(`${API_BASE}/api/financial-risk/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(data),
    signal,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(detail.detail || `Financial risk failed: ${res.status}`);
  }
  return res.json();
}

export async function uploadDocuments(loanApplicationId: string, files: File[], signal?: AbortSignal): Promise<DocumentRiskResponse> {
  const form = new FormData();
  files.forEach(f => form.append('documents', f));
  const url = `${API_BASE}/api/document-risk/?loan_application_id=${loanApplicationId}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: authHeaders(),
    body: form,
    signal,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(detail.detail || `Document upload failed: ${res.status}`);
  }
  return res.json();
}

export async function pollDocumentResult(taskId: string, maxRetries = 20, interval = 2000, signal?: AbortSignal): Promise<DocumentRiskResult> {
  for (let i = 0; i < maxRetries; i++) {
    const res = await fetch(`${API_BASE}/api/document-risk/${taskId}`, {
      headers: authHeaders(),
      signal,
    });
    if (res.status === 202) {
      await new Promise(r => setTimeout(r, interval));
      continue;
    }
    if (!res.ok) {
      const detail = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(detail.detail || `Poll failed: ${res.status}`);
    }
    return res.json();
  }
  throw new Error('Document processing timed out');
}
