import { motion } from 'framer-motion';
import { Download, FolderOpen, FileText, CheckCircle } from 'lucide-react';

interface OutputCardProps {
  status: string;
}

export function OutputCard({ status }: OutputCardProps) {
  if (status !== 'complete') return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ type: 'spring', bounce: 0.4 }}
      className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 border border-blue-500/30 p-8 rounded-3xl shadow-2xl backdrop-blur-xl relative overflow-hidden"
    >
      {/* Decorative background glow */}
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-blue-500/20 rounded-full blur-3xl" />
      <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-purple-500/20 rounded-full blur-3xl" />

      <div className="relative z-10 flex flex-col items-center text-center space-y-6">
        <div className="w-16 h-16 bg-blue-500/20 rounded-full flex items-center justify-center border border-blue-400/30">
          <CheckCircle className="w-8 h-8 text-blue-400" />
        </div>
        
        <div>
          <h2 className="text-2xl font-bold text-white mb-2">Project Ready!</h2>
          <p className="text-blue-200">The Forge has successfully generated your codebase.</p>
        </div>

        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl transition-all shadow-lg shadow-blue-500/20 font-medium">
            <Download className="w-5 h-5" />
            <span>Download ZIP</span>
          </button>
          
          <button className="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 px-6 py-3 rounded-xl transition-all font-medium">
            <FolderOpen className="w-5 h-5" />
            <span>Open Folder</span>
          </button>

          <button className="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 px-6 py-3 rounded-xl transition-all font-medium">
            <FileText className="w-5 h-5" />
            <span>View Report</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
}
