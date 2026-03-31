const StatsGrid = () => {
  return (
    <div className="grid grid-cols-3 gap-2">
      <div className="bg-white/5 border border-white/10 p-3 rounded-md">
        <div className="text-lg font-mono">18.5h</div>
        <div className="text-[10px] text-white/40">이번 주 총합</div>
      </div>

      <div className="bg-white/5 border border-white/10 p-3 rounded-md">
        <div className="text-lg font-mono">84점</div>
        <div className="text-[10px] text-white/40">평균 집중도</div>
      </div>

      <div className="bg-white/5 border border-white/10 p-3 rounded-md">
        <div className="text-lg font-mono">23분</div>
        <div className="text-[10px] text-white/40">최장 집중</div>
      </div>
    </div>
  );
};

export default StatsGrid;