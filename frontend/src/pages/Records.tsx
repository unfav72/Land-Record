import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { FileText, Download, Filter, Search as SearchIcon, Trash2 } from 'lucide-react';
import { records as recordsApi, exports } from '../api/endpoints';
import type { LandRecord } from '../types';

export default function Records() {
  const [records, setRecords] = useState<LandRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    fetchRecords();
  }, [statusFilter]);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const data = await recordsApi.list(statusFilter !== 'all' ? { status: statusFilter } : undefined);
      setRecords(data);
    } catch (error) {
      console.error("Failed to fetch records", error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusStyle = (status: string) => {
    switch(status) {
      case 'VERIFIED': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'NEEDS_REVIEW': return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'CONFLICT': return 'bg-rose-100 text-rose-800 border-rose-200';
      case 'REJECTED': return 'bg-slate-100 text-slate-800 border-slate-200';
      default: return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Land Records</h1>
          <p className="text-slate-500 mt-1">Manage and verify digitized land records.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={() => exports.downloadExcel()}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors shadow-sm text-sm font-medium"
          >
            <Download size={16} /> Export to Excel
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col">
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="relative w-full sm:max-w-md">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <SearchIcon size={16} className="text-slate-400" />
            </div>
            <input 
              type="text" 
              placeholder="Search by Owner or Survey No..." 
              className="block w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg leading-5 bg-white placeholder-slate-500 focus:outline-none focus:placeholder-slate-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              // A real implementation would trigger a search API call here
            />
          </div>
          
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter size={16} className="text-slate-400" />
            <select 
              className="block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="NEEDS_REVIEW">Needs Review</option>
              <option value="VERIFIED">Verified</option>
              <option value="CONFLICT">Conflicts</option>
              <option value="REJECTED">Rejected</option>
              <option value="DRAFT">Drafts</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-white">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Record / Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Owner Details</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Land Details</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">AI Confidence</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
                <th scope="col" className="relative px-6 py-3"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>
                  </td>
                </tr>
              ) : records.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-500">
                    No records found matching your criteria.
                  </td>
                </tr>
              ) : records.map((record) => (
                <tr key={record.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded bg-blue-100 flex items-center justify-center">
                        <FileText className="h-5 w-5 text-blue-600" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-slate-900">#{record.id}</div>
                        <div className="text-xs text-slate-500">{format(new Date(record.created_at), 'MMM d, yyyy')}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-slate-900 truncate max-w-[200px]">{record.owner_name || <span className="text-slate-400 italic">Unextracted</span>}</div>
                    <div className="text-xs text-slate-500 truncate max-w-[200px]">{record.father_spouse_name ? `S/o ${record.father_spouse_name}` : ''}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-slate-900">Sy. No: <span className="font-medium">{record.survey_number || '-'}</span></div>
                    <div className="text-xs text-slate-500 truncate max-w-[200px]">{record.village}, {record.district}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            !record.overall_confidence ? 'bg-slate-300' :
                            record.overall_confidence > 0.8 ? 'bg-emerald-500' : 
                            record.overall_confidence > 0.5 ? 'bg-amber-500' : 'bg-rose-500'
                          }`} 
                          style={{ width: `${Math.round((record.overall_confidence || 0) * 100)}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-medium text-slate-600">{Math.round((record.overall_confidence || 0) * 100)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getStatusStyle(record.status)}`}>
                      {record.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-3">
                      {record.status === 'VERIFIED' ? (
                        <>
                          <button 
                            onClick={() => exports.downloadPDF(record.id)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            PDF
                          </button>
                          <Link to={`/records/${record.id}`} className="text-slate-600 hover:text-slate-900">View</Link>
                        </>
                      ) : (
                        <Link 
                          to={`/verify/${record.id}`}
                          className="text-white bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg shadow-sm transition-colors"
                        >
                          Review
                        </Link>
                      )}
                      
                      <button
                        onClick={async () => {
                          if (window.confirm('Are you sure you want to delete this record?')) {
                            try {
                              await recordsApi.delete(record.id);
                              fetchRecords();
                            } catch (e) {
                              alert('Failed to delete record');
                            }
                          }
                        }}
                        className="text-red-500 hover:text-red-700 p-2 hover:bg-red-50 rounded-full transition-colors ml-2"
                        title="Delete Record"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
