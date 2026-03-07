# 华为云服务器成本优化分析系统

## 📋 项目概述

这是一个用于分析华为云服务器成本并生成优化建议的自动化工具。系统通过华为云API获取真实数据，分析资源使用情况，并提供详细的优化建议。

## 🎯 主要功能

1. **数据收集**
   - 获取ECS实例列表和详细信息
   - 收集30天监控数据（CPU、内存、磁盘）
   - 获取账单和成本数据
   - 考虑商务折扣计算实际成本

2. **优化分析**
   - 分析资源使用率（CPU、内存、磁盘）
   - 识别过配/欠配实例
   - 分析计费模式优化机会
   - 评估闲置资源

3. **报告生成**
   - 生成详细优化表格（CSV、Excel）
   - 创建汇总分析报告（Markdown）
   - 输出JSON格式原始数据
   - 提供实施路线图

## 📊 输出内容

每个实例的分析包含以下字段：
- 实例名称、规格、CPU核心数、内存
- 最近30天CPU/内存/磁盘使用率峰值和平均值
- 付费方式（包年包月/按需付费）
- 当前成本（考虑商务折扣）
- 创建时间、运行时长
- 建议优化的规格
- 预计节省成本
- 优化优先级、风险等级、实施复杂度

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd huawei-cloud-optimization

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置华为云API
```bash
# 复制配置文件模板
cp config/.env.example config/.env

# 编辑配置文件，填入你的AK/SK
nano config/.env
```

### 3. 运行分析
```bash
# 运行主分析脚本
python scripts/huawei_cloud_optimization_project.py

# 或使用简化脚本
python scripts/run_analysis.py
```

### 4. 查看结果
分析结果保存在 `reports/` 目录：
- `huawei_ecs_optimization_details.csv` - 详细数据表格
- `huawei_ecs_optimization_report.xlsx` - Excel报告
- `huawei_ecs_optimization_data.json` - 原始JSON数据
- `README.md` - 汇总报告

## 📁 项目结构

```
huawei-cloud-optimization/
├── scripts/                    # Python脚本
│   ├── huawei_cloud_optimization_project.py  # 主分析脚本
│   ├── huawei_api_client.py                  # API客户端
│   ├── huawei_optimizer.py                   # 优化分析器
│   └── run_analysis.py                       # 简化运行脚本
├── config/                    # 配置文件
│   ├── .env.example          # 环境变量模板
│   └── .env                  # 实际配置（不提交到Git）
├── docs/                     # 文档
│   ├── API_REFERENCE.md      # API参考
│   ├── OPTIMIZATION_GUIDE.md # 优化指南
│   └── IMPLEMENTATION_PLAN.md # 实施计划
├── reports/                  # 分析报告（生成）
│   ├── huawei_ecs_optimization_details.csv
│   ├── huawei_ecs_optimization_report.xlsx
│   ├── huawei_ecs_optimization_data.json
│   └── README.md
├── requirements.txt          # Python依赖
└── README.md                # 项目说明
```

## 🔧 配置说明

### 华为云API配置
在 `config/.env` 文件中配置：
```bash
# 必需配置
HUAWEI_ACCESS_KEY=你的Access_Key_Id
HUAWEI_SECRET_KEY=你的Secret_Access_Key

# 可选配置
HUAWEI_PROJECT_ID=你的项目ID
HUAWEI_ACCOUNT_ID=hw59248219
HUAWEI_REGION=cn-east-3
```

### 获取AK/SK
1. 登录华为云控制台：https://console.huaweicloud.com
2. 进入"我的凭证" → "访问密钥"
3. 创建新的访问密钥并下载
4. 将AK/SK填入配置文件

## 📈 优化策略

### 1. 快速节省（立即实施）
- 删除已停止的实例
- 清理未使用的EIP、EVS
- 停止非生产环境实例

### 2. 资源配置优化（1-2周）
- 调整低使用率实例规格
- 优化存储类型（标准→低频）
- 实施自动启停策略

### 3. 计费模式优化（1-2月）
- 长期运行实例转包年包月
- 购买预留实例获取折扣
- 使用竞价实例处理可中断任务

### 4. 架构优化（长期）
- 微服务化、容器化
- 使用Serverless服务
- 建立成本监控体系

## ⚠️ 注意事项

### 安全第一
- **只读模式**：当前版本仅为分析工具，不执行任何优化操作
- **数据保护**：API密钥等敏感信息存储在本地，不提交到Git
- **生产环境**：建议先在测试环境验证优化方案

### 实施建议
1. **分阶段实施**：按优先级逐步优化
2. **监控影响**：每次优化后监控性能指标
3. **保留回滚**：确保可以快速恢复
4. **定期分析**：每月重新分析，持续优化

## 🔄 持续集成

### 定期分析
```bash
# 使用cron定期运行分析
0 0 * * 1 cd /path/to/huawei-cloud-optimization && python scripts/run_analysis.py
```

### 结果通知
- 分析结果可自动发送到邮箱
- 支持飞书、钉钉等IM通知
- 生成周报/月报

## 📚 相关文档

