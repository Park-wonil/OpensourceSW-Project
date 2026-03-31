const CameraBox = () => {
  return (
    <div className="relative w-[180px] h-[135px] bg-[#111115] border border-green-300/20 rounded-md overflow-hidden flex items-center justify-center">

      <img
        src="http://localhost:5000/video"
        className="absolute inset-0 w-full h-full object-cover"
      />

      {/* corners */}
      <div className="absolute top-1 left-1 w-3 h-3 border-l border-t border-green-300/40"></div>
      <div className="absolute top-1 right-1 w-3 h-3 border-r border-t border-green-300/40"></div>
      <div className="absolute bottom-1 left-1 w-3 h-3 border-l border-b border-green-300/40"></div>
      <div className="absolute bottom-1 right-1 w-3 h-3 border-r border-b border-green-300/40"></div>

      <div className="absolute bottom-1 text-[9px] text-green-300 font-mono">
        FACE DETECTED
      </div>
    </div>
  );
};

export default CameraBox;