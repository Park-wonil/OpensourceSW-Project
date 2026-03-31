import { useEffect, useState } from "react";
import { getStatus } from "../api/focusApi";

export const useFocusData = () => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await getStatus();
      setData(res);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return data;
};