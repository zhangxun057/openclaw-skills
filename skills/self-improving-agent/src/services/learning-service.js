/**
 * Learning Service
 * 
 * Handles learning capture logic and file operations.
 */

const fs = require('fs');
const path = require('path');
const { renderLearningEntry } = require('../utils/template-renderer');

const DEFAULT_LEARNINGS_DIR = '.learnings';
const LEARNINGS_FILE = 'LEARNINGS.md';

/**
 * Generate a learning ID
 * @param {Date} date - Date for the ID (defaults to now)
 * @param {number} sequence - Sequence number
 * @returns {string} Learning ID in format LRN-YYYYMMDD-XXX
 */
function generateLearningId(date = new Date(), sequence = 1) {
  const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
  const seqStr = sequence.toString().padStart(3, '0');
  return `LRN-${dateStr}-${seqStr}`;
}

/**
 * Ensure the learnings directory exists
 * @param {string} baseDir - Base directory (defaults to current working directory)
 * @returns {string} Path to learnings directory
 */
function ensureLearningsDir(baseDir = process.cwd()) {
  const learningsDir = path.join(baseDir, DEFAULT_LEARNINGS_DIR);
  if (!fs.existsSync(learningsDir)) {
    fs.mkdirSync(learningsDir, { recursive: true });
  }
  return learningsDir;
}

/**
 * Get the next sequence number for learning IDs
 * @param {string} learningsDir - Path to learnings directory
 * @returns {number} Next sequence number
 */
function getNextSequence(learningsDir) {
  const learningsFile = path.join(learningsDir, LEARNINGS_FILE);
  
  if (!fs.existsSync(learningsFile)) {
    return 1;
  }
  
  const content = fs.readFileSync(learningsFile, 'utf8');
  const matches = content.match(/### LRN-\d{8}-(\d{3})/g);
  
  if (!matches || matches.length === 0) {
    return 1;
  }
  
  const numbers = matches.map(m => {
    const match = m.match(/LRN-\d{8}-(\d{3})/);
    return match ? parseInt(match[1], 10) : 0;
  });
  
  return Math.max(...numbers) + 1;
}

/**
 * Capture a learning entry
 * @param {Object} learning - Learning data
 * @param {string} baseDir - Base directory
 * @returns {Object} Result with success status and learning ID
 */
function captureLearning(learning, baseDir = process.cwd()) {
  try {
    const learningsDir = ensureLearningsDir(baseDir);
    const learningsFile = path.join(learningsDir, LEARNINGS_FILE);
    
    const sequence = getNextSequence(learningsDir);
    const learningId = generateLearningId(new Date(), sequence);
    
    const entry = renderLearningEntry({
      ...learning,
      id: learningId,
      date: new Date().toISOString().slice(0, 10),
    });
    
    // Append to file (create if doesn't exist)
    fs.appendFileSync(learningsFile, entry + '\n');
    
    return {
      success: true,
      id: learningId,
      file: learningsFile,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Read all learnings
 * @param {string} baseDir - Base directory
 * @returns {Array} Array of learning entries
 */
function readLearnings(baseDir = process.cwd()) {
  const learningsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, LEARNINGS_FILE);
  
  if (!fs.existsSync(learningsFile)) {
    return [];
  }
  
  const content = fs.readFileSync(learningsFile, 'utf8');
  // Simple parsing - could be enhanced with proper markdown parsing
  const entries = content.split('---').filter(e => e.trim());
  
  return entries.map(entry => ({
    raw: entry.trim(),
    // TODO: Parse into structured object
  }));
}

module.exports = {
  generateLearningId,
  ensureLearningsDir,
  getNextSequence,
  captureLearning,
  readLearnings,
  DEFAULT_LEARNINGS_DIR,
  LEARNINGS_FILE,
};
