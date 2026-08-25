import { useState, useEffect } from 'react';
import { Shield, ShieldAlert, UserPlus, Users as UsersIcon, Check, X, Loader2 } from 'lucide-react';
import { apiClient } from '../api/client';
import type { User } from '../types';

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Add User Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [addingUser, setAddingUser] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    role: 'officer'
  });
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await apiClient.get<User[]>('/api/users/');
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to fetch users', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingUser(true);
    setError('');
    
    try {
      await apiClient.post('/api/users/', formData);
      setShowAddForm(false);
      setFormData({ username: '', email: '', full_name: '', password: '', role: 'officer' });
      fetchUsers(); // Refresh list
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setAddingUser(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">User Management</h1>
          <p className="text-slate-500 mt-1">Manage system administrators and verification officers.</p>
        </div>
        
        <button 
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm text-sm font-medium"
        >
          {showAddForm ? <X size={16} /> : <UserPlus size={16} />}
          {showAddForm ? 'Cancel' : 'Add New User'}
        </button>
      </div>

      {showAddForm && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Create New Account</h2>
          <form onSubmit={handleAddUser} className="space-y-4 max-w-2xl">
            {error && <div className="p-3 bg-rose-50 text-rose-700 text-sm rounded-lg">{error}</div>}
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                <input 
                  type="text" required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-1 focus:ring-blue-500"
                  value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                <input 
                  type="email" required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-1 focus:ring-blue-500"
                  value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
                <input 
                  type="text" required
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-1 focus:ring-blue-500"
                  value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                <input 
                  type="password" required minLength={8}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-1 focus:ring-blue-500"
                  value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})}
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-1">Role</label>
                <select 
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-1 focus:ring-blue-500"
                  value={formData.role} onChange={e => setFormData({...formData, role: e.target.value})}
                >
                  <option value="officer">Verification Officer (Can review and approve records)</option>
                  <option value="admin">System Administrator (Full access)</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-end pt-4">
              <button 
                type="submit" 
                disabled={addingUser}
                className="flex items-center gap-2 px-6 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 disabled:opacity-50 transition-colors"
              >
                {addingUser ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
                Create Account
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">User</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Contact</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Role</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
                  </td>
                </tr>
              ) : users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 font-bold text-lg">
                        {u.full_name.charAt(0)}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-slate-900">{u.full_name}</div>
                        <div className="text-xs text-slate-500">ID: {u.username}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-slate-600">{u.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                      u.role === 'admin' ? 'bg-purple-50 text-purple-700 border-purple-200' : 'bg-blue-50 text-blue-700 border-blue-200'
                    }`}>
                      {u.role === 'admin' ? <ShieldAlert size={12} /> : <Shield size={12} />}
                      {u.role === 'admin' ? 'Administrator' : 'Officer'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                      u.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-800'
                    }`}>
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
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
