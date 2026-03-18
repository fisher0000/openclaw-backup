# 飞书消息回复技术知识库

> 来源：虾总分享的 FEISHU_MESSAGE_REPLY_GUIDE_CN.md
> 学习日期：2026-03-06
> 适用场景：OpenClaw 飞书消息回复线程

---

## 核心问题

使用 OpenClaw 的 `message` 工具发送消息时，即使指定了 `replyTo` 参数，也无法在飞书中创建真正的"回复"（即带有"回复：..."标识的消息）。消息会以独立消息的形式发送，而非回复某条消息。

---

## 根本原因

1. `message` 工具调用的是 `im.message.create` API 端点
2. 该端点不支持真正的回复功能
3. 即使传递 `root_id` 参数，API 也会忽略它

---

## 解决方案

使用 `im.message.reply` API 端点，并传递 `reply_in_thread` 参数。

### API 端点
```
POST /open-apis/im/v1/messages/:message_id/reply
```

### 关键参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message_id | string | ✅ | 要回复的消息 ID（URL 路径参数） |
| content | string | ✅ | 消息内容，JSON 序列化后的字符串 |
| msg_type | string | ✅ | 消息类型：text、post、interactive 等 |
| reply_in_thread | boolean | ❌ | 是否以话题形式回复 |

### reply_in_thread 参数详解

| 取值 | 效果 |
|------|------|
| true | 创建独立话题线程（在飞书中显示在单独的话题面板中） |
| false | 内联回复（在当前聊天中显示，带有"回复：..."标识） |

**建议**：对于普通回复，使用 `reply_in_thread: false` 更符合用户习惯。

---

## 代码示例

### 获取 tenant_access_token
```javascript
async function getTenantToken() {
  const res = await postJson(
    'open.feishu.cn',
    '/open-apis/auth/v3/tenant_access_token/internal',
    { app_id: APP_ID, app_secret: APP_SECRET }
  );
  if (res.code !== 0) throw new Error(res.msg);
  return res.tenant_access_token;
}
```

### 回复消息（创建真正的消息线程）
```javascript
async function replyToMessage(token, messageId, text) {
  const path = `/open-apis/im/v1/messages/${encodeURIComponent(messageId)}/reply`;

  const data = {
    content: JSON.stringify({ text: text }),
    msg_type: "text",
    reply_in_thread: false  // false = 在当前聊天中显示，true = 在话题面板中显示
  };

  return await postJson(
    'open.feishu.cn', 
    path, 
    data, 
    { 'Authorization': `Bearer ${token}` }
  );
}
```

---

## 响应字段说明

成功回复后，响应会包含以下关键字段：

```json
{
  "code": 0,
  "data": {
    "message_id": "om_xxx",
    "root_id": "om_parent",        // 根消息 ID
    "parent_id": "om_parent",      // 父消息 ID
    "thread_id": "omt_xxx"         // 话题 ID（仅当 reply_in_thread: true 时存在）
  }
}
```

| 字段 | 说明 |
|------|------|
| root_id | 根消息 ID，标识该回复属于哪个消息线程 |
| parent_id | 父消息 ID，即被回复的消息 ID |
| thread_id | 话题 ID，仅当 reply_in_thread: true 时返回 |

---

## 常见错误

### 1. 使用 im.message.create + root_id
```javascript
// ❌ 错误：root_id 会被 API 忽略
await client.im.message.create({
  params: { receive_id_type: "open_id" },
  data: {
    receive_id: userId,
    msg_type: "text",
    content: JSON.stringify({ text: "xxx" }),
    root_id: parentMessageId  // 无效！
  }
});
```

### 2. 使用 message 工具的 replyTo
```javascript
// ❌ 错误：message 工具的 replyTo 不会创建真正的回复线程
await message({
  action: "send",
  replyTo: "om_xxx",
  message: "xxx"
});
```

---

## 方法总结

| 方法 | 是否创建线程 | 说明 |
|------|-------------|------|
| message 工具 + replyTo | ❌ | 仅引用消息，不创建真正的回复 |
| im.message.create + root_id | ❌ | API 忽略 root_id 参数 |
| im.message.reply + reply_in_thread: false | ✅ | 内联回复，在当前聊天显示 |
| im.message.reply + reply_in_thread: true | ✅ | 话题回复，在话题面板显示 |

---

## 参考文档

- 飞书官方文档：https://open.feishu.cn/document/server-docs/im-v1/message/reply
- API Explorer：https://open.feishu.cn/api-explorer?project=im&resource=message&apiName=reply&version=v1

---

## 应用建议

1. 当需要真正回复消息时，**必须**直接调用飞书 API，不能使用 OpenClaw 的 `message` 工具
2. 在群聊场景中，使用 `reply_in_thread: false` 更符合中文用户习惯
3. 需要保存 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 以获取 tenant_access_token
