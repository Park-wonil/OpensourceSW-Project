import CameraBox from "../components/timer/CameraBox";
import TimerDisplay from "../components/timer/TimerDisplay";
import TimerControls from "../components/timer/TimerControls";
import StateBadge from "../components/timer/StateBadge";
import FocusScore from "../components/sidebar/FocusScore";

const TimerPage = () => {
  return (
    <div className="grid grid-cols-[1fr_260px] min-h-[600px]">

      {/* 왼쪽 */}
      <div className="flex flex-col items-center justify-center gap-6 border-r border-white/10">
        <CameraBox />
        <StateBadge status="studying" />
        <TimerDisplay time="25:00" />
        <TimerControls />
      </div>

      {/* 오른쪽 */}
      <div className="p-4 flex flex-col gap-4">
        <FocusScore score={82} />
      </div>

    </div>
  );
};

export default TimerPage;