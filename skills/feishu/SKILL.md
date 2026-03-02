---
name: feishu
description: Feishu (Lark) API wrapper - docs, drive, permissions, messages. Create/read/write Feishu docs, manage drive files, set permissions, send messages.
tags: [feishu, lark, doc, drive, message, permission]
---

# Feishu Skill

Feishu Open Platform API lightweight wrapper, zero external dependencies.

## Environment Variables
```bash
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxx
```

## Modules

| Module | Function |
|--------|----------|
| doc | Create, read, write, append, delete documents |
| drive | List, create folder, delete, move files |
| perm | Set permissions (public link, add/remove collaborators) |
| msg | Send messages, reply to messages |

## Usage

```bash
# Documents
node cli.js doc create --title "Title"
node cli.js doc read --token <doc_token>
node cli.js doc write --token <doc_token> --content "Content"

# Drive
node cli.js drive list [--folder <folder_token>]
node cli.js drive mkdir --name "Folder" [--folder <parent>]

# Permissions
node cli.js perm public --token <token> --type docx --share tenant_editable
node cli.js perm add --token <token> --type docx --member ou_xxx --perm edit

# Messages
node cli.js msg send --to <open_id|chat_id> --text "Hello"
node cli.js msg reply --message_id <msg_id> --content "Reply"
```
