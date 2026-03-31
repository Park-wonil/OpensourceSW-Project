import { useState } from "react";
import TopBar from "./components/layout/TopBar";
import TimerPage from "./pages/TimerPage";
import StatsPage from "./pages/StatsPage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  const [tab, setTab] = useState("timer");

  return (
    <div className="bg-[#0d0d0f] min-h-screen flex justify-center items-center text-white">
      <div className="w-full max-w-[720px] border border-white/10 rounded-xl overflow-hidden">

        <TopBar current={tab} setTab={setTab} />

        {tab === "timer" && <TimerPage />}
        {tab === "stats" && <StatsPage />}
        {tab === "settings" && <SettingsPage />}

      </div>
    </div>
  );
}

export default App;