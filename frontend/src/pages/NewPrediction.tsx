import { useState, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ApplicantInfoSection from '../components/ApplicantInfoSection';
import type { ApplicantInfo } from '../components/ApplicantInfoSection';
import FinancialParamsSection from '../components/FinancialParamsSection';
import type { FinancialParams } from '../components/FinancialParamsSection';
import ResultsPanel from '../components/ResultsPanel';
import { evaluateMacroRisk, evaluateFinancialRisk, uploadDocuments, pollDocumentResult } from '../api/client';
import type { MacroRiskResult, FinancialRiskResult, DocumentRiskResult } from '../types';

function NewPrediction() {
  const formRef = useRef<HTMLFormElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  void abortController;

  const [macroResult, setMacroResult] = useState<MacroRiskResult | null>(null);
  const [financialResult, setFinancialResult] = useState<FinancialRiskResult | null>(null);
  const [documentResult, setDocumentResult] = useState<DocumentRiskResult | null>(null);

  const loanAppId = uuidv4();

  const [applicant, setApplicant] = useState<ApplicantInfo>({
    entityName: 'Quantum Horizon Ventures',
    applicationId: loanAppId,
    region: 'North America (NA-01)',
    loanType: 'SME',
    industry: 'Manufacturing',
    employmentSector: 'Private',
  });

  const [financial, setFinancial] = useState<FinancialParams>({
    annualRevenue: '4500000',
    liquidityRatio: '1.84',
    operatingMargin: '0.12',
    roa: '0.08',
    profitMargin: '0.15',
    industryCode: 'manufacturing',
  });

  const handleFileSelect = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFilesChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setUploadedFiles(Array.from(e.target.files));
    }
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setShowResults(true);
    setDocumentResult(null);

    const ctrl = new AbortController();
    setAbortController(ctrl);

    const appId = uuidv4();

    const region = applicant.region.split('(')[1]?.replace(')', '') || applicant.region;

    try {
      const [macroRes, financialRes] = await Promise.all([
        evaluateMacroRisk({
          loan_application_id: appId,
          loan_amount: parseFloat(financial.annualRevenue) || 0,
          loan_type: applicant.loanType,
          industry: applicant.industry,
          location: region,
          employment_sector: applicant.employmentSector,
        }, ctrl.signal),
        evaluateFinancialRisk({
          loan_application_id: appId,
          financial_ratios: {
            liquidity_ratio: parseFloat(financial.liquidityRatio) || 0,
            operating_margin: parseFloat(financial.operatingMargin) || 0,
            roa: parseFloat(financial.roa) || 0,
            profit_margin: parseFloat(financial.profitMargin) || 0,
          },
          industry_code: financial.industryCode,
          loan_amount: parseFloat(financial.annualRevenue) || undefined,
        }, ctrl.signal),
      ]);

      setMacroResult(macroRes);
      setFinancialResult(financialRes);

      if (uploadedFiles.length > 0) {
        try {
          const { task_id } = await uploadDocuments(appId, uploadedFiles, ctrl.signal);
          const docRes = await pollDocumentResult(task_id, 20, 2000, ctrl.signal);
          setDocumentResult(docRes);
        } catch (docErr: unknown) {
          if (docErr instanceof Error && docErr.name !== 'AbortError') {
            console.warn('Document processing issue:', docErr.message);
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        if (err.name === 'AbortError') return;
        setError(err.message);
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
      setAbortController(null);
    }
  }, [applicant, financial, uploadedFiles]);

  return (
    <>
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="flex justify-between items-end animate-entrance">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface mb-1">New Risk Prediction</h2>
            <p className="text-on-surface-variant font-body-md">Initiate automated risk modeling for high-value financial entities.</p>
          </div>
          <div className="flex gap-element-gap-md">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png,.csv"
              onChange={handleFilesChange}
              className="hidden"
            />
            <button
              type="button"
              onClick={handleFileSelect}
              className="px-6 py-2 border border-outline-variant text-on-surface rounded-full font-label-md text-label-md flex items-center gap-2 transition-all duration-300 hover:bg-surface-variant/20 hover:scale-[1.03] hover:shadow-md active:scale-[0.97]"
            >
              <span className="material-symbols-outlined text-[18px]">upload_file</span>
              {uploadedFiles.length > 0 ? `${uploadedFiles.length} file(s)` : 'Upload CSV'}
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => formRef.current?.requestSubmit()}
              className="px-6 py-2 bg-primary text-on-primary-container rounded-full font-label-md text-label-md flex items-center gap-2 shadow-lg shadow-primary/20 disabled:opacity-50 transition-all duration-300 hover:scale-[1.04] hover:shadow-xl hover:shadow-primary/30 active:scale-[0.97]"
            >
              {loading ? (
                <><svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>Processing</>
              ) : (
                <><span className="material-symbols-outlined text-[18px]">bolt</span>Predict Risk</>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-error/10 border border-error/20 rounded-lg p-4 animate-entrance flex items-start gap-3">
            <span className="material-symbols-outlined text-error text-[20px] mt-0.5">error</span>
            <div>
              <p className="text-label-md text-error font-semibold">Prediction failed</p>
              <p className="text-body-sm text-on-surface-variant mt-1">{error}</p>
            </div>
          </div>
        )}

        <form ref={formRef} onSubmit={handleSubmit}>
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-12 lg:col-span-8 space-y-6">
              <ApplicantInfoSection value={applicant} onChange={setApplicant} />
              <FinancialParamsSection value={financial} onChange={setFinancial} />

              <div className="flex justify-end gap-3 animate-entrance delay-5">
                <button type="button" className="px-8 py-2 border border-outline-variant/30 text-on-surface rounded-full font-label-md text-label-md transition-all duration-300 hover:bg-surface-variant/10 hover:scale-[1.03] hover:border-outline-variant/50 active:scale-[0.97]">
                  Save Draft
                </button>
                <button type="button" className="px-8 py-2 bg-secondary text-on-secondary rounded-full font-label-md text-label-md transition-all duration-300 hover:scale-[1.04] hover:shadow-lg hover:shadow-secondary/20 active:scale-[0.97]">
                  Preview Report
                </button>
              </div>
            </div>

            <div className="col-span-12 lg:col-span-4">
              <ResultsPanel
                show={showResults}
                loading={loading}
                macro={macroResult}
                financial={financialResult}
                document={documentResult}
              />
            </div>
          </div>
        </form>
      </div>
    </>
  );
}

export default NewPrediction;
