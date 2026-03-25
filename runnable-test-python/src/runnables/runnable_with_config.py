"""
对应 runnable-test/src/runnables/RunnableWithConfig.mjs

演示 RunnableSequence + RunnableLambda 读取 RunnableConfig.configurable，
以及 chain.with_config(tags=..., metadata=..., configurable=...)。
"""
from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.runnables.config import RunnableConfig

# 模拟一个简单的「用户数据库」
mock_users: dict[str, dict[str, str]] = {
    "user-123": {
        "id": "user-123",
        "name": "神光",
        "email": "guang@example.com",
    },
}


def fetch_user_from_config(input: Any, config: RunnableConfig) -> dict[str, Any]:
  """节点1：根据 config.configurable.userId 查用户"""
  conf = config.get("configurable") or {}
  user_id = conf.get("userId")

  print("【节点1】收到了通知内容:", input)
  print("【节点1】从 config 里拿到 userId:", user_id)

  user = mock_users.get(user_id) if user_id else None
  if not user:
    raise ValueError("未找到用户，无法发送通知")

  return {"user": user, "notification": input}


def check_permission_by_role(
        state: dict[str, Any], config: RunnableConfig) -> dict[str, Any]:
  """节点2：根据 config.configurable.role 做权限判断"""
  conf = config.get("configurable") or {}
  role = conf.get("role") or "普通用户"

  print("【节点2】当前角色:", role)

  can_send = role in ("管理员", "运营", "系统")
  if not can_send:
    raise ValueError(f"角色「{role}」无权限发送系统通知")

  return {**state, "role": role}


def format_notification_by_locale(
        state: dict[str, Any], config: RunnableConfig) -> dict[str, Any]:
  """节点3：根据 locale 生成最终通知文案"""
  conf = config.get("configurable") or {}
  locale = conf.get("locale") or "zh-CN"

  print("【节点3】locale:", locale)

  user = state["user"]
  notification = state["notification"]
  role = state["role"]

  if locale == "en-US":
    content = (
        f"Dear {user['name']},\n\n{notification}\n\n(from role: {role})"
    )
  else:
    content = (
        f"亲爱的 {user['name']}，\n\n{notification}\n\n（发送人角色：{role}）"
    )

  return {**state, "locale": locale, "finalContent": content}


chain = RunnableSequence(
    RunnableLambda(fetch_user_from_config),
    RunnableLambda(check_permission_by_role),
    RunnableLambda(format_notification_by_locale),
)

chain_with_config = chain.with_config(
    tags=["demo", "withConfig", "notification"],
    metadata={"demoName": "RunnableWithConfig"},
    configurable={
        "userId": "user-123",
        "role": "管理员",
        "locale": "zh-CN",
    },
)

chain_with_config2 = chain.with_config(
    tags=["demo", "withConfig", "notification-en"],
    metadata={"demoName": "RunnableWithConfig2"},
    configurable={
        "userId": "user-123",
        "role": "运营",
        "locale": "en-US",
    },
)


def main() -> None:
  result = chain_with_config.invoke("你有一条新的系统通知，请及时查看。")
  print("✅ 最终通知内容:\n", result["finalContent"])

  print("\n--- chainWithConfig2 ---\n")

  result2 = chain_with_config2.invoke("System maintenance scheduled tonight.")
  print("✅ 最终通知内容:\n", result2["finalContent"])


if __name__ == "__main__":
  main()
