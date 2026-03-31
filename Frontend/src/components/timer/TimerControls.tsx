import { useState } from "react";

const TimerControls = () => {
  const [running, setRunning] = useState(false);

  return (
    <div className="flex items-center gap-3">

      {/* 리셋 */}
      <button className="w-10 h-10 rounded-full bg-white/5 border border-white/10 text-white/60 hover:bg-white/10 transition">
        ↺
      </button>

      {/* 플레이 버튼 */}
      <button
        onClick={() => setRunning(!running)}
        className="w-14 h-14 rounded-full bg-green-300 flex items-center justify-center hover:scale-105 active:scale-95 transition"
      >
        {running ? (
          <div className="flex gap-1">
            <div className="w-1 h-4 bg-black"></div>
            <div className="w-1 h-4 bg-black"></div>
          </div>
        ) : (
          <div className="ml-1 w-0 h-0 border-l-[12px] border-l-black border-y-[8px] border-y-transparent"></div>
        )}
      </button>

      {/* 상태 변경 버튼 */}
      <button className="w-10 h-10 rounded-full bg-white/5 border border-white/10 text-white/60 hover:bg-white/10 transition">
        ⊙
      </button>

    </div>
  );
};

export default TimerControls;