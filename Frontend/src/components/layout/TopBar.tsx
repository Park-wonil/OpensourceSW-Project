import NavTabs from "./NavTabs";

interface Props {
  current: string;
  setTab: (tab: string) => void;
}

const TopBar = ({ current, setTab }: Props) => {
  return (
    <div className="flex justify-between items-center px-5 py-3 border-b border-white/10">

      <div className="text-green-300 text-sm font-mono tracking-widest">
        FOCUSAI
      </div>

      <NavTabs current={current} onChange={setTab} />

      <div className="w-2 h-2 bg-green-300 rounded-full animate-pulse" />

    </div>
  );
};

export default TopBar;