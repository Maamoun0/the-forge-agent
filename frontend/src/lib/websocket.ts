import { useEffect, useRef, useState, useCallback } from 'react';

export interface AgentLog {
  agent: string;
  action: string;
  detail: string;
  status: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
}

export interface WsMessage {
  type: string;
  message?: string;
  phase?: string;
  node?: string;
  log?: AgentLog;
  blueprint?: any;
  files?: Record<string, string>;
}

export function useForgeWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WsMessage[]>([]);
  const [currentPhase, setCurrentPhase] = useState<string>('idle');
  const [blueprint, setBlueprint] = useState<any>(null);
  const [generatedFiles, setGeneratedFiles] = useState<Record<string, string>>({});
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to The Forge WS');
    };

    ws.onmessage = (event) => {
      try {
        const data: WsMessage = JSON.parse(event.data);
        setMessages((prev) => [...prev, data]);
        
        if (data.phase && data.phase !== currentPhase) {
          setCurrentPhase(data.phase);
        }

        if (data.type === 'blueprint' && data.blueprint) {
          setBlueprint(data.blueprint);
        }

        if (data.type === 'files_update' && data.files) {
          setGeneratedFiles(data.files);
        }
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from The Forge WS');
    };

    wsRef.current = ws;
  }, [url, currentPhase]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendProjectIdea = useCallback((idea: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      // Clear previous messages
      setMessages([]);
      setCurrentPhase('starting');
      setBlueprint(null);
      setGeneratedFiles({});
      
      wsRef.current.send(
        JSON.stringify({
          type: 'start_project',
          idea: idea,
        })
      );
    } else {
      console.error('WebSocket is not connected');
    }
  }, []);

  const approveBlueprint = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'approve_blueprint',
        })
      );
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    isConnected,
    messages,
    currentPhase,
    blueprint,
    generatedFiles,
    sendProjectIdea,
    approveBlueprint,
    connect,
  };
}
