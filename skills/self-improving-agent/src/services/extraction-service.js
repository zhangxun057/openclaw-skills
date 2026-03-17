/**
 * Extraction Service
 * 
 * Handles skill extraction from learnings.
 */

const fs = require('fs');
const path = require('path');

const SKILL_TEMPLATE = `---
name: {{skillName}}
description: "[TODO: Add a concise description of what this skill does and when to use it]"
---

# {{skillTitle}}

[TODO: Brief introduction explaining the skill's purpose]

## Quick Reference

| Situation | Action |
|-----------|--------|
| [Trigger condition] | [What to do] |

## Usage

[TODO: Detailed usage instructions]

## Examples

[TODO: Add concrete examples]

## Source Learning

This skill was extracted from a learning entry.
- Learning ID: [TODO: Add original learning ID]
- Original File: .learnings/LEARNINGS.md
`;

/**
 * Validate skill name format
 * @param {string} name - Skill name to validate
 * @returns {boolean} True if valid
 */
function isValidSkillName(name) {
  return /^[a-z0-9]+(-[a-z0-9]+)*$/.test(name);
}

/**
 * Convert skill name to title format
 * @param {string} name - Skill name (e.g., "docker-fixes")
 * @returns {string} Title format (e.g., "Docker Fixes")
 */
function skillNameToTitle(name) {
  return name
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Validate output path for security
 * @param {string} outputPath - Path to validate
 * @returns {Object} Validation result
 */
function validateOutputPath(outputPath) {
  // Must be relative path
  if (path.isAbsolute(outputPath)) {
    return {
      valid: false,
      error: 'Output directory must be a relative path',
    };
  }
  
  // Must not contain .. segments
  if (outputPath.includes('..')) {
    return {
      valid: false,
      error: 'Output directory cannot include ".." path segments',
    };
  }
  
  return { valid: true };
}

/**
 * Generate skill scaffold content
 * @param {string} skillName - Name of the skill
 * @returns {string} SKILL.md content
 */
function generateSkillScaffold(skillName) {
  const title = skillNameToTitle(skillName);
  return SKILL_TEMPLATE
    .replace(/{{skillName}}/g, skillName)
    .replace(/{{skillTitle}}/g, title);
}

/**
 * Extract a skill from a learning entry
 * @param {Object} options - Extraction options
 * @param {string} options.skillName - Name for the new skill
 * @param {string} options.outputDir - Output directory (relative)
 * @param {boolean} options.dryRun - If true, don't create files
 * @returns {Object} Extraction result
 */
function extractSkill({ skillName, outputDir = './skills', dryRun = false }) {
  // Validate skill name
  if (!skillName) {
    return {
      success: false,
      error: 'Skill name is required',
    };
  }
  
  if (!isValidSkillName(skillName)) {
    return {
      success: false,
      error: 'Invalid skill name format. Use lowercase letters, numbers, and hyphens only.',
    };
  }
  
  // Validate output path
  const pathValidation = validateOutputPath(outputDir);
  if (!pathValidation.valid) {
    return {
      success: false,
      error: pathValidation.error,
    };
  }
  
  const normalizedOutputDir = outputDir.startsWith('./') 
    ? outputDir 
    : `./${outputDir}`;
  const skillPath = path.join(normalizedOutputDir, skillName);
  const skillFile = path.join(skillPath, 'SKILL.md');
  
  // Check if skill already exists
  if (!dryRun && fs.existsSync(skillPath)) {
    return {
      success: false,
      error: `Skill already exists: ${skillPath}`,
    };
  }
  
  const content = generateSkillScaffold(skillName);
  
  if (dryRun) {
    return {
      success: true,
      dryRun: true,
      skillPath,
      skillFile,
      content,
    };
  }
  
  // Create skill directory and file
  try {
    fs.mkdirSync(skillPath, { recursive: true });
    fs.writeFileSync(skillFile, content);
    
    return {
      success: true,
      skillPath,
      skillFile,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

module.exports = {
  isValidSkillName,
  skillNameToTitle,
  validateOutputPath,
  generateSkillScaffold,
  extractSkill,
  SKILL_TEMPLATE,
};
