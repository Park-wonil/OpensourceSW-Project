const SubjectChart = () => {
  const subjects = [
    { name: "수학", width: "80%", color: "bg-green-300", time: "4h" },
    { name: "영어", width: "60%", color: "bg-purple-400", time: "3h" },
    { name: "코딩", width: "40%", color: "bg-yellow-300", time: "2h" },
  ];

  return (
    <div className="bg-white/5 border border-white/10 p-4 rounded-lg">
      <div className="text-[11px] text-white/40 mb-3">
        과목별 공부
      </div>

      <div className="flex flex-col gap-3">
        {subjects.map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="text-xs w-12 text-white/60">{s.name}</span>

            <div className="flex-1 h-1 bg-white/10 rounded">
              <div className={`${s.color} h-full`} style={{ width: s.width }} />
            </div>

            <span className="text-[10px] text-white/40">{s.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SubjectChart;