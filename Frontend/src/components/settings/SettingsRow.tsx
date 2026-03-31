import Toggle from "./Toggle";

interface Props {
  title: string;
  sub?: string;
  enabled?: boolean;
}

const SettingsRow = ({ title, sub, enabled = true }: Props) => {
  return (
    <div className="flex justify-between items-center p-3 border-b border-white/10">
      <div>
        <div className="text-sm">{title}</div>
        {sub && <div className="text-xs text-white/40">{sub}</div>}
      </div>

      <Toggle enabled={enabled} onToggle={() => {}} />
    </div>
  );
};

export default SettingsRow;