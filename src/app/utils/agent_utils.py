import os
import json
import datetime
from smolagents import CodeAgent

def get_role(msg):
    """Get role from message object"""
    if hasattr(msg, 'role'):
        role = msg.role
        # Compatible with Enum and str
        if hasattr(role, 'value'):
            return role.value
        return str(role)
    elif isinstance(msg, dict):
        return msg.get('role')
    return None

class TokenLimitedCodeAgent(CodeAgent):
    """CodeAgent with token-limited memory management"""
    def write_memory_to_messages(self, summary_mode: bool = False):
        messages = self.memory.system_prompt.to_messages(summary_mode=False)
        steps = self.memory.steps
        n_first = 8
        n_last = 8
        total = len(steps)
        for idx, memory_step in enumerate(steps):
            step_msgs = memory_step.to_messages(summary_mode=False)
            for msg in step_msgs:
                role = get_role(msg)
                if idx < n_first or idx >= total - n_last:
                    if role in ['user', 'assistant', 'tool-response']:
                        messages.append(msg)
                else:
                    if role in ['user', 'tool-response']:
                        messages.append(msg)

        return messages

def save_agent_memory(agent, log_dir="logs", config_info=None):
    """Save agent memory to JSON file"""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Handle special characters in filenames
    def safe_name(name):
        if not name:
            return "none"
        return str(name).replace("/", "_").replace("\\", "_").replace(" ", "_")
    
    model_name = safe_name(config_info.get("model_name") if config_info else None)
    prompt_name = safe_name(config_info.get("prompt_name") if config_info else None)
    log_file = f"memory_{timestamp}_{model_name}_{prompt_name}.json"
    log_path = os.path.join(log_dir, log_file)
    
    memory_data = []
    for step in agent.memory.steps:
        msgs = step.to_messages(summary_mode=False)
        for msg in msgs:
            if hasattr(msg, 'to_dict'):
                d = msg.to_dict()
            elif isinstance(msg, dict):
                d = msg
            elif hasattr(msg, 'role') and hasattr(msg, 'content'):
                d = {
                    "role": str(msg.role),
                    "content": msg.content
                }
            else:
                d = {"raw": str(msg)}
            if "content" in d and not isinstance(d["content"], str):
                d["content"] = json.dumps(d["content"], ensure_ascii=False, indent=2)
            memory_data.append(d)
    
    log_obj = {
        "config": {
            "prompt_name": config_info.get("prompt_name") if config_info else None,
            "model_name": config_info.get("model_name") if config_info else None,
            "log_file": log_file,
            "timestamp": timestamp,
            "first_user_input": config_info.get("first_user_input") if config_info else None
        },
        "memory": memory_data
    }
    
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_obj, f, ensure_ascii=False, indent=2)
    print(f"Memory log saved to: {log_path}") 