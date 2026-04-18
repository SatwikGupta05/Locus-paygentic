"use client";

import { useEffect, useState } from "react";
import { websocketUrl } from "../lib/api";

type LiveCardProps = {
  title: string;
  path: string;
};

export function LiveCard({ title, path }: LiveCardProps) {
  const [payload, setPayload] = useState<Record<string, unknown>>({});

  useEffect(() => {
    const socket = new WebSocket(websocketUrl(path));
    socket.onmessage = (event) => {
      try {
        setPayload(JSON.parse(event.data));
      } catch {
        setPayload({ raw: event.data });
      }
    };
    return () => socket.close();
  }, [path]);

  return (
    <div className="panel">
      <h3 className="mb-3 text-lg font-semibold text-foam">{title}</h3>
      <pre className="overflow-auto text-xs text-white/80">{JSON.stringify(payload, null, 2)}</pre>
    </div>
  );
}
