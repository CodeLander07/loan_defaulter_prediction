export interface MacroRiskRequest {
  loan_application_id: string;
  loan_amount: number;
  loan_type: string;
  industry: string;
  location: string;
  employment_sector: string;
}

export interface MacroRiskResult {
  loan_application_id: string;
  macro_risk_score: number;
  risk_category: string;
  confidence: number;
  contributing_factors: Record<string, number>;
  explainable_summary: string;
}

export interface FinancialRiskRequest {
  loan_application_id: string;
  financial_ratios: Record<string, number>;
  industry_code: string;
  loan_amount?: number;
}

export interface FinancialRiskResult {
  loan_application_id: string;
  financial_risk_score: number;
  industry_risk_score: number;
  combined_score: number;
  risk_tier: string;
  matched_features: string[];
  features_provided: number;
}

export interface DocumentRiskResponse {
  task_id: string;
}

export interface DocumentRiskResult {
  task_id: string;
  score: number;
  risk_category: string;
  confidence: number;
  fraud_probability: number;
  detected_issues: string[];
  recommendation: string;
  explainable_summary: string;
}

export interface PredictionResults {
  macro: MacroRiskResult | null;
  financial: FinancialRiskResult | null;
  document: DocumentRiskResult | null;
  macroError?: string;
  financialError?: string;
  documentError?: string;
}
