import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, AlertCircle, Loader2 } from 'lucide-react';
import { apiClient } from '../api/client';

export default function ManualEntry() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    owner_name: '',
    father_spouse_name: '',
    ownership_type: 'Private',
    survey_number: '',
    sub_survey_number: '',
    khata_number: '',
    khasra_number: '',
    village: '',
    taluk_tehsil: '',
    district: '',
    state: '',
    area: '',
    area_unit: 'Hectares',
    land_type: 'Dry Land',
    land_classification: '',
    registration_number: '',
    registration_date: '',
    mutation_number: '',
    mutation_date: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // We will hit a new manual endpoint
      await apiClient.post('/api/documents/manual', formData);
      navigate(`/records`);
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to submit manual entry.');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all bg-white/50 backdrop-blur-sm shadow-sm";
  const labelClass = "block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2";

  return (
    <div className="p-8 max-w-6xl mx-auto animate-fade-in">
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 tracking-tight">Manual Record Entry</h1>
          <p className="text-slate-500 mt-2">Directly input land record details without AI extraction.</p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-xl flex items-center gap-3">
          <AlertCircle size={20} />
          <p>{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8 glass-panel p-8 rounded-2xl shadow-sm">
        
        {/* Owner Details */}
        <section>
          <h2 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2 mb-6">Owner Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className={labelClass}>Owner Name *</label>
              <input required name="owner_name" value={formData.owner_name} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Father / Spouse Name</label>
              <input name="father_spouse_name" value={formData.father_spouse_name} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Ownership Type</label>
              <select name="ownership_type" value={formData.ownership_type} onChange={handleChange} className={inputClass}>
                <option>Private</option>
                <option>Government</option>
                <option>Trust</option>
              </select>
            </div>
          </div>
        </section>

        {/* Land Details */}
        <section>
          <h2 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2 mb-6">Land Identification</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <label className={labelClass}>Survey Number *</label>
              <input required name="survey_number" value={formData.survey_number} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Sub-Survey Number</label>
              <input name="sub_survey_number" value={formData.sub_survey_number} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Khata Number</label>
              <input name="khata_number" value={formData.khata_number} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Khasra Number</label>
              <input name="khasra_number" value={formData.khasra_number} onChange={handleChange} className={inputClass} />
            </div>
          </div>
        </section>

        {/* Location Details */}
        <section>
          <h2 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2 mb-6">Location</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <label className={labelClass}>Village *</label>
              <input required name="village" value={formData.village} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Taluk / Tehsil *</label>
              <input required name="taluk_tehsil" value={formData.taluk_tehsil} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>District *</label>
              <input required name="district" value={formData.district} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>State *</label>
              <input required name="state" value={formData.state} onChange={handleChange} className={inputClass} />
            </div>
          </div>
        </section>

        {/* Area & Classification */}
        <section>
          <h2 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2 mb-6">Area & Classification</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <label className={labelClass}>Area Value *</label>
              <input required type="number" step="0.01" name="area" value={formData.area} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Area Unit</label>
              <select name="area_unit" value={formData.area_unit} onChange={handleChange} className={inputClass}>
                <option>Hectares</option>
                <option>Acres</option>
                <option>Square Meters</option>
                <option>Square Feet</option>
                <option>Ares</option>
                <option>Cents</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Land Type</label>
              <select name="land_type" value={formData.land_type} onChange={handleChange} className={inputClass}>
                <option>Dry Land</option>
                <option>Wet Land</option>
                <option>Commercial</option>
                <option>Residential</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Classification</label>
              <input name="land_classification" value={formData.land_classification} onChange={handleChange} className={inputClass} />
            </div>
          </div>
        </section>

        {/* Registration */}
        <section>
          <h2 className="text-lg font-bold text-slate-800 border-b border-slate-200 pb-2 mb-6">Registration & Mutation</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <label className={labelClass}>Registration No.</label>
              <input name="registration_number" value={formData.registration_number} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Registration Date</label>
              <input type="date" name="registration_date" value={formData.registration_date} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Mutation No.</label>
              <input name="mutation_number" value={formData.mutation_number} onChange={handleChange} className={inputClass} />
            </div>
            <div>
              <label className={labelClass}>Mutation Date</label>
              <input type="date" name="mutation_date" value={formData.mutation_date} onChange={handleChange} className={inputClass} />
            </div>
          </div>
        </section>

        <div className="pt-6 flex justify-end">
          <button 
            type="submit" 
            disabled={loading}
            className="flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white rounded-xl font-bold shadow-lg shadow-blue-500/30 transition-all disabled:opacity-70 transform hover:-translate-y-0.5"
          >
            {loading ? <Loader2 className="animate-spin" /> : <Save size={20} />}
            Save Verified Record
          </button>
        </div>

      </form>
    </div>
  );
}
