/**
 * Template Renderer Tests
 */

const { describe, it } = require('node:test');
const assert = require('node:assert');
const {
  getLearningReminder,
  getActivatorReminder,
  getErrorReminder,
  renderLearningEntry,
  renderErrorEntry,
} = require('../../../src/utils/template-renderer');

describe('template-renderer', () => {
  describe('getLearningReminder', () => {
    it('should return non-empty string', () => {
      const reminder = getLearningReminder();
      assert.ok(reminder.length > 0);
      assert.ok(reminder.includes('Self-Improvement Reminder'));
    });

    it('should mention learning files', () => {
      const reminder = getLearningReminder();
      assert.ok(reminder.includes('LEARNINGS.md'));
      assert.ok(reminder.includes('ERRORS.md'));
      assert.ok(reminder.includes('FEATURE_REQUESTS.md'));
    });
  });

  describe('getActivatorReminder', () => {
    it('should return non-empty string', () => {
      const reminder = getActivatorReminder();
      assert.ok(reminder.length > 0);
      assert.ok(reminder.includes('self-improvement-reminder'));
    });

    it('should mention extractable knowledge', () => {
      const reminder = getActivatorReminder();
      assert.ok(reminder.includes('extractable knowledge'));
    });
  });

  describe('getErrorReminder', () => {
    it('should return non-empty string', () => {
      const reminder = getErrorReminder();
      assert.ok(reminder.length > 0);
      assert.ok(reminder.includes('error-detected'));
    });

    it('should mention error logging', () => {
      const reminder = getErrorReminder();
      assert.ok(reminder.includes('ERRORS.md'));
    });
  });

  describe('renderLearningEntry', () => {
    it('should render basic learning entry', () => {
      const learning = {
        id: 'LRN-20260305-001',
        date: '2026-03-05',
        title: 'Test Learning',
        category: 'best_practice',
        description: 'Test description',
      };
      
      const entry = renderLearningEntry(learning);
      assert.ok(entry.includes('### LRN-20260305-001'));
      assert.ok(entry.includes('Test Learning'));
      assert.ok(entry.includes('best_practice'));
      assert.ok(entry.includes('Test description'));
    });

    it('should include tags when provided', () => {
      const learning = {
        id: 'LRN-20260305-001',
        date: '2026-03-05',
        title: 'Test',
        category: 'correction',
        description: 'Desc',
        tags: ['docker', 'fix'],
      };
      
      const entry = renderLearningEntry(learning);
      assert.ok(entry.includes('docker, fix'));
    });

    it('should include solution when provided', () => {
      const learning = {
        id: 'LRN-20260305-001',
        date: '2026-03-05',
        title: 'Test',
        category: 'best_practice',
        description: 'Desc',
        solution: 'The solution',
      };
      
      const entry = renderLearningEntry(learning);
      assert.ok(entry.includes('Solution:'));
      assert.ok(entry.includes('The solution'));
    });
  });

  describe('renderErrorEntry', () => {
    it('should render basic error entry', () => {
      const error = {
        id: 'ERR-20260305-001',
        date: '2026-03-05',
        command: 'npm install',
        error: 'Module not found',
      };
      
      const entry = renderErrorEntry(error);
      assert.ok(entry.includes('### ERR-20260305-001'));
      assert.ok(entry.includes('npm install'));
      assert.ok(entry.includes('Module not found'));
    });

    it('should include context when provided', () => {
      const error = {
        id: 'ERR-20260305-001',
        date: '2026-03-05',
        command: 'npm test',
        error: 'Test failed',
        context: 'Running on Node 18',
      };
      
      const entry = renderErrorEntry(error);
      assert.ok(entry.includes('Context:'));
      assert.ok(entry.includes('Running on Node 18'));
    });

    it('should include resolution when provided', () => {
      const error = {
        id: 'ERR-20260305-001',
        date: '2026-03-05',
        command: 'npm test',
        error: 'Test failed',
        resolution: 'Update jest config',
      };
      
      const entry = renderErrorEntry(error);
      assert.ok(entry.includes('Resolution:'));
      assert.ok(entry.includes('Update jest config'));
    });
  });
});
