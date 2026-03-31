const BarChart = () => {
  const data = [40, 60, 30, 80, 50, 90, 70];

  return (
    <div className="bg-white/5 border border-white/10 p-4 rounded-lg">
      <div className="text-[11px] text-white/40 mb-3">
        일별 공부 시간
      </div>

      <div className="flex items-end gap-2 h-20">
        {data.map((h, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <div
              className={`w-full ${
                i === 6 ? "bg-green-300" : "bg-green-300/40"
              }`}
              style={{ height: `${h}%` }}
            />
            <span className="text-[9px] text-white/30">
              {["월","화","수","목","금","토","일"][i]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BarChart;