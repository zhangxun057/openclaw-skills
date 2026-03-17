/**
 * Extraction Service Tests
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const os = require('os');

const {
  isValidSkillName,
  skillNameToTitle,
  validateOutputPath,
  generateSkillScaffold,
  extractSkill,
  SKILL_TEMPLATE,
} = require('../../../src/services/extraction-service');

describe('extraction-service', () => {
  let tempDir;
  let originalCwd;

  before(() => {
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'extraction-test-'));
    originalCwd = process.cwd();
    process.chdir(tempDir);
  });

  after(() => {
    process.chdir(originalCwd);
    if (tempDir && fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  describe('isValidSkillName', () => {
    it('should accept valid skill names', () => {
      assert.strictEqual(isValidSkillName('docker-fixes'), true);
      assert.strictEqual(isValidSkillName('my-skill'), true);
      assert.strictEqual(isValidSkillName('skill123'), true);
      assert.strictEqual(isValidSkillName('a-b-c'), true);
      assert.strictEqual(isValidSkillName('simple'), true);
    });

    it('should reject invalid skill names', () => {
      assert.strictEqual(isValidSkillName(''), false);
      assert.strictEqual(isValidSkillName('DockerFixes'), false); // uppercase
      assert.strictEqual(isValidSkillName('my_skill'), false); // underscore
      assert.strictEqual(isValidSkillName('my skill'), false); // space
      assert.strictEqual(isValidSkillName('-docker'), false); // starts with hyphen
      assert.strictEqual(isValidSkillName('docker-'), false); // ends with hyphen
      assert.strictEqual(isValidSkillName('my--skill'), false); // double hyphen
    });
  });

  describe('skillNameToTitle', () => {
    it('should convert kebab-case to Title Case', () => {
      assert.strictEqual(skillNameToTitle('docker-fixes'), 'Docker Fixes');
      assert.strictEqual(skillNameToTitle('my-skill'), 'My Skill');
      assert.strictEqual(skillNameToTitle('simple'), 'Simple');
    });

    it('should handle multiple words', () => {
      assert.strictEqual(skillNameToTitle('a-b-c-d'), 'A B C D');
    });
  });

  describe('validateOutputPath', () => {
    it('should accept valid relative paths', () => {
      const result = validateOutputPath('./skills');
      assert.strictEqual(result.valid, true);
      
      const result2 = validateOutputPath('skills');
      assert.strictEqual(result2.valid, true);
      
      const result3 = validateOutputPath('my/skills/dir');
      assert.strictEqual(result3.valid, true);
    });

    it('should reject absolute paths', () => {
      const result = validateOutputPath('/absolute/path');
      assert.strictEqual(result.valid, false);
      assert.ok(result.error.includes('relative'));
    });

    it('should reject paths with ..', () => {
      const result = validateOutputPath('../skills');
      assert.strictEqual(result.valid, false);
      assert.ok(result.error.includes('..'));
      
      const result2 = validateOutputPath('skills/../other');
      assert.strictEqual(result2.valid, false);
    });
  });

  describe('generateSkillScaffold', () => {
    it('should generate scaffold with skill name', () => {
      const content = generateSkillScaffold('docker-fixes');
      assert.ok(content.includes('name: docker-fixes'));
    });

    it('should generate scaffold with title', () => {
      const content = generateSkillScaffold('docker-fixes');
      assert.ok(content.includes('# Docker Fixes'));
    });

    it('should include template placeholders', () => {
      const content = generateSkillScaffold('test-skill');
      assert.ok(content.includes('[TODO:'));
      assert.ok(content.includes('description:'));
    });
  });

  describe('extractSkill', () => {
    it('should return error if skill name is missing', () => {
      const result = extractSkill({});
      assert.strictEqual(result.success, false);
      assert.ok(result.error.includes('required'));
    });

    it('should return error for invalid skill name', () => {
      const result = extractSkill({ skillName: 'InvalidName' });
      assert.strictEqual(result.success, false);
      assert.ok(result.error.includes('Invalid'));
    });

    it('should return error for absolute output path', () => {
      const result = extractSkill({ 
        skillName: 'test-skill',
        outputDir: '/absolute/path'
      });
      assert.strictEqual(result.success, false);
      assert.ok(result.error.includes('relative'));
    });

    it('should return error for path with ..', () => {
      const result = extractSkill({ 
        skillName: 'test-skill',
        outputDir: '../skills'
      });
      assert.strictEqual(result.success, false);
      assert.ok(result.error.includes('..'));
    });

    it('should create skill in dry-run mode without files', () => {
      const result = extractSkill({ 
        skillName: 'test-skill',
        dryRun: true
      });
      
      assert.strictEqual(result.success, true);
      assert.strictEqual(result.dryRun, true);
      assert.ok(result.skillPath);
      assert.ok(result.skillFile);
      assert.ok(result.content);
      
      // Verify no files were created
      assert.strictEqual(fs.existsSync(result.skillPath), false);
    });

    it('should create skill directory and file', () => {
      const result = extractSkill({ 
        skillName: 'my-test-skill',
        outputDir: './skills'
      });
      
      assert.strictEqual(result.success, true);
      assert.ok(fs.existsSync(result.skillPath));
      assert.ok(fs.existsSync(result.skillFile));
      
      const content = fs.readFileSync(result.skillFile, 'utf8');
      assert.ok(content.includes('name: my-test-skill'));
    });

    it('should return error if skill already exists', () => {
      // First extraction
      extractSkill({ skillName: 'existing-skill' });
      
      // Second extraction should fail
      const result = extractSkill({ skillName: 'existing-skill' });
      assert.strictEqual(result.success, false);
      assert.ok(result.error.includes('already exists'));
    });

    it('should create skill in temp directory', () => {
      // Use a relative path from cwd
      const result = extractSkill({ 
        skillName: 'default-dir-skill',
        outputDir: path.relative(process.cwd(), tempDir)
      });
      
      assert.strictEqual(result.success, true);
      // Verify the skill was created
      assert.ok(fs.existsSync(result.skillPath));
      assert.ok(fs.existsSync(result.skillFile));
    });

    it('should create skill in subdirectory', () => {
      const subDir = path.join(tempDir, 'custom');
      fs.mkdirSync(subDir, { recursive: true });
      
      const result = extractSkill({ 
        skillName: 'normalized-skill',
        outputDir: path.relative(process.cwd(), subDir)
      });
      
      assert.strictEqual(result.success, true);
      // Verify the skill was created in the subdirectory
      assert.ok(fs.existsSync(result.skillPath));
      assert.ok(result.skillPath.includes('normalized-skill'));
    });
  });

  describe('SKILL_TEMPLATE', () => {
    it('should be a non-empty string', () => {
      assert.ok(typeof SKILL_TEMPLATE === 'string');
      assert.ok(SKILL_TEMPLATE.length > 0);
    });

    it('should contain required placeholders', () => {
      assert.ok(SKILL_TEMPLATE.includes('{{skillName}}'));
      assert.ok(SKILL_TEMPLATE.includes('{{skillTitle}}'));
    });

    it('should contain skill structure elements', () => {
      assert.ok(SKILL_TEMPLATE.includes('---'));
      assert.ok(SKILL_TEMPLATE.includes('name:'));
      assert.ok(SKILL_TEMPLATE.includes('description:'));
    });
  });
});
