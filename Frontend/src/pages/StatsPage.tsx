import StatsGrid from "../components/stats/StatsGrid";
import BarChart from "../components/stats/BarChart";
import SubjectChart from "../components/stats/SubjectChart";

const StatsPage = () => {
  return (
    <div className="p-4 flex flex-col gap-4 min-h-[560px]">
      <StatsGrid />
      <BarChart />
      <SubjectChart />
    </div>
  );
};

export default StatsPage;