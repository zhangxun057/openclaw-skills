/**
 * Activator Hook Tests
 */

const { describe, it } = require('node:test');
const assert = require('node:assert');

const {
  handleActivator,
  runActivator,
  REMINDER_CONTENT,
} = require('../../../src/hooks/activator-hook');

describe('activator-hook', () => {
  describe('handleActivator', () => {
    it('should return reminder content', () => {
      const result = handleActivator();
      assert.ok(typeof result === 'string');
      assert.ok(result.length > 0);
    });

    it('should contain self-improvement-reminder tag', () => {
      const result = handleActivator();
      assert.ok(result.includes('self-improvement-reminder'));
    });

    it('should mention extractable knowledge', () => {
      const result = handleActivator();
      assert.ok(result.includes('extractable knowledge'));
    });

    it('should return consistent content', () => {
      const result1 = handleActivator();
      const result2 = handleActivator();
      assert.strictEqual(result1, result2);
    });
  });

  describe('REMINDER_CONTENT', () => {
    it('should be a non-empty string', () => {
      assert.ok(typeof REMINDER_CONTENT === 'string');
      assert.ok(REMINDER_CONTENT.length > 0);
    });

    it('should contain XML-like tags', () => {
      assert.ok(REMINDER_CONTENT.includes('<self-improvement-reminder>'));
      assert.ok(REMINDER_CONTENT.includes('</self-improvement-reminder>'));
    });

    it('should mention .learnings/', () => {
      assert.ok(REMINDER_CONTENT.includes('.learnings/'));
    });
  });
});
