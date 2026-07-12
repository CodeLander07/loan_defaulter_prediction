import { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import NewPrediction from './pages/NewPrediction';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="flex bg-background h-screen overflow-hidden text-on-surface">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 flex flex-col relative z-10 overflow-hidden">
          <TopBar onMenuToggle={() => setSidebarOpen(true)} />
          <Routes>
            <Route path="/new-prediction" element={<NewPrediction />} />
            <Route path="*" element={<Navigate to="/new-prediction" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
