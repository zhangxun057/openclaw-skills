/**
 * Learning Service Tests
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const os = require('os');

const {
  generateLearningId,
  ensureLearningsDir,
  getNextSequence,
  captureLearning,
  readLearnings,
  DEFAULT_LEARNINGS_DIR,
  LEARNINGS_FILE,
} = require('../../../src/services/learning-service');

describe('learning-service', () => {
  let tempDir;

  before(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'learning-test-'));
  });

  after(() => {
    if (tempDir && fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  describe('generateLearningId', () => {
    it('should generate ID with default date and sequence', () => {
      const id = generateLearningId();
      assert.ok(id.startsWith('LRN-'));
      assert.ok(/LRN-\d{8}-\d{3}/.test(id));
    });

    it('should generate ID with specific date', () => {
      const date = new Date('2026-03-05');
      const id = generateLearningId(date, 1);
      assert.strictEqual(id, 'LRN-20260305-001');
    });

    it('should pad sequence number to 3 digits', () => {
      const date = new Date('2026-03-05');
      assert.strictEqual(generateLearningId(date, 1), 'LRN-20260305-001');
      assert.strictEqual(generateLearningId(date, 10), 'LRN-20260305-010');
      assert.strictEqual(generateLearningId(date, 100), 'LRN-20260305-100');
    });
  });

  describe('ensureLearningsDir', () => {
    it('should create learnings directory if it does not exist', () => {
      const baseDir = path.join(tempDir, 'test1');
      const learningsDir = ensureLearningsDir(baseDir);
      
      assert.strictEqual(learningsDir, path.join(baseDir, DEFAULT_LEARNINGS_DIR));
      assert.ok(fs.existsSync(learningsDir));
    });

    it('should return existing directory path without error', () => {
      const baseDir = path.join(tempDir, 'test2');
      const learningsDir1 = ensureLearningsDir(baseDir);
      const learningsDir2 = ensureLearningsDir(baseDir);
      
      assert.strictEqual(learningsDir1, learningsDir2);
      assert.ok(fs.existsSync(learningsDir2));
    });

    it('should use current working directory by default', () => {
      const learningsDir = ensureLearningsDir();
      assert.ok(learningsDir.endsWith(DEFAULT_LEARNINGS_DIR));
    });
  });

  describe('getNextSequence', () => {
    it('should return 1 for empty directory', () => {
      const baseDir = path.join(tempDir, 'test3');
      const learningsDir = ensureLearningsDir(baseDir);
      const seq = getNextSequence(learningsDir);
      assert.strictEqual(seq, 1);
    });

    it('should return 1 if file does not exist', () => {
      const baseDir = path.join(tempDir, 'test4');
      fs.mkdirSync(path.join(baseDir, DEFAULT_LEARNINGS_DIR), { recursive: true });
      const seq = getNextSequence(path.join(baseDir, DEFAULT_LEARNINGS_DIR));
      assert.strictEqual(seq, 1);
    });

    it('should return next sequence based on existing entries', () => {
      const baseDir = path.join(tempDir, 'test5');
      const learningsDir = ensureLearningsDir(baseDir);
      const learningsFile = path.join(learningsDir, LEARNINGS_FILE);
      
      fs.writeFileSync(learningsFile, `
### LRN-20260305-001
Test entry
---
### LRN-20260305-002
Another entry
---
### LRN-20260305-005
Out of sequence
---
`);
      
      const seq = getNextSequence(learningsDir);
      assert.strictEqual(seq, 6);
    });
  });

  describe('captureLearning', () => {
    it('should capture a learning entry successfully', () => {
      const baseDir = path.join(tempDir, 'test6');
      const learning = {
        title: 'Test Learning',
        category: 'best_practice',
        description: 'This is a test learning',
      };
      
      const result = captureLearning(learning, baseDir);
      
      assert.strictEqual(result.success, true);
      assert.ok(result.id);
      assert.ok(result.id.startsWith('LRN-'));
      assert.ok(fs.existsSync(result.file));
    });

    it('should append multiple learnings to the same file', () => {
      const baseDir = path.join(tempDir, 'test7');
      
      captureLearning({
        title: 'First Learning',
        category: 'best_practice',
        description: 'First',
      }, baseDir);
      
      captureLearning({
        title: 'Second Learning',
        category: 'correction',
        description: 'Second',
      }, baseDir);
      
      const learningsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, LEARNINGS_FILE);
      const content = fs.readFileSync(learningsFile, 'utf8');
      
      assert.ok(content.includes('First Learning'));
      assert.ok(content.includes('Second Learning'));
    });

    it('should include tags in the entry', () => {
      const baseDir = path.join(tempDir, 'test8');
      
      captureLearning({
        title: 'Tagged Learning',
        category: 'best_practice',
        description: 'With tags',
        tags: ['docker', 'fix'],
      }, baseDir);
      
      const learningsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, LEARNINGS_FILE);
      const content = fs.readFileSync(learningsFile, 'utf8');
      
      assert.ok(content.includes('docker, fix'));
    });

    it('should include solution in the entry', () => {
      const baseDir = path.join(tempDir, 'test9');
      
      captureLearning({
        title: 'Solved Learning',
        category: 'best_practice',
        description: 'Problem description',
        solution: 'The solution',
      }, baseDir);
      
      const learningsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, LEARNINGS_FILE);
      const content = fs.readFileSync(learningsFile, 'utf8');
      
      assert.ok(content.includes('Solution:'));
      assert.ok(content.includes('The solution'));
    });

    it('should return error on failure', () => {
      // Create a file where we expect a directory to test error handling
      const badDir = path.join(tempDir, 'not-a-dir');
      fs.writeFileSync(badDir, 'file content');
      
      const result = captureLearning({
        title: 'Test',
        category: 'best_practice',
        description: 'Test',
      }, badDir);
      
      assert.strictEqual(result.success, false);
      assert.ok(result.error);
    });
  });

  describe('readLearnings', () => {
    it('should return empty array if no learnings file', () => {
      const baseDir = path.join(tempDir, 'test10');
      const learnings = readLearnings(baseDir);
      assert.deepStrictEqual(learnings, []);
    });

    it('should read learnings from file', () => {
      const baseDir = path.join(tempDir, 'test11');
      const learningsDir = ensureLearningsDir(baseDir);
      const learningsFile = path.join(learningsDir, LEARNINGS_FILE);
      
      fs.writeFileSync(learningsFile, `
### LRN-20260305-001
Test entry
---
### LRN-20260305-002
Another entry
---
`);
      
      const learnings = readLearnings(baseDir);
      assert.strictEqual(learnings.length, 2);
      assert.ok(learnings[0].raw.includes('Test entry'));
      assert.ok(learnings[1].raw.includes('Another entry'));
    });
  });
});
