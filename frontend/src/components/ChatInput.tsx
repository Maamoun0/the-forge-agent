import { useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

interface ChatInputProps {
  onSend: (idea: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [idea, setIdea] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (idea.trim() && !disabled) {
      onSend(idea);
      setIdea('');
    }
  };

  return (
    <motion.form 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      onSubmit={handleSubmit} 
      className="relative w-full max-w-4xl mx-auto"
    >
      <div className="relative flex items-center w-full bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-2 shadow-2xl transition-all focus-within:border-blue-500/50 focus-within:ring-2 focus-within:ring-blue-500/20">
        <div className="pl-4 pr-2 text-blue-400">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <input
          type="text"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          disabled={disabled}
          placeholder="Describe your project idea... (e.g., A task manager with React and FastAPI)"
          className="w-full bg-transparent border-none text-white placeholder-gray-400 focus:outline-none p-3 text-lg disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!idea.trim() || disabled}
          className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed ml-2 flex items-center justify-center shadow-lg shadow-blue-500/30"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </motion.form>
  );
}