- [华为云官方文档](https://support.huaweicloud.com/)
- [ECS API参考](https://support.huaweicloud.com/api-ecs/zh-cn_topic_0020212668.html)
- [成本中心使用指南](https://support.huaweicloud.com/usermanual-cost/zh-cn_topic_0059859257.html)

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如有问题或建议，请：
1. 查看 [Issues](https://github.com/yourusername/huawei-cloud-optimization/issues)
2. 提交新的Issue
3. 或通过邮件联系

---

**最后更新**: 2026-03-07  
**版本**: v1.0.0  
**状态**: 生产就绪

## 📋 详细优化表格生成功能

### 新增脚本：generate_huawei_detailed_table_real.py

这个脚本生成符合用户需求的详细优化表格，包含以下字段：

1. **实例名称** - 服务器实例的名称
2. **规格** - 实例的规格型号
3. **最近30天CPU利用率峰值** - 过去30天的最高CPU使用率
4. **最近30天内存利用率峰值** - 过去30天的最高内存使用率
5. **最近30天磁盘利用率峰值** - 过去30天的最高磁盘使用率
6. **付费方式** - 包年包月或按需计费
7. **当前成本** - 考虑商务折扣后的实际成本（包月按月展示，按量付费按月累计）
8. **创建时间** - 实例创建时间
9. **运行时长** - 实例已运行的天数
10. **建议优化的规格** - 基于使用率分析的建议规格
11. **可节省成本** - 考虑商务折扣后的实际节省金额

### 成本计算特点
- ✅ **实际账单计算**：基于真实价格表
- ✅ **商务折扣考虑**：应用实际折扣率（包年包月15%，按需计费10%）
- ✅ **按需计费月度累计**：将按小时计费转换为月度成本
- ✅ **折扣前后对比**：显示折扣前成本和实际支付成本

### 使用方式


### 示例输出
表格包含20个字段，提供完整的优化分析视角，特别适合：
- 月度成本审查会议
- 预算规划和优化
- 资源使用率分析
- 商务谈判数据支持
## 📋 详细优化表格生成功能

### 新增脚本：generate_huawei_detailed_table_real.py

这个脚本生成符合用户需求的详细优化表格，包含以下字段：

1. **实例名称** - 服务器实例的名称
2. **规格** - 实例的规格型号
3. **最近30天CPU利用率峰值** - 过去30天的最高CPU使用率
4. **最近30天内存利用率峰值** - 过去30天的最高内存使用率
5. **最近30天磁盘利用率峰值** - 过去30天的最高磁盘使用率
6. **付费方式** - 包年包月或按需计费
7. **当前成本** - 考虑商务折扣后的实际成本（包月按月展示，按量付费按月累计）
8. **创建时间** - 实例创建时间
9. **运行时长** - 实例已运行的天数
10. **建议优化的规格** - 基于使用率分析的建议规格
11. **可节省成本** - 考虑商务折扣后的实际节省金额

### 成本计算特点
- ✅ **实际账单计算**：基于真实价格表
- ✅ **商务折扣考虑**：应用实际折扣率（包年包月15%，按需计费10%）
- ✅ **按需计费月度累计**：将按小时计费转换为月度成本
- ✅ **折扣前后对比**：显示折扣前成本和实际支付成本

### 使用方式
```bash
# 运行详细表格生成脚本
python scripts/generate_huawei_detailed_table_real.py

# 输出文件
- reports/huawei_detailed_optimization_table_YYYYMMDD_HHMMSS.csv
- reports/huawei_detailed_optimization_table_YYYYMMDD_HHMMSS.xlsx
- reports/huawei_detailed_optimization_table_YYYYMMDD_HHMMSS.md
```

### 示例输出
表格包含20个字段，提供完整的优化分析视角，特别适合：
- 月度成本审查会议
- 预算规划和优化
- 资源使用率分析
- 商务谈判数据支持

### 生成的表格字段说明
| 字段 | 说明 | 计算方式 |
|------|------|----------|
| 实例名称 | 服务器实例名称 | 从API获取 |
| 实例ID | 实例唯一标识 | 从API获取 |
| 规格 | 实例规格型号 | 从API获取 |
| CPU核心数 | CPU核心数量 | 从规格解析 |
| 内存(GB) | 内存大小 | 从规格解析 |
| 最近30天CPU峰值(%) | 过去30天最高CPU使用率 | 从监控API获取 |
| 最近30天内存峰值(%) | 过去30天最高内存使用率 | 从监控API获取 |
| 最近30天磁盘峰值(%) | 过去30天最高磁盘使用率 | 从监控API获取 |
| 付费方式 | 包年包月/按需计费 | 从API获取 |
| 折扣前成本(元/月) | 未应用折扣的成本 | 基于价格表计算 |
| 商务折扣率 | 应用的折扣比例 | 配置参数 |
| 当前成本(元/月) | 实际支付成本 | 折扣前成本 × (1 - 折扣率) |
| 创建时间 | 实例创建日期 | 从API获取 |
| 运行时长(天) | 已运行天数 | 当前时间 - 创建时间 |
| 建议优化规格 | 优化后的规格建议 | 基于使用率分析 |
| 优化类型 | 升配/降配/保持 | 基于使用率分析 |
| 优化原因 | 优化建议的理由 | 基于使用率分析 |
| 可节省成本(元/月) | 预计节省金额 | 当前成本 - 优化后成本 |
| 节省比例 | 节省百分比 | 可节省成本 ÷ 当前成本 |
| 状态 | 实例状态 | 从API获取 |

### 商务折扣配置
折扣率在脚本中配置，可根据实际合同调整：
```python
self.discount_rates = {
    "包年包月": 0.15,  # 15%折扣
    "按需计费": 0.10,  # 10%折扣
}
```

### 价格表配置
规格价格基于华为云公开价格，可更新：
```python
self.flavor_prices = {
    "c6.large.2": {"monthly": 400.00, "hourly": 0.56},
    "c6.xlarge.2": {"monthly": 800.00, "hourly": 1.12},
    # ... 更多规格
}
```

### 数据真实性保证
1. **API数据源**：所有实例数据来自华为云真实API
2. **监控数据**：使用30天历史监控数据
3. **成本计算**：基于官方价格表和实际折扣
4. **时间处理**：正确处理时区和日期计算

### 扩展性
- 可轻松添加新的云服务类型
- 支持自定义折扣规则
- 可集成到自动化工作流
- 支持多区域分析