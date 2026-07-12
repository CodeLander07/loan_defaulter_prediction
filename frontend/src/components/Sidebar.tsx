import { Link, useLocation } from 'react-router-dom';
import { NAV_ITEMS } from '../data/mockData';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

function Sidebar({ isOpen, onClose }: SidebarProps) {
  const location = useLocation();

  const mainNav = NAV_ITEMS.filter(i => i.label !== 'Settings');
  const bottomNav = NAV_ITEMS.filter(i => i.label === 'Settings');

  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black/60 z-20 lg:hidden backdrop-blur-sm" onClick={onClose} />}
      <aside
        className={`
          flex flex-col h-full py-4 gap-element-gap-sm bg-surface-container-low border-r border-outline-variant/10
          fixed lg:relative inset-y-0 left-0 z-50 w-64 shrink-0
          transition-all duration-300 ease-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="px-6 mb-8 animate-entrance">
          <h1 className="font-headline-md text-headline-md text-primary tracking-tight">Default Prediction</h1>
          <p className="font-label-sm text-label-sm text-on-surface-variant/60 uppercase tracking-widest">Early Warning Active</p>
        </div>

        <nav className="flex-1 space-y-1 animate-entrance delay-1">
          {mainNav.map(item => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={`
                  flex items-center px-3 py-1.5 mx-2 rounded-full transition-all duration-300 group
                  ${isActive
                    ? 'bg-secondary-container text-on-secondary-container font-semibold'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-variant hover:scale-[1.02]'
                  }
                `}
              >
                <span className={`material-symbols-outlined mr-3 text-[20px] transition-all duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110 group-hover:text-primary'}`}>{item.icon}</span>
                <span className="font-label-md text-label-md">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto px-4 space-y-4 animate-entrance delay-2">
          <div className="flex flex-col gap-1 border-t border-outline-variant/10 pt-4">
            {bottomNav.map(item => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={onClose}
                  className={`
                    flex items-center px-3 py-1.5 mx-0 rounded-full transition-all duration-300 group
                    ${isActive
                      ? 'bg-secondary-container text-on-secondary-container font-semibold'
                      : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-variant hover:scale-[1.02]'
                    }
                  `}
                >
                  <span className={`material-symbols-outlined mr-3 text-[20px] transition-all duration-300 group-hover:scale-110 group-hover:text-primary`}>{item.icon}</span>
                  <span className="font-label-md text-label-md">{item.label}</span>
                </Link>
              );
            })}
            <Link to="/support" className="text-on-surface-variant hover:text-on-surface flex items-center px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-surface-variant hover:scale-[1.02] group font-label-md text-label-md">
              <span className="material-symbols-outlined mr-3 text-[18px] group-hover:scale-110 group-hover:text-primary transition-all duration-300">contact_support</span>
              Support
            </Link>
            <Link to="/logs" className="text-on-surface-variant hover:text-on-surface flex items-center px-3 py-1.5 rounded-full transition-all duration-300 hover:bg-surface-variant hover:scale-[1.02] group font-label-md text-label-md">
              <span className="material-symbols-outlined mr-3 text-[18px] group-hover:scale-110 group-hover:text-primary transition-all duration-300">terminal</span>
              Logs
            </Link>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
