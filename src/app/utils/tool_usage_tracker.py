#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Usage Tracker - 工具使用统计

追踪工具使用情况、成功率、执行时间等指标，帮助 Agent 自我优化。
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from collections import defaultdict


class ToolUsageTracker:
    """工具使用追踪器"""
    
    def __init__(self, stats_file: str = "output/logs/tool_usage_stats.json"):
        self.stats_file = Path(stats_file)
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 当前会话统计（内存中）
        self.session_stats = defaultdict(lambda: {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
            "last_used": None,
            "error_messages": []
        })
        
        # 加载历史统计
        self.load_stats()
    
    def load_stats(self):
        """加载历史统计数据"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 合并历史数据到当前会话
                    for tool_name, stats in data.get("tools", {}).items():
                        self.session_stats[tool_name].update(stats)
            except Exception as e:
                print(f"Warning: Failed to load tool stats: {e}")
    
    def save_stats(self):
        """保存统计数据到文件"""
        try:
            stats_data = {
                "last_updated": datetime.now().isoformat(),
                "tools": dict(self.session_stats)
            }
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save tool stats: {e}")
    
    def track_call(self, tool_name: str, success: bool, execution_time: float, 
                    error_msg: Optional[str] = None):
        """
        追踪工具调用
        
        Args:
            tool_name: 工具名称
            success: 是否成功
            execution_time: 执行时间（秒）
            error_msg: 错误信息（如果失败）
        """
        stats = self.session_stats[tool_name]
        
        # 更新计数
        stats["total_calls"] += 1
        if success:
            stats["successful_calls"] += 1
        else:
            stats["failed_calls"] += 1
            if error_msg and len(stats["error_messages"]) < 10:  # 只保留最近 10 个错误
                stats["error_messages"].append({
                    "time": datetime.now().isoformat(),
                    "message": str(error_msg)[:200]  # 限制长度
                })
        
        # 更新时间统计
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_calls"]
        stats["last_used"] = datetime.now().isoformat()
        
        # 定期保存（每 5 次调用保存一次）
        if stats["total_calls"] % 5 == 0:
            self.save_stats()
    
    def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """获取特定工具的统计信息"""
        stats = self.session_stats.get(tool_name)
        if not stats:
            return {"error": f"No stats found for tool: {tool_name}"}
        
        success_rate = (stats["successful_calls"] / stats["total_calls"] * 100 
                       if stats["total_calls"] > 0 else 0)
        
        return {
            "tool_name": tool_name,
            "total_calls": stats["total_calls"],
            "successful_calls": stats["successful_calls"],
            "failed_calls": stats["failed_calls"],
            "success_rate": f"{success_rate:.1f}%",
            "avg_execution_time": f"{stats['avg_time']:.2f}s",
            "last_used": stats["last_used"],
            "recent_errors": stats["error_messages"][-3:] if stats["error_messages"] else []
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有工具的统计信息"""
        all_stats = {}
        for tool_name in self.session_stats.keys():
            all_stats[tool_name] = self.get_tool_stats(tool_name)
        
        return all_stats
    
    def get_top_tools(self, n: int = 10, by: str = "calls") -> list:
        """
        获取使用最多的工具
        
        Args:
            n: 返回前 N 个工具
            by: 排序依据 ("calls", "success_rate", "avg_time")
        """
        tools_list = []
        for tool_name, stats in self.session_stats.items():
            if stats["total_calls"] == 0:
                continue
            
            success_rate = stats["successful_calls"] / stats["total_calls"]
            tools_list.append({
                "name": tool_name,
                "calls": stats["total_calls"],
                "success_rate": success_rate,
                "avg_time": stats["avg_time"]
            })
        
        # 排序
        if by == "calls":
            tools_list.sort(key=lambda x: x["calls"], reverse=True)
        elif by == "success_rate":
            tools_list.sort(key=lambda x: x["success_rate"], reverse=True)
        elif by == "avg_time":
            tools_list.sort(key=lambda x: x["avg_time"])
        
        return tools_list[:n]
    
    def get_problematic_tools(self, threshold: float = 0.5) -> list:
        """
        获取问题工具（成功率低于阈值）
        
        Args:
            threshold: 成功率阈值（0-1）
        """
        problematic = []
        for tool_name, stats in self.session_stats.items():
            if stats["total_calls"] < 3:  # 至少调用 3 次才统计
                continue
            
            success_rate = stats["successful_calls"] / stats["total_calls"]
            if success_rate < threshold:
                problematic.append({
                    "name": tool_name,
                    "calls": stats["total_calls"],
                    "success_rate": f"{success_rate*100:.1f}%",
                    "recent_errors": stats["error_messages"][-2:]
                })
        
        return problematic
    
    def generate_report(self) -> str:
        """生成统计报告"""
        report = ["=" * 60]
        report.append("Tool Usage Statistics Report")
        report.append("=" * 60)
        report.append("")
        
        # 总体统计
        total_calls = sum(s["total_calls"] for s in self.session_stats.values())
        total_success = sum(s["successful_calls"] for s in self.session_stats.values())
        total_failed = sum(s["failed_calls"] for s in self.session_stats.values())
        
        report.append(f"Total Tools Used: {len(self.session_stats)}")
        report.append(f"Total Calls: {total_calls}")
        report.append(f"Total Successful: {total_success}")
        report.append(f"Total Failed: {total_failed}")
        if total_calls > 0:
            report.append(f"Overall Success Rate: {total_success/total_calls*100:.1f}%")
        report.append("")
        
        # 最常用工具
        report.append("Top 5 Most Used Tools:")
        report.append("-" * 60)
        for i, tool in enumerate(self.get_top_tools(5, by="calls"), 1):
            report.append(f"{i}. {tool['name']}: {tool['calls']} calls, "
                         f"{tool['success_rate']*100:.1f}% success, "
                         f"{tool['avg_time']:.2f}s avg")
        report.append("")
        
        # 问题工具
        problematic = self.get_problematic_tools(0.7)
        if problematic:
            report.append("⚠️  Problematic Tools (success rate < 70%):")
            report.append("-" * 60)
            for tool in problematic:
                report.append(f"• {tool['name']}: {tool['calls']} calls, "
                             f"{tool['success_rate']} success")
                if tool['recent_errors']:
                    report.append(f"  Recent error: {tool['recent_errors'][-1]['message'][:80]}")
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)


# 全局追踪器实例
_tracker_instance = None

def get_tracker() -> ToolUsageTracker:
    """获取全局追踪器实例"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ToolUsageTracker()
    return _tracker_instance


def track_tool_execution(tool_name: str):
    """
    装饰器：自动追踪工具执行
    
    用法:
        @track_tool_execution("my_tool")
        def my_tool():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = get_tracker()
            start_time = time.time()
            success = False
            error_msg = None
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_msg = str(e)
                raise
            finally:
                execution_time = time.time() - start_time
                tracker.track_call(tool_name, success, execution_time, error_msg)
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试
    tracker = ToolUsageTracker()
    
    # 模拟一些工具调用
    tracker.track_call("run_il_file", True, 1.2)
    tracker.track_call("run_il_file", True, 1.5)
    tracker.track_call("run_il_file", False, 0.8, "File not found")
    tracker.track_call("scan_knowledge_base", True, 0.3)
    tracker.track_call("load_domain_knowledge", True, 0.5)
    
    # 生成报告
    print(tracker.generate_report())
    
    # 保存统计
    tracker.save_stats()
    print(f"\nStats saved to: {tracker.stats_file}")

