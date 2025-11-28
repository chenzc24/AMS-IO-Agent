# Batch Experiments - 统一实验脚本

本项目使用统一的批量实验脚本 `run_batch_experiments.py`，支持多种实验类型。所有实验的 prompt 在运行时动态生成，无需在 YAML 文件中预定义。

## 改进内容

### 之前的问题
1. **代码重复**：为每个模型（claude, gpt, deepseek）维护几乎完全相同的脚本
2. **YAML 文件臃肿**：需要在 `user_prompts.yaml` 中为每个 sheet 预定义 prompt，导致文件巨大且难以维护
3. **维护困难**：修改 prompt 模板需要更新多个文件和 YAML 条目
4. **脚本分散**：多个不同的 batch 脚本，功能重复

### 现在的解决方案
1. **统一脚本**：只需要一个 `run_batch_experiments.py`，支持所有实验类型
2. **动态生成 prompt**：不再依赖 YAML 文件，prompt 在运行时动态生成
3. **易于维护**：prompt 模板在代码中统一管理（字典注册表模式），修改一处即可
4. **易于扩展**：添加新模板只需在字典中添加条目

## 实验类型

脚本支持两种实验类型：

1. **`cdac`**（默认）：CDAC 数组实验，基于 Excel 文件中的 sheet
2. **`capacitance_shape`**：电容值和形状组合实验（19 个电容值 × 5 种形状 = 95 个实验）

## 使用方法

### 1. CDAC 实验

基于 Excel 文件中的 sheet 运行 CDAC 数组实验。

#### 基本用法

```bash
# 运行默认实验（array-only 模式，无前缀）
python run_batch_experiments.py

# 运行 Claude 模型实验（array-only 模式，使用 'claude_' 前缀）
python run_batch_experiments.py --prefix claude --model-name claude

# 运行全流程实验（unit + dummy + array）使用 Claude 模型
python run_batch_experiments.py --prefix claude --model-name claude --template-type full

# 运行 GPT 模型实验（array-only 模式，使用 'gpt_' 前缀）
python run_batch_experiments.py --prefix gpt --model-name gpt-4o

# 运行 DeepSeek 模型实验（array-only 模式，使用 'deepseek_' 前缀）
python run_batch_experiments.py --prefix deepseek --model-name deepseek

# 预览生成的 prompt
python run_batch_experiments.py --prefix claude --template-type full --preview-prompt first

# 从第 5 个实验开始
python run_batch_experiments.py --prefix claude --start-index 5

# 只运行前 10 个实验
python run_batch_experiments.py --prefix claude --stop-index 10

# 并行运行（使用不同的 RAMIC 端口）
python run_batch_experiments.py --prefix claude --ramic-port-start 65432
```

### 2. Capacitance/Shape 实验

运行不同电容值和单位电容形状的组合实验。

#### 实验配置
- **电容值**: 19个 (0.1, 0.2, ..., 0.9, 1, 2, ..., 10 fF)
- **形状**: 5个 (H, H_shieldless, I, I_shield, sandwich_simplified_h_notch)
- **总实验数**: 95个 (19 × 5)
- **每个实验超时**: 50分钟

#### 基本用法

```bash
# 运行所有电容值和形状组合（95 个实验）
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --model-name claude

# 预览第一个 prompt
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --preview-prompt first

# 从第 10 个实验开始
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 10

# 只运行前 20 个实验
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --stop-index 20

# 并行运行（使用不同的 RAMIC 端口）
# 终端1：运行前32个实验
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 1 --stop-index 32 --ramic-port-start 65432

# 终端2：运行第33到第64个实验
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 33 --stop-index 64 --ramic-port-start 65433

# 终端3：运行剩余实验
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 65 --ramic-port-start 65434
```

## 模板类型

脚本支持三种 prompt 模板类型：

1. **`array`**（CDAC 默认）：只生成 CDAC array，跳过 unit cell 和 dummy 生成
   - 适用于 unit 和 dummy 已经存在的情况
   - 更快，只执行 Phase 3

2. **`full`**（CDAC）：完整流程，包含三个阶段
   - Phase 1: 生成 unit H-shape capacitor
   - Phase 2: 生成 dummy capacitor
   - Phase 3: 生成 CDAC array
   - 适用于从头开始完整设计

3. **`capacitance_shape`**（自动）：电容值和形状组合实验
   - Phase 1: 生成 unit capacitor（指定电容值和形状）
   - Phase 2: 生成 dummy capacitor
   - 适用于测试不同电容值和形状的组合

## 通用参数

所有实验类型都支持以下参数：

### 模型和前缀
- `--prefix`: 前缀（如 'claude', 'gpt', 'deepseek'）
- `--model-name`: 模型名称（如 'claude', 'gpt-4o', 'deepseek'）

### 实验范围
- `--start-index`: 从第 N 个实验开始（1-based）
- `--stop-index`: 运行到第 N 个实验（包含）
- `--start-from`: 从特定 sheet 名称开始（仅 CDAC 实验）
- `--stop-at`: 运行到特定 sheet 名称（仅 CDAC 实验）

### 预览和测试
- `--dry-run`: 预览模式，只列出将要运行的实验
- `--preview-prompt`: 预览生成的 prompt（'first', 'all', 或指定 sheet 名称）

### RAMIC 配置
- `--ramic-port`: 所有实验使用同一个端口
- `--ramic-port-start`: 每个实验使用递增端口（port_start + index）
- `--ramic-host`: RAMIC 主机地址

