#!/usr/bin/env node
/**
 * cron-rescue: session-analyzer
 * 解析隔离会话 JSONL 文件，输出完整时间轴
 * 
 * Usage: node session-analyzer.js <session-file.jsonl> [--detail]
 */

const fs = require('fs');
const path = require('path');

const sessionFile = process.argv[2];
const detail = process.argv.includes('--detail');

if (!sessionFile || !fs.existsSync(sessionFile)) {
  console.error('Usage: node session-analyzer.js <session-file.jsonl> [--detail]');
  process.exit(1);
}

const lines = fs.readFileSync(sessionFile, 'utf-8').trim().split('\n');
const msgs = lines.map(l => { try { return JSON.parse(l); } catch(e) { return null; } }).filter(Boolean);

// Find base time from user message
const baseMsg = msgs.find(m => m.type === 'message' && m.message?.role === 'user');
const baseTime = baseMsg ? new Date(baseMsg.message.timestamp) : new Date();

function timeLabel(ts) {
  const dt = new Date(ts);
  const elapsed = Math.round((dt - baseTime) / 1000);
  const sign = elapsed >= 0 ? '+' : '-';
  const abs = Math.abs(elapsed);
  const m = String(Math.floor(abs / 60)).padStart(2, '0');
  const s = String(abs % 60).padStart(2, '0');
  return sign + m + ':' + s;
}

console.log('=== 会话时间轴 ===');
console.log('文件: ' + sessionFile.split(/[\\/]/).pop());
console.log('消息数: ' + msgs.length);
console.log('');

let thinkSeq = 0;
let toolSeq = 0;

