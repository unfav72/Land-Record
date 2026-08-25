import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Files, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  Activity,
  FileText
} from 'lucide-react';
import { dashboard, records } from '../api/endpoints';
import type { DashboardStats, LandRecord } from '../types';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentRecords, setRecentRecords] = useState<LandRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsData, recordsData] = await Promise.all([
          dashboard.getStats(),
          records.list({ limit: 5 })
        ]);
        setStats(statsData);
        setRecentRecords(recordsData);
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const statCards = [
    { name: 'Total Documents', value: stats?.total_documents || 0, icon: Files, color: 'text-blue-600', bg: 'bg-blue-100' },
    { name: 'Needs Review', value: stats?.needs_review || 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
    { name: 'Verified Records', value: stats?.verified || 0, icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-100' },
    { name: 'Conflicts / Errors', value: stats?.conflicts || 0, icon: AlertTriangle, color: 'text-rose-600', bg: 'bg-rose-100' },
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Overview</h1>
        <p className="text-slate-500 mt-1">Real-time statistics of digitized land records.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.name} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center gap-4 transition-all hover:shadow-md">
              <div className={`p-4 rounded-xl ${card.bg}`}>
                <Icon className={`w-6 h-6 ${card.color}`} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">{card.name}</p>
                <p className="text-2xl font-bold text-slate-900">{card.value}</p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">Recent Records</h2>
              <Link to="/records" className="text-sm font-medium text-blue-600 hover:text-blue-700">View All</Link>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Record ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Owner</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Survey No</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {recentRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                        #{record.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {record.owner_name || <span className="text-slate-400 italic">Unknown</span>}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                        {record.survey_number || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                          ${record.status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-800' : 
                            record.status === 'NEEDS_REVIEW' ? 'bg-amber-100 text-amber-800' :
                            record.status === 'CONFLICT' ? 'bg-rose-100 text-rose-800' :
                            'bg-slate-100 text-slate-800'
                          }
                        `}>
                          {record.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Link 
                          to={`/verify/${record.id}`}
                          className="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-md transition-colors"
                        >
                          Review
                        </Link>
                      </td>
                    </tr>
                  ))}
                  {recentRecords.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-8 text-center text-sm text-slate-500">
                        No records found. Upload a document to get started.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-500" /> System Health
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-600 font-medium">AI Extraction Confidence</span>
                  <span className="text-slate-900 font-bold">{Math.round((stats?.avg_confidence || 0) * 100)}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${Math.round((stats?.avg_confidence || 0) * 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-500" /> Document Types
            </h2>
            <div className="space-y-3">
              {stats?.document_types && Object.entries(stats.document_types).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">{type}</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                    {count}
                  </span>
                </div>
              ))}
              {(!stats?.document_types || Object.keys(stats.document_types).length === 0) && (
                <p className="text-sm text-slate-500 italic">No documents processed yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
