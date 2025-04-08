import React, { useState } from "react";
import { Menu, X } from "lucide-react";

interface NavbarProps {
  activeTab: 'metrics' | 'charts' | 'search' | 'projects-table' | 'insigths';
  setActiveTab: (tab: NavbarProps['activeTab']) => void;
}

const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [menuOpen, setMenuOpen] = useState(false);

  const tabs = [
    { id: 'metrics', label: 'Métricas', icon: 'fa-chart-bar' },
    { id: 'charts', label: 'Gráficos', icon: 'fa-chart-pie' },
    { id: 'search', label: 'Buscar', icon: 'fa-search' },
    { id: 'projects-table', label: 'Proyectos', icon: 'fa-list' },
    { id: 'insigths', label: 'Insights', icon: 'fa-lightbulb' }
  ];

  const renderTabs = (isMobile = false) => (
    <ul className={`flex ${isMobile ? "flex-col gap-3 mt-4" : "space-x-6"}`}>
      {tabs.map((tab) => (
        <li key={tab.id}>
          <button
            onClick={() => {
              setActiveTab(tab.id as NavbarProps["activeTab"]);
              setMenuOpen(false);
            }}
            className={`pb-1 text-lg md:text-xl font-medium transition-all ${
              activeTab === tab.id
                ? 'text-purple-600 border-b-2 border-purple-600'
                : 'text-gray-700 hover:text-purple-600 hover:border-b-2 hover:border-purple-200'
            }`}
          >
            <i className={`fas ${tab.icon} mr-2`}></i>
            {tab.label}
          </button>
        </li>
      ))}
    </ul>
  );

  return (
    <nav className="bg-white shadow-md fixed w-full top-0 left-0 z-50 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-2 flex justify-between items-center">
        {/* LOGO */}
        <div className="flex items-center">
          <img
            src="/public/conti-negro.png"
            alt="Logo UContinental"
            className="h-14 md:h-24 w-auto"
          />
        </div>

        {/* Desktop Nav */}
        <div className="hidden md:flex">{renderTabs()}</div>

        {/* Mobile Button */}
        <div className="md:hidden">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="text-gray-600 hover:text-purple-600 transition"
          >
            {menuOpen ? <X size={28} /> : <Menu size={28} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden bg-white px-4 pb-4 shadow-md border-t border-gray-100">
          {renderTabs(true)}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
