#!/usr/bin/env node

// ============================================================================
// HTML Generator - AI 生图核心脚本
// 调用 Seedream API 生成图片，上传到文件服务器
// ============================================================================

import { readFile, writeFile } from 'fs/promises';
import { execSync } from 'child_process';
import { tmpdir } from 'os';
import { join } from 'path';

// -- 配置 ---------------------------------------------------------------

const CONFIG = {
  // Seedream API
  SEEDREAM_URL: 'https://ark.cn-beijing.volces.com/api/v3/images/generations',
  SEEDREAM_KEY: 'd155ace0-ee4d-42b1-936e-4a16d2623c89',
  MODEL: 'doubao-seedream-5-0-260128',
  
  // 文件服务器
  FILE_SERVER: 'https://mjy.gzlex.com:8095/api/sse/file/upload',
  FILE_TOKEN: 'ampzOmhjenFAMTIz',
};

// -- 工具函数 -----------------------------------------------------------

function generateImage(prompt, size = '2048x2048') {
  console.log(`🎨 生成图片: ${prompt.substring(0, 50)}...`);
  
  const cmd = `curl -s -X POST "${CONFIG.SEEDREAM_URL}" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${CONFIG.SEEDREAM_KEY}" \\
    -d '${JSON.stringify({
      model: CONFIG.MODEL,
      prompt: prompt,
      sequential_image_generation: 'disabled',
      response_format: 'url',
      size: size,
      watermark: false
    })}'`;
  
  const result = execSync(cmd, { encoding: 'utf-8' });
  const data = JSON.parse(result);
  
  if (data.error) {
    throw new Error(`Seedream API error: ${data.error.message}`);
  }
  
  return data.data[0].url;
}

function uploadToFileServer(filePath) {
  console.log(`📤 上传到文件服务器: ${filePath}`);
  
  const cmd = `curl -s -X POST "${CONFIG.FILE_SERVER}" \\
    -H "Authorization: Bearer ${CONFIG.FILE_TOKEN}" \\
    -H "User-Agent: Apifox/1.0.0" \\
    -F "file=@${filePath}"`;
  
  const result = execSync(cmd, { encoding: 'utf-8' });
  const data = JSON.parse(result);
  
  if (data.code !== '0') {
    throw new Error(`Upload failed: ${result}`);
  }
  
  return data.data.fileUrl;
}

function downloadImage(url, outputPath) {
  console.log(`⬇️ 下载图片: ${url}`);
  
  const cmd = `curl -s -o "${outputPath}" "${url}"`;
  execSync(cmd, { encoding: 'utf-8' });
  
  return outputPath;
}

// -- 主程序 -----------------------------------------------------------

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'generate') {
    // 生成图片并上传
    const prompt = args[1] || args[--args];
    if (!prompt) {
      console.error('Usage: node html-gen.js generate "prompt text"');
      process.exit(1);
    }
    
    try {
      // 1. 生成图片
      const tempUrl = generateImage(prompt);
      console.log(`✅ Seedream: ${tempUrl}`);
      
      // 2. 下载到临时文件
      const tempPath = join(tmpdir(), `html-gen-${Date.now()}.jpg`);
      downloadImage(tempUrl, tempPath);
      
      // 3. 上传到文件服务器
      const permanentUrl = uploadToFileServer(tempPath);
      console.log(`✅ 永久链接: ${permanentUrl}`);
      
      console.log('\n📋 URL for HTML:');
      console.log(permanentUrl);
      
    } catch (err) {
      console.error('❌ Error:', err.message);
      process.exit(1);
    }
    
  } else if (command === 'upload') {
    // 仅上传文件
    const filePath = args[1];
    if (!filePath) {
      console.error('Usage: node html-gen.js upload /path/to/file');
      process.exit(1);
    }
    
    try {
      const url = uploadToFileServer(filePath);
      console.log(`✅ 永久链接: ${url}`);
    } catch (err) {
      console.error('❌ Error:', err.message);
      process.exit(1);
    }
    
  } else {
    console.log(`
HTML Generator - AI 生图脚本

Usage:
  node html-gen.js generate "prompt"     生成图片并上传
  node html-gen.js upload /path/to/file  仅上传文件

Examples:
  node html-gen.js generate "A premium Chinese baijiu bottle on dark table"
  node html-gen.js upload /tmp/image.jpg
`);
  }
}

main();
