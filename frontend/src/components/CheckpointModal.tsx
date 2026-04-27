import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, X, Check, FileCode, Database, Globe } from 'lucide-react';

interface Blueprint {
  files: any[];
  db_schema?: string;
  api_routes: any[];
  architecture_notes: string;
}

interface CheckpointModalProps {
  isOpen: boolean;
  blueprint: Blueprint | null;
  onApprove: () => void;
  onReject: () => void;
}

export function CheckpointModal({ isOpen, blueprint, onApprove, onReject }: CheckpointModalProps) {
  if (!isOpen || !blueprint) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="bg-[#161b22] border border-gray-800 rounded-3xl shadow-2xl w-full max-w-4xl max-h-[85vh] overflow-hidden flex flex-col"
        >
          {/* Header */}
          <div className="p-6 bg-gray-900/50 border-b border-gray-800 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/20 rounded-xl">
                <ShieldCheck className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Review Architectural Blueprint</h2>
                <p className="text-sm text-gray-400">The Architect has finished the design. Please approve to start coding.</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
            {/* Notes */}
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Architecture Notes</h3>
              <div className="p-4 bg-gray-900/50 rounded-2xl border border-gray-800 text-gray-300 leading-relaxed">
                {blueprint.architecture_notes}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Files */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-widest flex items-center space-x-2">
                  <FileCode className="w-4 h-4" />
                  <span>Files to be created ({blueprint.files.length})</span>
                </h3>
                <div className="space-y-2">
                  {blueprint.files.slice(0, 10).map((file, i) => (
                    <div key={i} className="text-xs font-mono p-2 bg-gray-900/30 rounded border border-gray-800 text-gray-400 truncate">
                      {file.path}
                    </div>
                  ))}
                  {blueprint.files.length > 10 && <div className="text-xs text-gray-500 pl-2">... and {blueprint.files.length - 10} more</div>}
                </div>
              </div>

              {/* API & DB */}
              <div className="space-y-8">
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-widest flex items-center space-x-2">
                    <Globe className="w-4 h-4" />
                    <span>API Endpoints ({blueprint.api_routes.length})</span>
                  </h3>
                  <div className="space-y-2">
                    {blueprint.api_routes.map((route, i) => (
                      <div key={i} className="text-xs font-mono p-2 bg-gray-900/30 rounded border border-gray-800 text-gray-400">
                        <span className="text-blue-400 font-bold mr-2">{route.method}</span> {route.path}
                      </div>
                    ))}
                  </div>
                </div>

                {blueprint.db_schema && (
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-widest flex items-center space-x-2">
                      <Database className="w-4 h-4" />
                      <span>Database Schema</span>
                    </h3>
                    <pre className="text-[10px] font-mono p-3 bg-black/40 rounded border border-gray-800 text-green-400/80 overflow-x-auto">
                      {blueprint.db_schema}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 bg-gray-900/80 border-t border-gray-800 flex items-center justify-end space-x-4">
            <button
              onClick={onReject}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-all font-medium"
            >
              <X className="w-4 h-4" />
              <span>Reject & Retry</span>
            </button>
            <button
              onClick={onApprove}
              className="flex items-center space-x-2 px-8 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20 transition-all font-bold"
            >
              <Check className="w-4 h-4" />
              <span>Approve & Build</span>
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
