'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Cpu } from 'lucide-react';
import { useForgeWebSocket } from '../lib/websocket';
import { ChatInput } from '../components/ChatInput';
import { ActivityFeed } from '../components/ActivityFeed';
import { OutputCard } from '../components/OutputCard';
import { FileTree } from '../components/FileTree';
import { CheckpointModal } from '../components/CheckpointModal';

export default function Dashboard() {
  // Assuming the FastAPI backend runs on 8000
  const { messages, currentPhase, sendProjectIdea, approveBlueprint, isConnected, blueprint, generatedFiles } = useForgeWebSocket('ws://127.0.0.1:8000/ws');
  const [hasStarted, setHasStarted] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleSend = (idea: string) => {
    sendProjectIdea(idea);
    setHasStarted(true);
  };

  const handleApprove = () => {
    approveBlueprint();
    setIsModalOpen(false);
  };

  // Open modal when blueprint arrives
  useEffect(() => {
    if (currentPhase === 'approval' && blueprint) {
      setIsModalOpen(true);
    }
  }, [currentPhase, blueprint]);

  const isComplete = currentPhase === 'complete';

  return (
    <main className="min-h-screen mesh-bg flex flex-col p-6">
      {/* Header */}
      <header className="flex items-center justify-between mb-8 px-4">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600/20 p-2 rounded-xl border border-blue-500/30">
            <Bot className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
              The Forge
            </h1>
            <p className="text-xs text-gray-400 uppercase tracking-widest font-semibold">AI Agentic Factory</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 bg-gray-900/50 px-4 py-2 rounded-full border border-gray-800">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]' : 'bg-red-500'}`} />
          <span className="text-xs font-mono text-gray-300">
            {isConnected ? 'Engine Online' : 'Engine Offline'}
          </span>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col max-w-6xl w-full mx-auto relative">
        
        {/* Initial View (Centered Search) */}
        <AnimatePresence mode="wait">
          {!hasStarted ? (
            <motion.div 
              key="hero"
              exit={{ opacity: 0, y: -50 }}
              className="flex-1 flex flex-col items-center justify-center space-y-8"
            >
              <div className="text-center space-y-4">
                <motion.div 
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.5 }}
                  className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl mx-auto flex items-center justify-center shadow-2xl shadow-blue-500/20 rotate-3"
                >
                  <Cpu className="w-10 h-10 text-white" />
                </motion.div>
                <h2 className="text-4xl md:text-5xl font-extrabold text-white tracking-tight">
                  What shall we build today?
                </h2>
                <p className="text-gray-400 max-w-2xl mx-auto text-lg">
                  Describe your idea, and our team of AI agents will plan, write, test, and document the entire codebase.
                </p>
              </div>
              <ChatInput onSend={handleSend} disabled={!isConnected} />
            </motion.div>
          ) : (
            /* Active View (Dashboard) */
            <motion.div 
              key="dashboard"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex-1 flex flex-col h-full space-y-6"
            >
              <div className="w-full">
                <ChatInput onSend={handleSend} disabled={currentPhase !== 'complete' && currentPhase !== 'error'} />
              </div>

              <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[500px]">
                {/* Left Col: Activity Feed */}
                <div className="lg:col-span-2 h-full">
                  <ActivityFeed messages={messages} currentPhase={currentPhase} />
                </div>
                
                {/* Right Col: Info / Output */}
                <div className="flex flex-col space-y-6">
                  <FileTree files={generatedFiles} />
                </div>
              </div>

              {/* Modals */}
              <CheckpointModal 
                isOpen={isModalOpen || (currentPhase === 'approval' && !!blueprint)} 
                blueprint={blueprint} 
                onApprove={handleApprove} 
                onReject={() => setIsModalOpen(false)} 
              />

              <AnimatePresence>
                {isComplete && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="absolute inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm rounded-3xl"
                  >
                    <OutputCard status={currentPhase} />
                  </motion.div>
                )}
              </AnimatePresence>

            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </main>
  );
}
