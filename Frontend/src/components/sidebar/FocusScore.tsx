interface Props {
  score: number;
}

const FocusScore = ({ score }: Props) => {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-3">

      {/* 상단 */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-[10px] text-white/40 tracking-wider">
          집중도 점수
        </span>

        <span className="text-[11px] font-mono text-green-300">
          {score}점
        </span>
      </div>

      {/* 바 */}
      <div className="h-[5px] bg-white/10 rounded overflow-hidden">
        <div
          className="h-full bg-green-300 transition-all duration-300"
          style={{ width: `${score}%` }}
        />
      </div>

    </div>
  );
};

export default FocusScore;