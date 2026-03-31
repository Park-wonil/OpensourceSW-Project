interface Props {
  time: string;
}

const TimerDisplay = ({ time }: Props) => {
  return (
    <div className="text-center">
      <div className="font-mono text-[56px] leading-none text-[#f0ede6] tracking-tight">
        {time}
      </div>

      <div className="mt-2 text-[11px] text-white/30 tracking-widest font-mono">
        뽀모도로 세션 1/4
      </div>
    </div>
  );
};

export default TimerDisplay;