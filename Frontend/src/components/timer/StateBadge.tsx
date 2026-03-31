interface Props {
  status: "studying" | "away" | "drowsy";
}

const StateBadge = ({ status }: Props) => {
  const styles = {
    studying: "bg-green-300/10 text-green-300 border-green-300/30",
    away: "bg-orange-300/10 text-orange-300 border-orange-300/30",
    drowsy: "bg-yellow-300/10 text-yellow-300 border-yellow-300/30",
  };

  const labels = {
    studying: "공부 중",
    away: "자리 비움",
    drowsy: "졸음 감지",
  };

  return (
    <div
      className={`flex items-center gap-2 px-3 py-1 text-[11px] font-semibold tracking-wide rounded-full border ${styles[status]}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
      {labels[status]}
    </div>
  );
};

export default StateBadge;