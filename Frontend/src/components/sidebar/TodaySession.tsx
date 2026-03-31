const TodaySession = () => {
  return (
    <div className="bg-white/5 border border-white/10 rounded-md p-3">
      <div className="text-xs text-white/40 mb-1">오늘 세션</div>
      <div className="text-lg font-mono text-white">
        <span className="text-green-300">3</span>h 42m
      </div>
    </div>
  );
};

export default TodaySession;