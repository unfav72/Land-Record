import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { X, AlertTriangle, Image as ImageIcon, Save, CheckCircle, Edit3, Loader2 } from 'lucide-react';
import { records as recordsApi } from '../api/endpoints';
import { apiClient } from '../api/client';
import type { LandRecord, Document as DocType, ValidationResult } from '../types';

export default function Verification() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [record, setRecord] = useState<LandRecord | null>(null);
  const [document, setDocument] = useState<DocType | null>(null);
  const [validations, setValidations] = useState<ValidationResult[]>([]);
  const [imageBlobUrl, setImageBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Field editing state
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [editReason, setEditReason] = useState('');
  const [savingField, setSavingField] = useState(false);
  
  // Action state
  const [actioning, setActioning] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectInput, setShowRejectInput] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  useEffect(() => {
    return () => {
      if (imageBlobUrl) {
        URL.revokeObjectURL(imageBlobUrl);
      }
    };
  }, [imageBlobUrl]);

  const fetchData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const rec = await recordsApi.getById(parseInt(id));
      setRecord(rec);
      
      const [docData, valData] = await Promise.all([
        apiClient.get(`/api/documents/${rec.document_id}`).then((res: any) => res.data),
        recordsApi.getValidation(parseInt(id))
      ]);
      setDocument(docData);
      setValidations(valData);
      
      try {
        const imageRes = await apiClient.get(`/api/export/document/${rec.document_id}/original`, { responseType: 'blob' });
        const objectUrl = URL.createObjectURL(imageRes.data);
        setImageBlobUrl(objectUrl);
      } catch (imgError) {
        console.error("Failed to fetch document image", imgError);
      }
    } catch (error) {
      console.error("Failed to fetch verification data", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveField = async (fieldName: string) => {
    if (!id || !record) return;
    setSavingField(true);
    try {
      await recordsApi.correctField(parseInt(id), {
        field_name: fieldName,
        officer_value: editValue,
        reason: editReason
      });
      // Update local state
      setRecord({ ...record, [fieldName]: editValue });
      setEditingField(null);
    } catch (error) {
      console.error("Failed to save field", error);
      alert("Failed to update field");
    } finally {
      setSavingField(false);
    }
  };

  const handleAction = async (action: 'approve' | 'reject') => {
    if (!id) return;
    
    if (action === 'reject' && !rejectReason && !showRejectInput) {
      setShowRejectInput(true);
      return;
    }
    
    if (action === 'reject' && !rejectReason) {
      alert("Please provide a rejection reason.");
      return;
    }

    setActioning(true);
    try {
      await recordsApi.action(parseInt(id), action, rejectReason);
      navigate('/records');
    } catch (error) {
      console.error(`Failed to ${action} record`, error);
      alert(`Failed to ${action} record`);
    } finally {
      setActioning(false);
    }
  };

  if (loading || !record) {
    return <div className="flex h-screen items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-blue-600" /></div>;
  }

  // Parse confidences
  let confidences: Record<string, number> = {};
  try {
    if (record.field_confidences) confidences = JSON.parse(record.field_confidences);
  } catch(e) {}

  const renderFieldRow = (label: string, fieldName: keyof LandRecord, width = "full") => {
    const value = record[fieldName] as string;
    const isEditing = editingField === fieldName;
    const conf = confidences[fieldName as string];
    
    // Check if this field has a validation issue
    const issue = validations.find(v => v.field_name === fieldName);

    return (
      <div className={`p-4 ${width === 'half' ? 'col-span-1' : 'col-span-1 md:col-span-2'} border border-slate-200 rounded-lg bg-white relative group`}>
        <div className="flex justify-between items-start mb-1">
          <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</label>
          
          {conf !== undefined && !isEditing && (
            <div className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
              conf > 0.8 ? 'bg-emerald-100 text-emerald-700' : 
              conf > 0.5 ? 'bg-amber-100 text-amber-700' : 'bg-rose-100 text-rose-700'
            }`}>
              {Math.round(conf * 100)}% conf
            </div>
          )}
        </div>
        
        {isEditing ? (
          <div className="space-y-3 mt-2">
            <input 
              type="text" 
              className="w-full px-3 py-2 border border-blue-500 rounded-md focus:ring-1 focus:ring-blue-500 outline-none"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              autoFocus
            />
            <input 
              type="text" 
              className="w-full px-3 py-2 text-sm border border-slate-300 rounded-md focus:ring-1 focus:ring-slate-500 outline-none"
              placeholder="Reason for change (optional)"
              value={editReason}
              onChange={(e) => setEditReason(e.target.value)}
            />
            <div className="flex gap-2 justify-end">
              <button 
                onClick={() => setEditingField(null)}
                className="px-3 py-1.5 text-sm text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors"
                disabled={savingField}
              >
                Cancel
              </button>
              <button 
                onClick={() => handleSaveField(fieldName as string)}
                className="px-3 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors flex items-center gap-1"
                disabled={savingField}
              >
                {savingField ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />} Save
              </button>
            </div>
          </div>
        ) : (
          <div className="flex justify-between items-center mt-1">
            <div className="text-slate-900 font-medium break-words pr-8">
              {value || <span className="text-slate-400 italic">Not extracted</span>}
            </div>
            {record.status !== 'VERIFIED' && (
              <button 
                onClick={() => {
                  setEditingField(fieldName as string);
                  setEditValue(value || '');
                  setEditReason('');
                }}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full opacity-0 group-hover:opacity-100 transition-all"
                title="Edit Field"
              >
                <Edit3 size={16} />
              </button>
            )}
          </div>
        )}

        {issue && !isEditing && (
          <div className="mt-2 text-xs flex items-start gap-1 text-amber-700 bg-amber-50 p-2 rounded border border-amber-100">
            <AlertTriangle size={14} className="shrink-0 mt-0.5" />
            <span>{issue.message}</span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-full flex-col md:flex-row overflow-hidden">
      
      {/* Document Viewer Pane (Left) */}
      <div className="w-full md:w-5/12 bg-slate-900 border-r border-slate-800 flex flex-col relative shrink-0">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900 text-white shrink-0">
          <div className="flex items-center gap-2">
            <ImageIcon size={18} className="text-slate-400" />
            <h2 className="font-medium text-sm">Original Document</h2>
          </div>
          <span className="text-xs text-slate-500 bg-slate-800 px-2 py-1 rounded">
            ID: {document?.id} • {document?.document_type}
          </span>
        </div>
        
        <div className="flex-1 overflow-auto bg-slate-800 flex items-center justify-center p-4">
          {imageBlobUrl ? (
            <img 
              src={imageBlobUrl} 
              alt="Original Document" 
              className="max-w-full h-auto shadow-2xl rounded"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.onerror = null;
                // Fallback rendering
                target.src = 'https://via.placeholder.com/800x1200?text=Document+Preview+Not+Available';
              }}
            />
          ) : (
            <Loader2 className="w-8 h-8 animate-spin text-slate-600" />
          )}
        </div>
      </div>

      {/* Verification Pane (Right) */}
      <div className="flex-1 flex flex-col bg-slate-50 overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-white flex justify-between items-center shrink-0 shadow-sm z-10">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Record Verification</h1>
            <p className="text-sm text-slate-500">Review AI extracted data and approve to generate official digital record.</p>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`px-3 py-1 text-sm font-semibold rounded-full border ${
              record.overall_confidence && record.overall_confidence > 0.8 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'
            }`}>
              AI Confidence: {Math.round((record.overall_confidence || 0) * 100)}%
            </div>
          </div>
        </div>

        {/* Global Warnings */}
        {validations.filter(v => !v.field_name).length > 0 && (
          <div className="px-6 mt-4 shrink-0">
            {validations.filter(v => !v.field_name).map((v, i) => (
              <div key={i} className={`p-4 rounded-lg flex items-start gap-3 border ${
                v.severity === 'ERROR' ? 'bg-rose-50 border-rose-200 text-rose-800' : 'bg-amber-50 border-amber-200 text-amber-800'
              }`}>
                <AlertTriangle className="shrink-0 mt-0.5" size={20} />
                <div>
                  <h4 className="font-bold text-sm">{v.rule_name}</h4>
                  <p className="text-sm mt-1">{v.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Form Fields */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-8">
            
            {/* Section 1 */}
            <section>
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b pb-2">Owner Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderFieldRow('Owner Name', 'owner_name', 'half')}
                {renderFieldRow('Father / Spouse Name', 'father_spouse_name', 'half')}
                {renderFieldRow('Ownership Type', 'ownership_type', 'half')}
              </div>
            </section>

            {/* Section 2 */}
            <section>
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b pb-2">Land Identification & Location</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderFieldRow('Survey Number', 'survey_number', 'half')}
                {renderFieldRow('Sub-Survey Number', 'sub_survey_number', 'half')}
                {renderFieldRow('Khata Number', 'khata_number', 'half')}
                {renderFieldRow('Khasra Number', 'khasra_number', 'half')}
                {renderFieldRow('Village', 'village', 'half')}
                {renderFieldRow('Taluk / Tehsil', 'taluk_tehsil', 'half')}
                {renderFieldRow('District', 'district', 'half')}
                {renderFieldRow('State', 'state', 'half')}
              </div>
            </section>

            {/* Section 3 */}
            <section>
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b pb-2">Area & Classification</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderFieldRow('Area Value', 'area', 'half')}
                {renderFieldRow('Area Unit', 'area_unit', 'half')}
                {renderFieldRow('Land Type (e.g. Punja/Nanja)', 'land_type', 'half')}
                {renderFieldRow('Classification', 'land_classification', 'half')}
              </div>
            </section>
            
            {/* Section 4 */}
            <section>
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 border-b pb-2">Registration & Mutation (If Applicable)</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderFieldRow('Registration Number', 'registration_number', 'half')}
                {renderFieldRow('Registration Date', 'registration_date', 'half')}
                {renderFieldRow('Mutation Number', 'mutation_number', 'half')}
                {renderFieldRow('Mutation Date', 'mutation_date', 'half')}
              </div>
            </section>
            
          </div>
        </div>

        {/* Action Footer */}
        {record.status !== 'VERIFIED' && (
          <div className="p-4 bg-white border-t border-slate-200 shrink-0 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
            <div className="max-w-4xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
              
              <div className="w-full sm:w-auto">
                {showRejectInput ? (
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      placeholder="Reason for rejection..." 
                      className="px-3 py-2 border border-slate-300 rounded-lg w-full sm:w-64 text-sm outline-none focus:ring-1 focus:ring-rose-500"
                      value={rejectReason}
                      onChange={(e) => setRejectReason(e.target.value)}
                    />
                    <button 
                      onClick={() => handleAction('reject')}
                      className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium transition-colors"
                      disabled={actioning || !rejectReason}
                    >
                      Confirm Reject
                    </button>
                    <button 
                      onClick={() => setShowRejectInput(false)}
                      className="p-2 text-slate-400 hover:text-slate-600 bg-slate-100 rounded-lg"
                    >
                      <X size={18} />
                    </button>
                  </div>
                ) : (
                  <button 
                    onClick={() => setShowRejectInput(true)}
                    className="w-full sm:w-auto px-6 py-2.5 bg-white border-2 border-rose-200 text-rose-600 hover:bg-rose-50 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors"
                    disabled={actioning}
                  >
                    <X size={18} /> Reject Record
                  </button>
                )}
              </div>

              <div className="w-full sm:w-auto flex gap-3">
                <button 
                  onClick={() => handleAction('approve')}
                  className="w-full sm:w-auto px-8 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors shadow-sm"
                  disabled={actioning || showRejectInput}
                >
                  {actioning ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle size={18} />}
                  Approve & Generate Verified PDF
                </button>
              </div>
            </div>
            <p className="text-center text-xs text-slate-500 mt-3">
              By approving, you legally verify that the extracted data matches the original document perfectly.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
