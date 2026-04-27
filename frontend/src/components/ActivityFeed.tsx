import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, CheckCircle2, AlertCircle, Info, Loader2 } from 'lucide-react';
import { WsMessage } from '../lib/websocket';

interface ActivityFeedProps {
  messages: WsMessage[];
  currentPhase: string;
}

export function ActivityFeed({ messages, currentPhase }: ActivityFeedProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const agentLogs = messages.filter((m) => m.type === 'agent_log' && m.log);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-green-400" />;
      case 'warning':
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const getPhaseName = (phase: string) => {
    const phases: Record<string, string> = {
      idle: 'Waiting for Input',
      starting: 'Initializing',
      research: 'Researching',
      architecture: 'Designing Blueprint',
      approval: 'Waiting for Approval',
      development: 'Writing Code',
      integration: 'Integrating Files',
      qa: 'Running Tests',
      fixing: 'Fixing Errors',
      reporting: 'Generating Docs',
      complete: 'Done',
      error: 'Error',
    };
    return phases[phase] || phase;
  };

  return (
    <div className="flex flex-col h-full bg-[#0d1117] border border-gray-800 rounded-2xl overflow-hidden shadow-2xl relative">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-900/80 border-b border-gray-800 backdrop-blur-md z-10">
        <div className="flex items-center space-x-2">
          <Terminal className="w-5 h-5 text-gray-400" />
          <h2 className="text-sm font-semibold text-gray-200 uppercase tracking-wider">Agent Activity</h2>
        </div>
        <div className="flex items-center space-x-2 bg-gray-800/50 px-3 py-1 rounded-full border border-gray-700">
          {currentPhase !== 'complete' && currentPhase !== 'idle' && currentPhase !== 'error' && (
            <Loader2 className="w-3 h-3 text-blue-400 animate-spin" />
          )}
          <span className="text-xs font-medium text-gray-300">
            {getPhaseName(currentPhase)}
          </span>
        </div>
      </div>

      {/* Feed */}
      <div className="flex-1 p-4 overflow-y-auto font-mono text-sm space-y-3 custom-scrollbar">
        <AnimatePresence initial={false}>
          {agentLogs.length === 0 && currentPhase === 'idle' && (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              className="text-gray-500 text-center mt-10"
            >
              System ready. Awaiting project details...
            </motion.div>
          )}

          {agentLogs.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-start space-x-3 bg-gray-900/30 p-2 rounded-lg border border-gray-800/50 hover:bg-gray-800/50 transition-colors"
            >
              <div className="mt-0.5">{getStatusIcon(msg.log!.status)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <span className="text-purple-400 font-semibold uppercase text-xs">
                    [{msg.log!.agent}]
                  </span>
                  <span className="text-gray-200">{msg.log!.action}</span>
                </div>
                {msg.log!.detail && (
                  <p className="text-gray-500 text-xs mt-1 mt-0.5 break-words">
                    {msg.log!.detail}
                  </p>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
