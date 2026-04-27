import React from 'react';
import { motion } from 'framer-motion';
import { Folder, File, FileCode, FileJson, FileText, ChevronRight, ChevronDown } from 'lucide-react';

interface FileNode {
  path: string;
  type: 'file' | 'directory';
  size?: number | null;
}

interface FileTreeProps {
  files: Record<string, string>; // { path: content }
}

export function FileTree({ files }: FileTreeProps) {
  const filePaths = Object.keys(files).sort();

  if (filePaths.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 font-mono text-xs opacity-50">
        <Folder className="w-8 h-8 mb-2" />
        <p>No files generated yet</p>
      </div>
    );
  }

  const getIcon = (path: string) => {
    const ext = path.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'py':
      case 'js':
      case 'ts':
      case 'tsx':
        return <FileCode className="w-4 h-4 text-blue-400" />;
      case 'json':
        return <FileJson className="w-4 h-4 text-yellow-400" />;
      case 'md':
        return <FileText className="w-4 h-4 text-gray-400" />;
      default:
        return <File className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0d1117] border border-gray-800 rounded-2xl overflow-hidden shadow-2xl">
      <div className="p-4 bg-gray-900/80 border-b border-gray-800 flex items-center space-x-2">
        <Folder className="w-4 h-4 text-gray-400" />
        <h2 className="text-xs font-semibold text-gray-200 uppercase tracking-wider">Project Files</h2>
      </div>
      
      <div className="flex-1 p-4 overflow-y-auto custom-scrollbar font-mono text-sm">
        <div className="space-y-1">
          {filePaths.map((path) => (
            <motion.div
              key={path}
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-2 p-1.5 hover:bg-gray-800/50 rounded-md transition-colors cursor-pointer group"
            >
              {getIcon(path)}
              <span className="text-gray-300 group-hover:text-blue-400 truncate">{path}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
