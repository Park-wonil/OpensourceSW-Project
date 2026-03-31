export const getStatus = async () => {
  const res = await fetch("http://localhost:5000/detect");
  return res.json();
};

export const startCamera = async () => {
  await fetch("http://localhost:5000/start");
};

export const stopCamera = async () => {
  await fetch("http://localhost:5000/stop");
};