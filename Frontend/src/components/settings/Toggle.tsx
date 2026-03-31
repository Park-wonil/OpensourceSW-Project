interface Props {
  enabled: boolean;
  onToggle: () => void;
}

const Toggle = ({ enabled, onToggle }: Props) => {
  return (
    <button
      onClick={onToggle}
      className={`w-10 h-5 rounded-full relative ${
        enabled ? "bg-green-300" : "bg-white/20"
      }`}
    >
      <div
        className={`w-4 h-4 bg-black rounded-full absolute top-0.5 transition ${
          enabled ? "left-5" : "left-1"
        }`}
      />
    </button>
  );
};

export default Toggle;