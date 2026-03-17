/**
 * CLI Integration Tests
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CLI_PATH = path.join(__dirname, '../../src/cli.js');

describe('cli integration', () => {
  let tempDir;
  let originalCwd;

  before(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cli-test-'));
    originalCwd = process.cwd();
  });

  after(() => {
    if (tempDir && fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  function runCli(args, cwd = tempDir) {
    return new Promise((resolve, reject) => {
      const child = spawn('node', [CLI_PATH, ...args], {
        cwd,
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      child.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', (code) => {
        resolve({ code, stdout, stderr });
      });

      child.on('error', reject);
    });
  }

  describe('help command', () => {
    it('should show usage for --help', async () => {
      const { code, stdout } = await runCli(['--help']);
      assert.strictEqual(code, 0);
      assert.ok(stdout.includes('Usage:'));
      assert.ok(stdout.includes('learning'));
      assert.ok(stdout.includes('error'));
      assert.ok(stdout.includes('extract'));
    });

    it('should show usage for no command', async () => {
      const { code, stdout } = await runCli([]);
      assert.strictEqual(code, 0);
      assert.ok(stdout.includes('Usage:'));
    });
  });

  describe('learning command', () => {
    it('should require title', async () => {
      const { code, stderr } = await runCli(['learning', '--description', 'Test']);
      assert.notStrictEqual(code, 0);
      assert.ok(stderr.includes('title'));
    });

    it('should require description', async () => {
      const { code, stderr } = await runCli(['learning', '--title', 'Test']);
      assert.notStrictEqual(code, 0);
      assert.ok(stderr.includes('description'));
    });

    it('should capture learning successfully', async () => {
      const { code, stdout } = await runCli([
        'learning',
        '--title', 'Test Learning',
        '--category', 'best_practice',
        '--description', 'This is a test'
      ]);
      
      assert.strictEqual(code, 0);
      assert.ok(stdout.includes('Learning captured:'));
      assert.ok(stdout.includes('LRN-'));
    });
  });

  describe('error command', () => {
    it('should require command', async () => {
      const { code, stderr } = await runCli(['error', '--error', 'Test']);
      assert.notStrictEqual(code, 0);
      assert.ok(stderr.includes('command'));
    });

    it('should require error message', async () => {
      const { code, stderr } = await runCli(['error', '--command', 'npm test']);
      assert.notStrictEqual(code, 0);
      assert.ok(stderr.includes('error'));
    });

    it('should log error successfully', async () => {
      const { code, stdout } = await runCli([
        'error',
        '--command', 'npm install',
        '--error', 'Module not found'
      ]);
      
      assert.strictEqual(code, 0);
      assert.ok(stdout.includes('Error logged:'));
      assert.ok(stdout.includes('ERR-'));
    });
  });

  describe('extract command', () => {
    it('should require skill name', async () => {
      const { code, stderr } = await runCli(['extract']);
      assert.notStrictEqual(code, 0);
      assert.ok(stderr.includes('name'));
    });

    it('should validate skill name format', async () => {
      const { code, stderr } = await runCli(['extract', '--name', 'InvalidName']);
      assert.notStrictEqual(code, 0);
      assert.ok(stderr.includes('Invalid'));
    });

    it('should extract skill in dry-run mode', async () => {
      const { code, stdout } = await runCli([
        'extract',
        '--name', 'test-skill',
        '--dry-run'
      ]);
      
      assert.strictEqual(code, 0);
      assert.ok(stdout.includes('Dry run'));
      assert.ok(stdout.includes('test-skill'));
    });
  });

  describe('activator command', () => {
    it('should output activator reminder', async () => {
      const { code, stdout } = await runCli(['activator']);
      assert.strictEqual(code, 0);
      assert.ok(stdout.includes('self-improvement-reminder'));
    });
  });

  describe('error-hook command', () => {
    it('should handle no error in environment', async () => {
      const { code, stdout } = await runCli(['error-hook']);
      assert.strictEqual(code, 0);
      assert.strictEqual(stdout.trim(), '');
    });
  });

  describe('unknown command', () => {
    it('should show error for unknown command', async () => {
      const { code, stderr } = await runCli(['unknown']);
      assert.notStrictEqual(code, 0);
      assert.ok(stderr.includes('Unknown command'));
    });
  });
});
