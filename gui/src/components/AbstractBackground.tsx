// 1. DYNAMIC BACKGROUND
// A subtle, pulsing gradient background that moves
export const AbstractBackground = ({ active }: { active: boolean }) => (
    <div className={`absolute inset-0 z-0 overflow-hidden pointer-events-none transition-opacity duration-1000 ${active ? 'opacity-100' : 'opacity-20'}`}>
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 animate-gradient-xy"></div>
        <div className="absolute top-0 left-0 w-full h-full opacity-30 mix-blend-overlay filter blur-3xl animate-blob">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500 rounded-full"></div>
            <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-pink-500 rounded-full animation-delay-2000"></div>
            <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-blue-500 rounded-full animation-delay-4000"></div>
        </div>
    </div>
);

export default AbstractBackground;