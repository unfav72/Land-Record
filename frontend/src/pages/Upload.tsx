import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, File, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { documents } from '../api/endpoints';
import type { Document as DocType } from '../types';

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState('auto');
  const [uploading, setUploading] = useState(false);
  const [uploadedDoc, setUploadedDoc] = useState<DocType | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [jobs, setJobs] = useState<any[]>([]);
  const [error, setError] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
      setUploadedDoc(null);
      setJobs([]);
      setProcessingStatus('');
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
      setUploadedDoc(null);
    }
  };

  const handleSubmit = async () => {
    if (!file) return;
    
    setUploading(true);
    setError('');
    
    try {
      const typeParam = docType === 'auto' ? undefined : docType;
      const doc = await documents.upload(file, typeParam);
      setUploadedDoc(doc);
      setProcessingStatus(doc.status);
    } catch (err: any) {
      let errMsg = 'Upload failed';
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errMsg = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errMsg = err.response.data.detail.map((e: any) => e.msg).join(', ');
        }
      }
      setError(errMsg);
    } finally {
      setUploading(false);
    }
  };

  // Poll for job status if uploaded
  useEffect(() => {
    let interval: number;
    
    if (uploadedDoc && !['COMPLETED', 'FAILED'].includes(processingStatus)) {
      interval = window.setInterval(async () => {
        try {
          const doc = await documents.getById(uploadedDoc.id);
          const currentJobs = await documents.getJobs(uploadedDoc.id);
          
          setProcessingStatus(doc.status || '');
          setJobs(currentJobs || []);
          
          if (['COMPLETED', 'FAILED'].includes(doc.status)) {
            clearInterval(interval);
          }
        } catch (e) {
          console.error("Polling error", e);
        }
      }, 2000);
    }
    
    return () => clearInterval(interval);
  }, [uploadedDoc, processingStatus]);

  const stages = ['PREPROCESSING', 'OCR', 'CLASSIFICATION', 'EXTRACTION', 'VALIDATION'];

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Digitize New Record</h1>
        <p className="text-slate-500 mt-1">Upload scanned land records for AI-powered data extraction.</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <div className="flex flex-col sm:flex-row gap-6">
            
            {/* Upload Area */}
            <div className="flex-1">
              {!file ? (
                <div 
                  className="border-2 border-dashed border-slate-300 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer group flex flex-col items-center justify-center p-12 text-center h-64"
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleDrop}
                >
                  <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <UploadIcon size={32} />
                  </div>
                  <p className="text-slate-700 font-medium text-lg">Click or drag file to upload</p>
                  <p className="text-slate-500 text-sm mt-2">Supports PDF, JPG, PNG, TIFF (Max 20MB)</p>
                </div>
              ) : (
                <div className="border border-slate-200 rounded-xl p-6 h-64 flex flex-col items-center justify-center relative bg-slate-50">
                  <button 
                    onClick={() => { setFile(null); setUploadedDoc(null); }}
                    className="absolute top-4 right-4 p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-full transition-colors"
                    disabled={uploading || uploadedDoc !== null}
                  >
                    <X size={20} />
                  </button>
                  <File className="w-16 h-16 text-blue-500 mb-4" />
                  <p className="text-slate-900 font-medium truncate max-w-[250px]">{file.name}</p>
                  <p className="text-slate-500 text-sm mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
              )}
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif"
                onChange={handleFileChange}
              />
            </div>

            {/* Config Area */}
            <div className="w-full sm:w-64 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Document Type</label>
                <select 
                  className="w-full rounded-lg border border-slate-300 py-2.5 px-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  disabled={uploading || uploadedDoc !== null}
                >
                  <option value="auto">Auto-Detect (AI)</option>
                  <option value="Land Record">Land Record / Patta</option>
                  <option value="Mutation Record">Mutation Record</option>
                  <option value="Registration Record">Registration Deed</option>
                </select>
              </div>

              {error && (
                <div className="p-3 bg-rose-50 text-rose-700 text-sm rounded-lg border border-rose-100 flex items-start gap-2">
                  <AlertCircle size={16} className="shrink-0 mt-0.5" />
                  {error}
                </div>
              )}

              <button
                onClick={handleSubmit}
                disabled={!file || uploading || uploadedDoc !== null}
                className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white text-sm font-semibold rounded-lg shadow-sm transition-colors"
              >
                {uploading ? <Loader2 size={18} className="animate-spin" /> : <UploadIcon size={18} />}
                {uploading ? 'Uploading...' : 'Start Digitization'}
              </button>
            </div>
          </div>
        </div>

        {/* Processing Tracker */}
        {uploadedDoc && (
          <div className="p-6 bg-slate-50">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-6">AI Processing Pipeline</h3>
            
            <div className="space-y-6">
              {(stages || []).map((stage, index) => {
                const job = (jobs || []).find(j => j?.stage === stage);
                let status = 'pending';
                if (job && job.status) {
                  status = job.status.toLowerCase(); // running, completed, failed
                } else if (['COMPLETED', 'FAILED'].includes(processingStatus)) {
                  // If pipeline is done but job isn't here, it was skipped or failed before
                  status = processingStatus === 'COMPLETED' ? 'completed' : 'pending';
                }

                return (
                  <div key={stage} className="flex items-start gap-4">
                    <div className="flex flex-col items-center mt-1">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 border-2 
                        ${status === 'completed' ? 'bg-emerald-500 border-emerald-500 text-white' : 
                          status === 'running' ? 'border-blue-500 text-blue-600 bg-blue-50' : 
                          status === 'failed' ? 'bg-rose-500 border-rose-500 text-white' :
                          'border-slate-300 bg-white text-slate-300'}`}
                      >
                        {status === 'completed' ? <CheckCircle size={14} /> : 
                         status === 'running' ? <Loader2 size={14} className="animate-spin" /> : 
                         status === 'failed' ? <X size={14} /> : 
                         <span className="text-xs font-bold">{index + 1}</span>}
                      </div>
                      {index < stages.length - 1 && (
                        <div className={`w-0.5 h-10 mt-2 ${
                          ['completed', 'running'].includes(status) ? 'bg-blue-200' : 'bg-slate-200'
                        }`}></div>
                      )}
                    </div>
                    <div>
                      <h4 className={`text-sm font-semibold ${
                        status === 'completed' ? 'text-slate-900' : 
                        status === 'running' ? 'text-blue-700' : 
                        status === 'failed' ? 'text-rose-700' : 'text-slate-400'
                      }`}>
                        {stage.replace('_', ' ')}
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">
                        {status === 'running' && 'Processing...'}
                        {status === 'completed' && job?.result_data && (
                          <span className="text-emerald-600 text-xs truncate max-w-md block">
                            Success
                          </span>
                        )}
                        {status === 'failed' && <span className="text-rose-600">{job?.error_message || 'Failed'}</span>}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {processingStatus === 'COMPLETED' && (
              <div className="mt-8 p-4 bg-emerald-50 rounded-lg border border-emerald-200 flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-emerald-800">Processing Complete!</h4>
                  <p className="text-sm text-emerald-600">The AI has extracted all fields successfully.</p>
                </div>
                <button 
                  onClick={() => navigate('/records')} // We would navigate to /verify/:id but we need the record ID. For now just go to records.
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg shadow-sm"
                >
                  View Extracted Record
                </button>
              </div>
            )}
            
            {processingStatus === 'FAILED' && (
              <div className="mt-8 p-4 bg-rose-50 rounded-lg border border-rose-200">
                <h4 className="font-semibold text-rose-800">Processing Failed</h4>
                <p className="text-sm text-rose-600 mt-1">{uploadedDoc?.error_message}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
