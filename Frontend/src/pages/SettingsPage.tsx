import SettingsRow from "../components/settings/SettingsRow";

const SettingsPage = () => {
  return (
    <div className="p-4 flex flex-col gap-3 min-h-[560px]">
      <div className="bg-white/5 border border-white/10 rounded-lg overflow-hidden">
        <SettingsRow title="뽀모도로 모드" sub="자동 전환" />
        <SettingsRow title="자리 이탈 감지" />
        <SettingsRow title="졸음 감지" />
        <SettingsRow title="카메라 표시" />
      </div>
    </div>
  );
};

export default SettingsPage;