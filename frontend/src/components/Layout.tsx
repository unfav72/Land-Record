import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Upload as UploadIcon, 
  Search, 
  Files, 
  Users, 
  LogOut
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.png';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Upload Document', path: '/upload', icon: UploadIcon },
    { name: 'Manual Entry', path: '/manual-entry', icon: Files },
    { name: 'Search Records', path: '/search', icon: Search },
    { name: 'All Records', path: '/records', icon: Files },
  ];

  if (user?.role === 'admin') {
    navItems.push({ name: 'User Management', path: '/users', icon: Users });
  }

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      {/* Sidebar - Premium Glassmorphism */}
      <div className="w-72 glass-panel-dark text-white flex flex-col shadow-2xl z-20 shrink-0 border-r border-slate-700/50">
        <div className="p-8 border-b border-slate-700/50 flex items-center gap-4">
          <div className="p-2 bg-slate-900 rounded-xl shadow-lg">
            <img src={logo} alt="Mind Matrix Logo" className="h-10 w-10 shrink-0 object-contain" />
          </div>
          <span className="font-bold text-xl leading-tight tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-100 to-white">
            Mind Matrix<br/>
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Land Records</span>
          </span>
        </div>
        
        <nav className="flex-1 px-4 py-8 space-y-2 overflow-y-auto custom-scrollbar">
          <p className="px-4 text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-6">Main Menu</p>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || 
                            (item.path !== '/' && location.pathname.startsWith(item.path));
            
            return (
              <Link 
                key={item.path}
                to={item.path} 
                className={`flex items-center gap-4 px-4 py-3.5 rounded-xl transition-all duration-300 group relative overflow-hidden ${
                  isActive 
                    ? 'bg-blue-600/20 text-blue-300 font-semibold shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] border border-blue-500/30' 
                    : 'text-slate-400 hover:bg-slate-800/80 hover:text-white border border-transparent'
                }`}
              >
                {isActive && <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-400 to-cyan-400 rounded-r-md"></div>}
                <Icon size={20} className={`${isActive ? 'text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]' : 'text-slate-500 group-hover:text-white'} transition-all duration-300`} /> 
                <span className="tracking-wide text-sm">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-800/50 bg-slate-900/50">
          <div className="flex items-center gap-3 mb-4 px-2">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-blue-400 text-white flex items-center justify-center font-bold text-sm shadow-md">
              {user?.full_name.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
              <p className="text-xs text-slate-400 capitalize truncate">{user?.role}</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-red-500/10 hover:text-red-400 transition-colors"
          >
            <LogOut size={16} /> Sign Out
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Top gradient accent */}
        <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-blue-600 to-cyan-400 z-50"></div>
        
        <main className="flex-1 overflow-auto bg-slate-50 relative z-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
