const EventLog = () => {
  const logs = [
    { color: "bg-green-300", text: "14:32 — 공부 시작" },
    { color: "bg-orange-400", text: "14:48 — 자리 이탈" },
    { color: "bg-yellow-300", text: "15:12 — 졸음 감지" },
  ];

  return (
    <div>
      <div className="text-[10px] text-white/40 mb-2 tracking-wider">
        이벤트 로그
      </div>

      <div className="flex flex-col gap-2 text-[10px] font-mono text-white/40">
        {logs.map((log, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full ${log.color}`} />
            {log.text}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EventLog;