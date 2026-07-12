interface TopBarProps {
  onMenuToggle: () => void;
}

function TopBar({ onMenuToggle }: TopBarProps) {
  return (
    <header className="flex justify-between items-center px-6 py-4 w-full bg-surface-container-low/50 backdrop-blur-md shadow-sm sticky top-0 z-40 border-b border-outline-variant/5">
      <div className="flex items-center gap-4 animate-entrance">
        <button onClick={onMenuToggle} className="lg:hidden p-2 text-on-surface-variant hover:text-on-surface transition-all hover:scale-110 active:scale-95">
          <span className="material-symbols-outlined text-[24px]">menu</span>
        </button>
        <div className="h-8 w-8 bg-primary rounded-full flex items-center justify-center text-on-primary animate-float">
          <span className="material-symbols-outlined text-[18px]">shield_with_heart</span>
        </div>
        <span className="font-headline-sm text-headline-sm font-bold text-primary">Default Prediction</span>
        <div className="h-4 w-px bg-outline-variant/30" />
        <span className="font-body-md text-body-md text-on-surface-variant flex items-center gap-2">
          Model Context <span className="indicator-dot" />
          <span className="ml-1 opacity-60">— System #4092</span>
        </span>
      </div>

      <div className="flex items-center gap-element-gap-md animate-entrance-right">
        <div className="relative group">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant text-[18px] transition-all group-focus-within:text-primary">search</span>
          <input
            className="bg-surface-container-highest/50 border-none rounded-full pl-9 pr-4 py-1.5 text-body-sm focus:ring-1 focus:ring-primary/50 w-64 transition-all duration-300 placeholder:text-on-surface-variant/40 focus:w-80 focus:bg-surface-container-highest focus:shadow-[0_0_20px_rgba(221,183,255,0.1)] hover:bg-surface-container-highest/80"
            placeholder="Search database..."
            type="text"
          />
        </div>
        <button className="p-2 text-on-surface-variant hover:bg-surface-variant/50 rounded-full transition-all duration-300 hover:scale-110 hover:text-primary active:scale-95">
          <span className="material-symbols-outlined text-[20px]">notifications</span>
        </button>
        <button className="p-2 text-on-surface-variant hover:bg-surface-variant/50 rounded-full transition-all duration-300 hover:scale-110 hover:text-primary active:scale-95">
          <span className="material-symbols-outlined text-[20px]">help</span>
        </button>
        <button className="bg-primary text-on-primary-container px-4 py-1.5 rounded-full font-label-md text-label-md flex items-center gap-2 transition-all duration-300 hover:scale-[1.04] hover:shadow-lg hover:shadow-primary/25 active:scale-[0.97]">
          <span className="material-symbols-outlined text-[18px]">account_circle</span>
          Account
        </button>
      </div>
    </header>
  );
}

export default TopBar;