msgs.forEach(msg => {
  const type = msg.type;
  const ts = msg.timestamp;

  if (type === 'session') {
    console.log('[' + timeLabel(ts) + '] 📋 会话初始化: ' + (msg.id || '').substring(0, 8));
  } else if (type === 'model_change') {
    console.log('[' + timeLabel(ts) + '] 🔄 模型: ' + (msg.modelId || 'unknown'));
  } else if (type === 'thinking_level_change') {
    console.log('[' + timeLabel(ts) + '] 💭 Thinking: ' + (msg.thinkingLevel || 'unknown'));
  } else if (type === 'custom') {
    const ct = msg.customType || '';
    if (ct === 'model-snapshot') {
      const d = msg.data || {};
      console.log('[' + timeLabel(ts) + '] 🤖 模型快照: ' + (d.provider || '') + ' / ' + (d.modelId || ''));
    } else if (ct === 'openclaw:prompt-error') {
      const d = msg.data || {};
      console.log('[' + timeLabel(ts) + '] ❌ PROMPT ERROR: ' + (d.error || 'unknown'));
      console.log('   runId: ' + (d.runId || '').substring(0, 16));
      console.log('   距开始: ' + Math.round((d.timestamp - baseTime.getTime()) / 1000) + 's');
    }
  } else if (type === 'message') {
    const inner = msg.message || {};
    const role = inner.role;
    const innerTs = inner.timestamp || ts;

    if (role === 'user') {
      const content = inner.content || '';
      const text = typeof content === 'string' ? content : (Array.isArray(content) ? content.map(x => x.text || '').join('') : '');
      console.log('[' + timeLabel(innerTs) + '] 👤 USER');
      console.log('   ' + text.substring(0, 120));
    } else if (role === 'assistant') {
      const content = inner.content || [];
      let hasThinking = false;
      let hasToolCall = false;
      let hasText = false;

      if (Array.isArray(content)) {
        for (const part of content) {
          if (part.type === 'thinking') {
            hasThinking = true;
            thinkSeq++;
            const think = part.thinking || '';
            const sig = part.thinkingSignature || '';
            const lines2 = think.split('\n').filter(l => l.trim());
            console.log('');
            console.log('[' + timeLabel(innerTs) + '] 🧠 THINKING #' + thinkSeq + ' [' + sig + ']');
            console.log('   长度: ' + think.length + ' 字符, ' + lines2.length + ' 行');
            if (detail) {
              console.log(think.split('\n').map(l => '   ' + l).join('\n'));
            } else if (lines2.length <= 10) {
              lines2.forEach(l => console.log('   ' + l));
            } else {
              lines2.slice(0, 3).forEach(l => console.log('   ' + l));
              console.log('   ... (' + (lines2.length - 6) + ' 行省略) ...');
              lines2.slice(-3).forEach(l => console.log('   ' + l));
            }
            console.log('');
          } else if (part.type === 'toolCall') {
            hasToolCall = true;
            toolSeq++;
            const name = part.name || '';
            const args = part.arguments || {};
            if (name === 'feishu_bitable_app_table_record') {
              const action = args.action || '';
              if (action === 'list') {
                console.log('[' + timeLabel(innerTs) + '] 🔧 BITABLE.list 查询');
              } else if (action === 'update') {
                console.log('[' + timeLabel(innerTs) + '] 🔧 BITABLE.update ID:' + (args.record_id || '').substring(0, 12));
              } else if (action === 'create') {
                const fn = args.fields && args.fields['任务名称'] ? JSON.stringify(args.fields['任务名称']) : '';
                console.log('[' + timeLabel(innerTs) + '] 🔧 BITABLE.create ' + fn);
              } else {
                console.log('[' + timeLabel(innerTs) + '] 🔧 BITABLE.' + action);
              }
            } else if (name === 'exec') {
              const cmd = (args.command || '').substring(0, 80);
              console.log('[' + timeLabel(innerTs) + '] 🔧 EXEC: ' + cmd + '...');
            } else if (name === 'read') {
              const fp = (args.file_path || args.path || '').split(/[\\/]/).pop() || '';
              console.log('[' + timeLabel(innerTs) + '] 📖 READ: ' + fp);
            } else {
              console.log('[' + timeLabel(innerTs) + '] 🔧 ' + name);
            }
          } else if (part.type === 'text') {
            hasText = true;
            const text = part.text || '';
            console.log('[' + timeLabel(innerTs) + '] 💬 TEXT');
            console.log('   ' + text.replace(/\n/g, '\n   '));
          }
        }
      } else if (typeof content === 'string') {
        console.log('[' + timeLabel(innerTs) + '] 💬 TEXT: ' + content.substring(0, 150));
      }

      if (inner.stopReason) {
        console.log('   >> stop: ' + inner.stopReason);
      }
      if (inner.usage) {
        const u = inner.usage;
        console.log('   >> tokens: in=' + u.input + ' out=' + u.output + ' total=' + u.totalTokens);
      }
    } else if (role === 'toolResult') {
      const tool = inner.toolName || '';
      const isError = inner.isError || false;
      const status = isError ? '❌' : '✅';
      let textContent = '';
      if (Array.isArray(inner.content)) {
        textContent = inner.content[0] && inner.content[0].text || '';
      } else if (typeof inner.content === 'string') {
        textContent = inner.content;
      }
      const clen = textContent.length;

      if (tool === 'feishu_bitable_app_table_record') {
        try {
          const parsed = JSON.parse(textContent);
          if (parsed.error) {
            console.log('[' + timeLabel(innerTs) + '] ' + status + ' BITABLE返回: ' + parsed.error);
          } else if (parsed.records) {
            console.log('[' + timeLabel(innerTs) + '] ' + status + ' BITABLE.list: ' + parsed.records.length + ' 条');
          } else if (parsed.record) {
            const r = parsed.record;
            const rid = (r.record_id || '').substring(0, 12);
            const fname = r.fields && r.fields['任务名称'];
            const nameStr = fname ? (typeof fname === 'string' ? fname : (fname[0] && fname[0].text || '')) : '';
            console.log('[' + timeLabel(innerTs) + '] ' + status + ' BITABLE记录: ' + rid + ' | ' + nameStr);
          }
        } catch (e) {
          console.log('[' + timeLabel(innerTs) + '] ' + status + ' BITABLE[' + clen + 'chars]: ' + textContent.substring(0, 80));
        }
      } else if (tool === 'exec') {
        const preview = textContent.substring(0, 150).replace(/\n/g, ' ');
        console.log('[' + timeLabel(innerTs) + '] ' + status + ' EXEC[' + clen + 'chars]: ' + preview);
      } else if (tool === 'read') {
        console.log('[' + timeLabel(innerTs) + '] ' + status + ' READ[' + clen + 'chars]: ' + textContent.substring(0, 80));
      } else {
        console.log('[' + timeLabel(innerTs) + '] ' + status + ' ' + tool + '[' + clen + 'chars]');
      }
    } else {
      console.log('[' + timeLabel(innerTs) + '] [' + role + '] ' + JSON.stringify(msg).substring(0, 100));
    }
  }
});

// Summary
console.log('');
console.log('=== 统计 ===');
console.log('思考轮次: ' + thinkSeq);
console.log('工具调用: ' + toolSeq);
console.log('总消息: ' + msgs.length);

// Find errors
const errors = msgs.filter(m => m.customType === 'openclaw:prompt-error');
if (errors.length > 0) {
  console.log('');
  console.log('=== 错误 ===');
  errors.forEach(e => {
    const d = e.data || {};
    console.log('  ' + d.error);
    console.log('  时间: ' + timeLabel(d.timestamp));
  });
}
