interface Props {
  current: string;
  onChange: (tab: string) => void;
}

const NavTabs = ({ current, onChange }: Props) => {
  const tabs = ["timer", "stats", "settings"];

  return (
    <div className="flex gap-1 bg-white/5 rounded-md p-1">
      {tabs.map((tab) => (
        <button
          key={tab}
          onClick={() => onChange(tab)}
          className={`px-3 py-1 text-xs rounded ${
            current === tab
              ? "bg-[#1e1e24] text-green-300"
              : "text-white/40"
          }`}
        >
          {tab === "timer" && "타이머"}
          {tab === "stats" && "통계"}
          {tab === "settings" && "설정"}
        </button>
      ))}
    </div>
  );
};

export default NavTabs;