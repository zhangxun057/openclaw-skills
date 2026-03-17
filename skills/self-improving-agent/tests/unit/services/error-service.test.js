/**
 * Error Service Tests
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const os = require('os');

const {
  generateErrorId,
  ensureErrorsFile,
  getNextErrorSequence,
  detectErrors,
  logError,
  readErrors,
  DEFAULT_LEARNINGS_DIR,
  ERRORS_FILE,
} = require('../../../src/services/error-service');

describe('error-service', () => {
  let tempDir;

  before(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'error-test-'));
  });

  after(() => {
    if (tempDir && fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  describe('generateErrorId', () => {
    it('should generate ID with default date and sequence', () => {
      const id = generateErrorId();
      assert.ok(id.startsWith('ERR-'));
      assert.ok(/ERR-\d{8}-\d{3}/.test(id));
    });

    it('should generate ID with specific date', () => {
      const date = new Date('2026-03-05');
      const id = generateErrorId(date, 1);
      assert.strictEqual(id, 'ERR-20260305-001');
    });

    it('should pad sequence number to 3 digits', () => {
      const date = new Date('2026-03-05');
      assert.strictEqual(generateErrorId(date, 1), 'ERR-20260305-001');
      assert.strictEqual(generateErrorId(date, 10), 'ERR-20260305-010');
      assert.strictEqual(generateErrorId(date, 100), 'ERR-20260305-100');
    });
  });

  describe('ensureErrorsFile', () => {
    it('should create errors file if it does not exist', () => {
      const baseDir = path.join(tempDir, 'test1');
      const errorsFile = ensureErrorsFile(baseDir);
      
      assert.ok(errorsFile.endsWith(ERRORS_FILE));
      assert.ok(fs.existsSync(path.dirname(errorsFile)));
    });

    it('should return existing file path without error', () => {
      const baseDir = path.join(tempDir, 'test2');
      const errorsFile1 = ensureErrorsFile(baseDir);
      const errorsFile2 = ensureErrorsFile(baseDir);
      
      assert.strictEqual(errorsFile1, errorsFile2);
    });
  });

  describe('getNextErrorSequence', () => {
    it('should return 1 for non-existent file', () => {
      const baseDir = path.join(tempDir, 'test3');
      const errorsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, ERRORS_FILE);
      const seq = getNextErrorSequence(errorsFile);
      assert.strictEqual(seq, 1);
    });

    it('should return next sequence based on existing entries', () => {
      const baseDir = path.join(tempDir, 'test4');
      const errorsFile = ensureErrorsFile(baseDir);
      
      fs.writeFileSync(errorsFile, `
### ERR-20260305-001
Test error
---
### ERR-20260305-003
Another error
---
`);
      
      const seq = getNextErrorSequence(errorsFile);
      assert.strictEqual(seq, 4);
    });
  });

  describe('detectErrors', () => {
    it('should detect error in output', () => {
      assert.strictEqual(detectErrors('Something failed'), true);
      assert.strictEqual(detectErrors('Error: Connection refused'), true);
      assert.strictEqual(detectErrors('npm ERR! code ENOENT'), true);
    });

    it('should return false for clean output', () => {
      assert.strictEqual(detectErrors('Everything completed successfully'), false);
      assert.strictEqual(detectErrors('Build successful'), false);
    });

    it('should handle empty/null input', () => {
      assert.strictEqual(detectErrors(''), false);
      assert.strictEqual(detectErrors(null), false);
      assert.strictEqual(detectErrors(undefined), false);
    });
  });

  describe('logError', () => {
    it('should log an error entry successfully', () => {
      const baseDir = path.join(tempDir, 'test5');
      const error = {
        command: 'npm install',
        error: 'Module not found',
      };
      
      const result = logError(error, baseDir);
      
      assert.strictEqual(result.success, true);
      assert.ok(result.id);
      assert.ok(result.id.startsWith('ERR-'));
      assert.ok(fs.existsSync(result.file));
    });

    it('should append multiple errors to the same file', () => {
      const baseDir = path.join(tempDir, 'test6');
      
      logError({
        command: 'npm install',
        error: 'First error',
      }, baseDir);
      
      logError({
        command: 'npm test',
        error: 'Second error',
      }, baseDir);
      
      const errorsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, ERRORS_FILE);
      const content = fs.readFileSync(errorsFile, 'utf8');
      
      assert.ok(content.includes('First error'));
      assert.ok(content.includes('Second error'));
    });

    it('should include context in the entry', () => {
      const baseDir = path.join(tempDir, 'test7');
      
      logError({
        command: 'npm test',
        error: 'Test failed',
        context: 'Running on Node 18',
      }, baseDir);
      
      const errorsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, ERRORS_FILE);
      const content = fs.readFileSync(errorsFile, 'utf8');
      
      assert.ok(content.includes('Context:'));
      assert.ok(content.includes('Running on Node 18'));
    });

    it('should include resolution in the entry', () => {
      const baseDir = path.join(tempDir, 'test8');
      
      logError({
        command: 'npm test',
        error: 'Test failed',
        resolution: 'Update jest config',
      }, baseDir);
      
      const errorsFile = path.join(baseDir, DEFAULT_LEARNINGS_DIR, ERRORS_FILE);
      const content = fs.readFileSync(errorsFile, 'utf8');
      
      assert.ok(content.includes('Resolution:'));
      assert.ok(content.includes('Update jest config'));
    });

    it('should return error on failure', () => {
      // Create a file where we expect a directory to test error handling
      const badDir = path.join(tempDir, 'not-a-dir');
      fs.writeFileSync(badDir, 'file content');
      
      const result = logError({
        command: 'test',
        error: 'test',
      }, badDir);
      
      assert.strictEqual(result.success, false);
      assert.ok(result.error);
    });
  });

  describe('readErrors', () => {
    it('should return empty array if no errors file', () => {
      const baseDir = path.join(tempDir, 'test9');
      const errors = readErrors(baseDir);
      assert.deepStrictEqual(errors, []);
    });

    it('should read errors from file', () => {
      const baseDir = path.join(tempDir, 'test10');
      const errorsFile = ensureErrorsFile(baseDir);
      
      fs.writeFileSync(errorsFile, `
### ERR-20260305-001
Test error
---
### ERR-20260305-002
Another error
---
`);
      
      const errors = readErrors(baseDir);
      assert.strictEqual(errors.length, 2);
      assert.ok(errors[0].raw.includes('Test error'));
      assert.ok(errors[1].raw.includes('Another error'));
    });
  });
});