### 其他
- `--excel-file`: Excel 文件路径（仅 CDAC 实验，默认：excel/CDAC_3-8bit.xlsx）
- `--experiment-type`: 实验类型（'cdac' 或 'capacitance_shape'，默认：'cdac'）
- `--template-type`: 模板类型（'array', 'full', 'capacitance_shape'）

### 高级选项示例

```bash
# 指定 Excel 文件
python run_batch_experiments.py --excel-file path/to/file.xlsx --prefix claude

# 从指定 sheet 开始
python run_batch_experiments.py --prefix claude --start-from "Sheet3"

# 运行到指定 sheet 停止
python run_batch_experiments.py --prefix claude --stop-at "Sheet10"

# 预览所有 prompt
python run_batch_experiments.py --prefix claude --preview-prompt all

# 预览特定 sheet 的 prompt
python run_batch_experiments.py --prefix claude --preview-prompt "Sheet3"
```

## Prompt 生成

Prompt 现在在 `run_batch_experiments.py` 的 `PROMPT_TEMPLATES` 字典中定义，通过 `generate_prompt_text()` 函数动态生成。修改字典中的模板即可更新所有实验的 prompt。

### Prompt 模板位置
- 文件：`run_batch_experiments.py`
- 位置：文件顶部的 `PROMPT_TEMPLATES` 字典
- 函数：`generate_prompt_text()`

### 预览 Prompt

在运行实验前，可以预览生成的 prompt：

```bash
# 预览第一个 prompt（作为示例）
python run_batch_experiments.py --prefix claude --preview-prompt first

# 预览所有 prompt
python run_batch_experiments.py --prefix claude --preview-prompt all

# 预览特定 sheet 的 prompt
python run_batch_experiments.py --prefix claude --preview-prompt "Sheet3"
```

这对于验证 prompt 模板是否正确非常有用。

## 日志文件

所有实验的日志会保存在：
- CDAC 实验：`logs/batch_cdac_{prefix}_{template_type}/`
- Capacitance/Shape 实验：`logs/batch_capacitance_shape_{prefix}_capacitance_shape/`

日志文件命名格式：`{prompt_key}_{timestamp}.log`

## 运行建议

### 单机运行
```bash
# 直接运行所有实验（按顺序执行）
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --model-name claude
```

### 并行运行（推荐）

如果有多台机器或可以启动多个 Virtuoso 实例，可以并行运行：

```bash
# 将 95 个实验分成 3 组，每组约 32 个
# 终端1
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 1 --stop-index 32 --ramic-port-start 65432

# 终端2
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 33 --stop-index 64 --ramic-port-start 65433

# 终端3
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 65 --ramic-port-start 65434
```

## 注意事项

1. **超时设置**: 每个实验最多运行 50 分钟，超时后会自动终止并继续下一个
2. **自动退出**: 脚本会自动发送 "exit" 命令，无需手动干预
3. **错误处理**: 如果某个实验失败，脚本会自动继续运行下一个实验
4. **并行运行**: 如果并行运行，确保每个实例使用不同的 RAMIC 端口
5. **资源占用**: 每个实验会占用一定的 CPU 和内存，注意系统资源
6. **Prompt 动态生成**: 不再需要在 YAML 中预定义 prompt，所有 prompt 在运行时动态生成

## 时间估算

### Capacitance/Shape 实验（95 个）
- **单线程**: 95个实验 × 20分钟 = 约32小时
- **3线程并行**: 约11小时
- **5线程并行**: 约6.5小时

### CDAC 实验（20 个 sheet）
- **单线程**: 20个实验 × 40分钟 = 约13小时
- **3线程并行**: 约4.5小时

## 恢复运行

如果实验中断，可以从指定位置继续：

```bash
# 从第 50 个实验继续运行
python run_batch_experiments.py --experiment-type capacitance_shape --prefix claude --start-index 50

# CDAC 实验：从特定 sheet 继续
python run_batch_experiments.py --prefix claude --start-from "6bit_1"
```

## 技术细节

### Prompt 传递方式
1. 动态生成 prompt 文本
2. 写入临时文件 `user_prompt.txt`
3. `multi_agent_main.py` 自动读取该文件
4. 实验结束后自动清理临时文件

### 新增的 CLI 参数
- `--prompt-text`：直接传递 prompt 文本（在 `multi_agent_main.py` 中可用，但 batch 脚本使用文件方式更可靠）

## 优势总结

✅ **代码简洁**：从多个重复脚本减少到 1 个统一脚本  
✅ **维护方便**：prompt 模板使用字典注册表模式，集中管理，易于扩展  
✅ **无需 YAML**：不再需要在 YAML 中预定义大量 prompt  
✅ **灵活配置**：通过命令行参数轻松切换模型、实验类型和配置  
✅ **易于扩展**：添加新模板只需在 `PROMPT_TEMPLATES` 字典中添加条目  
✅ **统一接口**：所有实验类型使用相同的命令行接口  
✅ **向后兼容**：仍然支持通过 `--prompt` 使用 YAML 中的 prompt（用于其他场景）

## 已废弃的文件

以下文件已整合到 `run_batch_experiments.py`，可以安全删除：
- ✅ `run_batch_experiments_claude.py` - 已删除
- ✅ `run_batch_experiments_gpt.py` - 已删除
- ✅ `run_batch_experiments_deepseek.py` - 已删除
- ✅ `run_capacitance_shape_batch.py` - 已删除
- ✅ `generate_test_array_prompts.py` - 已删除
- ✅ `generate_test_array_deepseek_prompts.py` - 已删除
- ✅ `generate_capacitance_shape_prompts.py` - 已删除

所有功能现在都通过 `run_batch_experiments.py` 统一管理。
