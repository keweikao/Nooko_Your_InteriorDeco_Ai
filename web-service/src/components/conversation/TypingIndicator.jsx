import React from 'react';
import { motion } from 'framer-motion';

/**
 * Purpose: 顯示一個 AI 正在輸入的動畫指示器，提供視覺反饋。
 *
 * Input (Props): 無
 *
 * Output:
 *   - 渲染一個由三個跳動圓點組成的動畫 UI 元件。
 */
function TypingIndicator() {
  const dotVariants = {
    initial: { y: '0%' },
    animate: { y: '-100%' },
  };

  const containerVariants = {
    animate: {
      transition: {
        staggerChildren: 0.15,
        repeat: Infinity,
        repeatType: 'reverse',
      },
    },
  };

  return (
    <motion.div
      className="flex items-center justify-start gap-3 p-4"
      variants={bubbleVariants}
      initial="hidden"
      animate="visible"
    >
      <div className="relative flex-shrink-0">
        <img src="https://placehold.co/40x40/EBF0F4/7C8490?text=A&font=sans" alt="Agent Avatar" className="w-10 h-10 rounded-full" />
      </div>
      <motion.div
        className="flex items-center justify-center gap-1 px-4 py-3 h-10 bg-muted rounded-2xl rounded-bl-none"
        variants={containerVariants}
        initial="initial"
        animate="animate"
      >
        <motion.span className="block w-2 h-2 bg-muted-foreground rounded-full" variants={dotVariants} />
        <motion.span className="block w-2 h-2 bg-muted-foreground rounded-full" variants={dotVariants} />
        <motion.span className="block w-2 h-2 bg-muted-foreground rounded-full" variants={dotVariants} />
      </motion.div>
    </motion.div>
  );
}

// This is a shared animation variant, assuming it's used in MessageItem as well.
// If not, it should be defined locally or imported from a shared file.
const bubbleVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};


export default TypingIndicator;