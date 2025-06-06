import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/providers/AuthProvider";
import toast from "react-hot-toast";

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  autoReconnect?: boolean;
  reconnectInterval?: number;
}

export function useWebSocket(
  endpoint: string,
  options: UseWebSocketOptions = {}
) {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoReconnect = true,
    reconnectInterval = 5000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const { user } = useAuth();

  const connect = () => {
    if (!user) return;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const token = document.cookie
      .split("; ")
      .find((row) => row.startsWith("access_token="))
      ?.split("=")[1];

    if (!token) {
      console.error("No access token found for WebSocket connection");
      return;
    }

    const fullUrl = `${wsUrl}/api/v1/ws${endpoint}?token=${token}`;

    try {
      wsRef.current = new WebSocket(fullUrl);

      wsRef.current.onopen = () => {
        setIsConnected(true);
        onConnect?.();
        console.log(`WebSocket connected to ${endpoint}`);

        // Clear any existing reconnection timeout
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage?.(data);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      wsRef.current.onclose = (event) => {
        setIsConnected(false);
        onDisconnect?.();
        console.log(
          `WebSocket disconnected from ${endpoint}`,
          event.code,
          event.reason
        );

        // Auto-reconnect if enabled and not a normal closure
        if (autoReconnect && event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect to ${endpoint}...`);
            connect();
          }, reconnectInterval);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error(`WebSocket error on ${endpoint}:`, error);
        onError?.(error);
        toast.error("WebSocket connection error");
      };
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, "Manual disconnect");
      wsRef.current = null;
    }
  };

  const sendMessage = (data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        typeof data === "string" ? data : JSON.stringify(data)
      );
    } else {
      console.warn("WebSocket is not connected");
      toast.error("WebSocket is not connected");
    }
  };

  const sendPing = () => {
    sendMessage("ping");
  };

  useEffect(() => {
    if (user) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [user, endpoint]);

  // Send periodic pings to keep connection alive
  useEffect(() => {
    if (isConnected) {
      const pingInterval = setInterval(() => {
        sendPing();
      }, 30000); // Send ping every 30 seconds

      return () => clearInterval(pingInterval);
    }
  }, [isConnected]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    sendPing,
    connect,
    disconnect,
  };
}
