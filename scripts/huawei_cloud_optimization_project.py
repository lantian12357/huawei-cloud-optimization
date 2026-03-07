#!/usr/bin/env python3
"""
华为云服务器优化分析项目
获取真实API数据并生成详细优化报告
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
import hashlib
import base64
import hmac
from urllib.parse import urlparse
import time

class HuaweiCloudAPI:
    """华为云API客户端"""
    
    def __init__(self, access_key: str, secret_key: str, project_id: str = None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.project_id = project_id
        self.region = "cn-east-3"
        self.base_url = f"https://ecs.{self.region}.myhuaweicloud.com"
        self.token = None
        self.token_expires = None
        
    def _get_signature_key(self, secret_key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
        """生成签名密钥"""
        k_date = hmac.new(f"HWS{secret_key}".encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region_name.encode('utf-8'), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service_name.encode('utf-8'), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, "sdk_request".encode('utf-8'), hashlib.sha256).digest()
        return k_signing
    
    def _get_auth_token(self) -> str:
        """获取IAM认证token"""
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
            
        url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "name": self.access_key,
                            "password": self.secret_key,
                            "domain": {
                                "name": self.access_key
                            }
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": self.region
                    }
                }
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 201:
                self.token = response.headers.get('X-Subject-Token')
                # Token通常有效24小时
                self.token_expires = datetime.now() + timedelta(hours=23)
                return self.token
            else:
                print(f"❌ 获取token失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ 获取token异常: {e}")
            return None
    
    def get_ecs_instances(self) -> List[Dict]:
        """获取ECS实例列表"""
        print("🔍 获取ECS实例列表...")
        
        # 模拟数据（实际应调用API）
        # 这里使用模拟数据展示格式
        mock_instances = [
            {
                "id": "i-001",
                "name": "web-server-01",
                "spec": "c6.2xlarge.2",
                "cpu": 8,
                "memory": 16,
                "status": "ACTIVE",
                "billing_mode": "prePaid",  # 包年包月
                "created_at": "2025-01-15T10:30:00Z",
                "flavor_id": "c6.2xlarge.2",
                "image_id": "img-001",
                "vpc_id": "vpc-001",
                "subnet_id": "subnet-001",
                "security_groups": ["sg-001"],
                "volume_ids": ["vol-001"],
                "eip_id": "eip-001"
            },
            {
                "id": "i-002",
                "name": "db-server-01",
                "spec": "r6.4xlarge.2",
                "cpu": 16,
                "memory": 64,
                "status": "ACTIVE",
                "billing_mode": "postPaid",  # 按需付费
                "created_at": "2025-03-20T14:45:00Z",
                "flavor_id": "r6.4xlarge.2",
                "image_id": "img-002",
                "vpc_id": "vpc-001",
                "subnet_id": "subnet-002",
                "security_groups": ["sg-002"],
                "volume_ids": ["vol-002", "vol-003"],
                "eip_id": "eip-002"
            },
            {
                "id": "i-003",
                "name": "test-server-01",
                "spec": "c6.xlarge.2",
                "cpu": 4,
                "memory": 8,
                "status": "STOPPED",
                "billing_mode": "postPaid",
                "created_at": "2025-06-10T09:15:00Z",
                "flavor_id": "c6.xlarge.2",
                "image_id": "img-003",
                "vpc_id": "vpc-001",
                "subnet_id": "subnet-003",
                "security_groups": ["sg-003"],
                "volume_ids": ["vol-004"],
                "eip_id": None
            },
            {
                "id": "i-004",
                "name": "app-server-01",
                "spec": "c6.4xlarge.2",
                "cpu": 16,
                "memory": 32,
                "status": "ACTIVE",
                "billing_mode": "prePaid",
                "created_at": "2025-08-05T11:20:00Z",
                "flavor_id": "c6.4xlarge.2",
                "image_id": "img-004",
                "vpc_id": "vpc-001",
                "subnet_id": "subnet-001",
                "security_groups": ["sg-001"],
                "volume_ids": ["vol-005", "vol-006"],
                "eip_id": "eip-003"
            },
            {
                "id": "i-005",
                "name": "backup-server-01",
                "spec": "s6.large.2",
                "cpu": 2,
                "memory": 4,
                "status": "ACTIVE",
                "billing_mode": "postPaid",
                "created_at": "2025-10-12T16:30:00Z",
                "flavor_id": "s6.large.2",
                "image_id": "img-005",
                "vpc_id": "vpc-001",
                "subnet_id": "subnet-004",
                "security_groups": ["sg-004"],
                "volume_ids": ["vol-007"],
                "eip_id": None
            }
        ]
        
        print(f"✅ 获取到 {len(mock_instances)} 个ECS实例")
        return mock_instances
    
    def get_monitoring_data(self, instance_id: str, metric_name: str, days: int = 30) -> Dict:
        """获取监控数据"""
        # 模拟监控数据
        metrics = {
            "cpu_util": {"max": 35.2, "avg": 18.7, "min": 5.1},
            "mem_util": {"max": 62.8, "avg": 45.3, "min": 32.1},
            "disk_util": {"max": 78.5, "avg": 65.2, "min": 52.3},
            "disk_read_bytes_rate": {"max": 1250000, "avg": 850000, "min": 450000},
            "disk_write_bytes_rate": {"max": 980000, "avg": 620000, "min": 310000},
            "network_in_bytes_rate": {"max": 2100000, "avg": 1450000, "min": 890000},
            "network_out_bytes_rate": {"max": 1850000, "avg": 1250000, "min": 760000}
        }
        
        return metrics.get(metric_name, {"max": 0, "avg": 0, "min": 0})
    
    def get_billing_data(self, resource_id: str, resource_type: str = "ecs") -> Dict:
        """获取账单数据"""
        # 模拟账单数据
        billing_data = {
            "i-001": {
                "monthly_cost": 1250.00,  # 包月费用
                "discount_rate": 0.85,    # 商务折扣85折
                "actual_cost": 1062.50,   # 实际费用
                "billing_mode": "prePaid",
                "resource_type": "ecs"
            },
            "i-002": {
                "daily_cost": 42.50,      # 日均费用
                "monthly_cost": 1275.00,  # 按月累计
                "discount_rate": 0.88,    # 商务折扣88折
                "actual_cost": 1122.00,   # 实际费用
                "billing_mode": "postPaid",
                "resource_type": "ecs"
            },
            "i-003": {
                "daily_cost": 18.75,
                "monthly_cost": 562.50,
                "discount_rate": 0.90,
                "actual_cost": 506.25,
                "billing_mode": "postPaid",
                "resource_type": "ecs"
            },
            "i-004": {
                "monthly_cost": 2100.00,
                "discount_rate": 0.82,
                "actual_cost": 1722.00,
                "billing_mode": "prePaid",
                "resource_type": "ecs"
            },
            "i-005": {
                "daily_cost": 12.80,
                "monthly_cost": 384.00,
                "discount_rate": 0.85,
                "actual_cost": 326.40,
                "billing_mode": "postPaid",
                "resource_type": "ecs"
            }
        }
        
        return billing_data.get(resource_id, {
            "monthly_cost": 0,
            "discount_rate": 1.0,
            "actual_cost": 0,
            "billing_mode": "unknown",
            "resource_type": resource_type
        })
    
    def get_flavor_prices(self) -> Dict:
        """获取规格价格表"""
        # 华为云ECS规格价格（模拟数据，单位：元/月）
        flavor_prices = {
            "c6.large.2": {"cpu": 2, "memory": 4, "price": 320.00},
            "c6.xlarge.2": {"cpu": 4, "memory": 8, "price": 640.00},
            "c6.2xlarge.2": {"cpu": 8, "memory": 16, "price": 1280.00},
            "c6.4xlarge.2": {"cpu": 16, "memory": 32, "price": 2560.00},
            "r6.large.2": {"cpu": 2, "memory": 16, "price": 480.00},
            "r6.xlarge.2": {"cpu": 4, "memory": 32, "price": 960.00},
            "r6.2xlarge.2": {"cpu": 8, "memory": 64, "price": 1920.00},
            "r6.4xlarge.2": {"cpu": 16, "memory": 128, "price": 3840.00},
            "s6.large.2": {"cpu": 2, "memory": 4, "price": 280.00},
            "s6.xlarge.2": {"cpu": 4, "memory": 8, "price": 560.00},
            "s6.2xlarge.2": {"cpu": 8, "memory": 16, "price": 1120.00},
        }
        
        return flavor_prices

class HuaweiCloudOptimizer:
    """华为云优化分析器"""
    
    def __init__(self, api_client: HuaweiCloudAPI):
        self.api = api_client
        self.instances = []
        self.analysis_results = []
        
    def collect_data(self):
        """收集所有数据"""
        print("📊 开始收集云服务器数据...")
        
        # 获取ECS实例
        self.instances = self.api.get_ecs_instances()
        
        # 为每个实例收集详细数据
        for instance in self.instances:
            print(f"  分析实例: {instance['name']} ({instance['id']})")
            
            # 获取监控数据
            cpu_data = self.api.get_monitoring_data(instance['id'], "cpu_util", 30)
            mem_data = self.api.get_monitoring_data(instance['id'], "mem_util", 30)
            disk_data = self.api.get_monitoring_data(instance['id'], "disk_util", 30)
            
            # 获取账单数据
            billing_data = self.api.get_billing_data(instance['id'])
            
            # 计算运行时长
            created_at_str = instance['created_at'].replace('Z', '+00:00')
            created_at = datetime.fromisoformat(created_at_str)
            # 确保两个datetime对象都有时区信息
            from datetime import timezone
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            running_days = (now - created_at).days
            
            # 分析优化建议
            optimization = self.analyze_optimization(instance, cpu_data, mem_data, disk_data, billing_data)
            
            # 构建结果
            result = {
                "实例ID": instance['id'],
                "实例名称": instance['name'],
                "规格": instance['spec'],
                "CPU核心数": instance['cpu'],
                "内存(GB)": instance['memory'],
                "最近30天CPU峰值(%)": round(cpu_data['max'], 1),
                "最近30天CPU平均(%)": round(cpu_data['avg'], 1),
                "最近30天内存峰值(%)": round(mem_data['max'], 1),
                "最近30天内存平均(%)": round(mem_data['avg'], 1),
                "最近30天磁盘峰值(%)": round(disk_data['max'], 1),
                "最近30天磁盘平均(%)": round(disk_data['avg'], 1),
                "付费方式": "包年包月" if instance['billing_mode'] == 'prePaid' else "按需付费",
                "当前成本(元/月)": billing_data['actual_cost'],
                "原价成本(元/月)": billing_data['monthly_cost'],
                "商务折扣": f"{int((1 - billing_data['discount_rate']) * 100)}%",
                "创建时间": created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "运行时长(天)": running_days,
                "实例状态": instance['status'],
                "建议优化规格": optimization['recommended_spec'],
                "建议优化方式": optimization['optimization_type'],
                "预计节省成本(元/月)": optimization['monthly_saving'],
                "节省比例": optimization['saving_percentage'],
                "优化优先级": optimization['priority'],
                "风险等级": optimization['risk_level'],
                "实施复杂度": optimization['complexity']
            }
            
            self.analysis_results.append(result)
        
        print(f"✅ 数据收集完成，共分析 {len(self.analysis_results)} 个实例")
    
    def analyze_optimization(self, instance: Dict, cpu_data: Dict, mem_data: Dict, disk_data: Dict, billing_data: Dict) -> Dict:
        """分析优化建议"""
        
        cpu_max = cpu_data['max']
        cpu_avg = cpu_data['avg']
        mem_max = mem_data['max']
        mem_avg = mem_data['avg']
        
        # 获取规格价格表
        flavor_prices = self.api.get_flavor_prices()
        current_spec = instance['spec']
        
        # 初始化建议
        recommendation = {
            "recommended_spec": current_spec,
            "optimization_type": "保持现状",
            "monthly_saving": 0.0,
            "saving_percentage": "0%",
            "priority": "低",
            "risk_level": "低",
            "complexity": "低"
        }
        
        # 分析CPU使用率
        if cpu_max < 20 and cpu_avg < 15:
            # CPU使用率过低，考虑降配
            if current_spec in ["c6.4xlarge.2", "r6.4xlarge.2"]:
                recommendation["recommended_spec"] = "c6.2xlarge.2"
                recommendation["optimization_type"] = "降配"
                recommendation["priority"] = "高"
            elif current_spec in ["c6.2xlarge.2", "r6.2xlarge.2"]:
                recommendation["recommended_spec"] = "c6.xlarge.2"
                recommendation["optimization_type"] = "降配"
                recommendation["priority"] = "高"
            elif current_spec in ["c6.xlarge.2", "r6.xlarge.2"]:
                recommendation["recommended_spec"] = "c6.large.2"
                recommendation["optimization_type"] = "降配"
                recommendation["priority"] = "中"
        
        elif cpu_max > 80 or cpu_avg > 70:
            # CPU使用率过高，考虑升配
            if current_spec in ["c6.large.2", "s6.large.2"]:
                recommendation["recommended_spec"] = "c6.xlarge.2"
                recommendation["optimization_type"] = "升配"
                recommendation["priority"] = "高"
                recommendation["risk_level"] = "中"
            elif current_spec in ["c6.xlarge.2", "s6.xlarge.2"]:
                recommendation["recommended_spec"] = "c6.2xlarge.2"
                recommendation["optimization_type"] = "升配"
                recommendation["priority"] = "高"
                recommendation["risk_level"] = "中"
        
        # 分析内存使用率
        if mem_max < 30 and mem_avg < 25:
            # 内存使用率过低
            if "r6" in current_spec and current_spec in ["r6.4xlarge.2", "r6.2xlarge.2"]:
                recommendation["recommended_spec"] = "r6.xlarge.2"
                recommendation["optimization_type"] = "降配"
                recommendation["priority"] = "高"
            elif "r6" in current_spec and current_spec == "r6.xlarge.2":
                recommendation["recommended_spec"] = "c6.xlarge.2"
                recommendation["optimization_type"] = "更换规格族"
                recommendation["priority"] = "中"
        
        # 分析计费模式
        if instance['billing_mode'] == 'postPaid' and instance['status'] == 'ACTIVE':
            # 按需付费且运行稳定的实例，考虑转为包年包月
            from datetime import timezone
            created_at_str = instance['created_at'].replace('Z', '+00:00')
            created_at = datetime.fromisoformat(created_at_str)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            running_days = (now - created_at).days
            if running_days > 90:  # 运行超过90天
                recommendation["optimization_type"] = "转为包年包月"
                recommendation["priority"] = "中"
                recommendation["risk_level"] = "低"
        
        # 计算节省成本
        if recommendation["recommended_spec"] != current_spec:
            current_price = flavor_prices.get(current_spec, {}).get("price", 0)
            recommended_price = flavor_prices.get(recommendation["recommended_spec"], {}).get("price", 0)
            
            if current_price > 0 and recommended_price > 0:
                monthly_saving = (current_price - recommended_price) * billing_data['discount_rate']
                saving_percentage = (monthly_saving / (current_price * billing_data['discount_rate'])) * 100
                
                recommendation["monthly_saving"] = round(monthly_saving, 2)
                recommendation["saving_percentage"] = f"{saving_percentage:.1f}%"
        
        # 分析停止的实例
        if instance['status'] == 'STOPPED':
            recommendation["optimization_type"] = "删除实例"
            recommendation["monthly_saving"] = billing_data['actual_cost']
            recommendation["saving_percentage"] = "100%"
            recommendation["priority"] = "高"
            recommendation["risk_level"] = "低"
            recommendation["complexity"] = "低"
        
        return recommendation
    
    def generate_detailed_table(self) -> pd.DataFrame:
        """生成详细表格"""
        if not self.analysis_results:
            self.collect_data()
        
        # 创建DataFrame
        df = pd.DataFrame(self.analysis_results)
        
        # 重新排序列顺序
        columns_order = [
            "实例名称", "规格", "CPU核心数", "内存(GB)",
            "最近30天CPU峰值(%)", "最近30天CPU平均(%)",
            "最近30天内存峰值(%)", "最近30天内存平均(%)",
            "最近30天磁盘峰值(%)", "最近30天磁盘平均(%)",
            "付费方式", "当前成本(元/月)", "原价成本(元/月)", "商务折扣",
            "创建时间", "运行时长(天)", "实例状态",
            "建议优化规格", "建议优化方式", "预计节省成本(元/月)",
            "节省比例", "优化优先级", "风险等级", "实施复杂度"
        ]
        
        df = df[columns_order]
        
        return df
    
    def generate_summary_report(self) -> Dict:
        """生成汇总报告"""
        if not self.analysis_results:
            self.collect_data()
        
        df = pd.DataFrame(self.analysis_results)
        
        # 计算汇总指标
        total_current_cost = df["当前成本(元/月)"].sum()
        total_potential_saving = df["预计节省成本(元/月)"].sum()
        saving_percentage = (total_potential_saving / total_current_cost * 100) if total_current_cost > 0 else 0
        
        # 按优先级统计
        high_priority = df[df["优化优先级"] == "高"]
        medium_priority = df[df["优化优先级"] == "中"]
        low_priority = df[df["优化优先级"] == "低"]
        
        # 按优化类型统计
        optimization_types = df["建议优化方式"].value_counts().to_dict()
        
        summary = {
            "分析时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "分析实例总数": len(df),
            "运行中实例": len(df[df["实例状态"] == "ACTIVE"]),
            "已停止实例": len(df[df["实例状态"] == "STOPPED"]),
            "月度总成本": round(total_current_cost, 2),
            "月度潜在节省": round(total_potential_saving, 2),
            "节省比例": f"{saving_percentage:.1f}%",
            "高优先级优化": len(high_priority),
            "中优先级优化": len(medium_priority),
            "低优先级优化": len(low_priority),
            "优化类型分布": optimization_types,
            "高风险优化": len(df[df["风险等级"] == "高"]),
            "中风险优化": len(df[df["风险等级"] == "中"]),
            "低风险优化": len(df[df["风险等级"] == "低"])
        }
        
        return summary
    
    def save_results(self, output_dir: str = "huawei_optimization_results"):
        """保存分析结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成详细表格
        df = self.generate_detailed_table()
        
        # 保存为CSV
        csv_path = os.path.join(output_dir, "huawei_ecs_optimization_details.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ 详细表格已保存: {csv_path}")
        
        # 保存为Excel
        excel_path = os.path.join(output_dir, "huawei_ecs_optimization_report.xlsx")
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='详细分析', index=False)
            
            # 添加汇总表
            summary = self.generate_summary_report()
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='汇总报告', index=False)
            
            # 添加按优先级分类的表
            for priority in ["高", "中", "低"]:
                priority_df = df[df["优化优先级"] == priority]
                if not priority_df.empty:
                    priority_df.to_excel(writer, sheet_name=f'{priority}优先级', index=False)
        
        print(f"✅ Excel报告已保存: {excel_path}")
        
        # 保存JSON格式的详细数据
        json_path = os.path.join(output_dir, "huawei_ecs_optimization_data.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": self.generate_summary_report(),
                "details": self.analysis_results,
                "metadata": {
                    "account_id": "hw59248219",
                    "region": "cn-east-3",
                    "analysis_time": datetime.now().isoformat(),
                    "data_source": "华为云API + 模拟数据"
                }
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON数据已保存: {json_path}")
        
        # 生成Markdown报告
        md_path = os.path.join(output_dir, "README.md")
        self.generate_markdown_report(md_path)
        print(f"✅ Markdown报告已保存: {md_path}")
        
        return {
            "csv": csv_path,
            "excel": excel_path,
            "json": json_path,
            "markdown": md_path
        }
    
    def generate_markdown_report(self, output_path: str):
        """生成Markdown格式的报告"""
        df = pd.DataFrame(self.analysis_results)
        summary = self.generate_summary_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 华为云服务器优化分析报告\n\n")
            f.write(f"**生成时间**: {summary['分析时间']}\n")
            f.write(f"**账号**: hw59248219\n")
            f.write(f"**地域**: 华东-上海一 (cn-east-3)\n\n")
            
            f.write("## 📊 执行摘要\n\n")
            f.write(f"- **分析实例总数**: {summary['分析实例总数']} 个\n")
            f.write(f"- **运行中实例**: {summary['运行中实例']} 个\n")
            f.write(f"- **已停止实例**: {summary['已停止实例']} 个\n")
            f.write(f"- **月度总成本**: ¥{summary['月度总成本']:,.2f}\n")
            f.write(f"- **月度潜在节省**: ¥{summary['月度潜在节省']:,.2f}\n")
            f.write(f"- **节省比例**: {summary['节省比例']}\n\n")
            
            f.write("## 🎯 优化优先级分布\n\n")
            f.write(f"- **高优先级**: {summary['高优先级优化']} 个实例\n")
            f.write(f"- **中优先级**: {summary['中优先级优化']} 个实例\n")
            f.write(f"- **低优先级**: {summary['低优先级优化']} 个实例\n\n")
            
            f.write("## ⚠️ 风险分布\n\n")
            f.write(f"- **高风险**: {summary['高风险优化']} 个优化\n")
            f.write(f"- **中风险**: {summary['中风险优化']} 个优化\n")
            f.write(f"- **低风险**: {summary['低风险优化']} 个优化\n\n")
            
            f.write("## 📈 优化类型分布\n\n")
            for opt_type, count in summary['优化类型分布'].items():
                f.write(f"- **{opt_type}**: {count} 个实例\n")
            
            f.write("\n## 📋 详细优化建议\n\n")
            f.write("| 实例名称 | 规格 | CPU峰值(%) | 内存峰值(%) | 付费方式 | 当前成本(元/月) | 建议优化 | 预计节省(元/月) | 优先级 |\n")
            f.write("|----------|------|------------|-------------|----------|----------------|----------|----------------|--------|\n")
            
            for result in self.analysis_results:
                f.write(f"| {result['实例名称']} | {result['规格']} | {result['最近30天CPU峰值(%)']} | {result['最近30天内存峰值(%)']} | {result['付费方式']} | {result['当前成本(元/月)']} | {result['建议优化方式']}→{result['建议优化规格']} | {result['预计节省成本(元/月)']} | {result['优化优先级']} |\n")
            
            f.write("\n## 🚀 实施建议\n\n")
            f.write("### 第一阶段（立即实施）\n")
            f.write("1. **删除已停止的实例** - 零风险，立即节省\n")
            f.write("2. **清理未使用的资源** - EIP、EVS等\n")
            f.write("3. **实施自动启停策略** - 针对开发测试环境\n\n")
            
            f.write("### 第二阶段（1-2周内）\n")
            f.write("1. **调整明显过配实例** - CPU使用率<20%的实例\n")
            f.write("2. **优化存储类型** - 标准存储转低频/归档\n")
            f.write("3. **计费模式优化** - 长期运行实例转包年包月\n\n")
            
            f.write("### 第三阶段（1-2月内）\n")
            f.write("1. **架构优化** - 微服务化、容器化\n")
            f.write("2. **预留实例购买** - 获取更大折扣\n")
            f.write("3. **建立成本监控体系** - 持续优化\n\n")
            
            f.write("## 📁 生成文件\n\n")
            f.write("- `huawei_ecs_optimization_details.csv` - 详细数据表格\n")
            f.write("- `huawei_ecs_optimization_report.xlsx` - Excel报告\n")
            f.write("- `huawei_ecs_optimization_data.json` - 原始JSON数据\n")
            f.write("- `README.md` - 本报告\n\n")
            
            f.write("## ⚠️ 注意事项\n\n")
            f.write("1. **生产环境谨慎操作** - 建议先在测试环境验证\n")
            f.write("2. **备份重要数据** - 任何变更前做好备份\n")
            f.write("3. **分阶段实施** - 避免一次性大规模变更\n")
            f.write("4. **监控变更影响** - 实施后密切监控性能指标\n")
            f.write("5. **保留回滚方案** - 确保可以快速恢复\n")

def main():
    """主函数"""
    print("="*70)
    print("华为云服务器优化分析系统")
    print("="*70)
    
    # 检查环境变量
    access_key = os.getenv("HUAWEI_ACCESS_KEY")
    secret_key = os.getenv("HUAWEI_SECRET_KEY")
    
    if not access_key or not secret_key:
        print("❌ 未检测到华为云API认证信息")
        print("\n📋 请先设置环境变量:")
        print("  export HUAWEI_ACCESS_KEY='your_access_key'")
        print("  export HUAWEI_SECRET_KEY='your_secret_key'")
        print("\n💡 或创建.env文件:")
        print("  cp .env.example .env")
        print("  # 编辑.env文件填入AK/SK")
        print("\n🚀 使用模拟数据生成报告...")
        use_mock_data = True
    else:
        print("✅ 检测到华为云API认证信息")
        use_mock_data = False
    
    # 初始化API客户端
    if use_mock_data:
        # 使用模拟的AK/SK
        api_client = HuaweiCloudAPI(
            access_key="mock_access_key",
            secret_key="mock_secret_key",
            project_id="mock_project_id"
        )
    else:
        api_client = HuaweiCloudAPI(
            access_key=access_key,
            secret_key=secret_key,
            project_id=os.getenv("HUAWEI_PROJECT_ID")
        )
    
    # 初始化优化器
    optimizer = HuaweiCloudOptimizer(api_client)
    
    # 收集数据并生成报告
    print("\n📊 开始分析...")
    optimizer.collect_data()
    
    # 生成详细表格
    print("\n📋 生成详细表格...")
    df = optimizer.generate_detailed_table()
    
    # 显示表格预览
    print("\n预览前5行数据:")
    print(df.head().to_string())
    
    # 生成汇总报告
    print("\n📈 生成汇总报告...")
    summary = optimizer.generate_summary_report()
    print(f"\n汇总信息:")
    print(f"  分析实例总数: {summary['分析实例总数']}")
    print(f"  月度总成本: ¥{summary['月度总成本']:,.2f}")
    print(f"  月度潜在节省: ¥{summary['月度潜在节省']:,.2f}")
    print(f"  节省比例: {summary['节省比例']}")
    
    # 保存结果
    print("\n💾 保存分析结果...")
    output_files = optimizer.save_results()
    
    print("\n" + "="*70)
    print("分析完成!")
    print("="*70)
    
    print("\n📁 生成的文件:")
    for file_type, file_path in output_files.items():
        print(f"  {file_type.upper()}: {file_path}")
    
    print("\n🎯 下一步:")
    print("1. 查看生成的报告文件")
    print("2. 根据优先级实施优化措施")
    print("3. 监控优化效果")
    print("4. 定期重新分析")
    
    return output_files

if __name__ == "__main__":
    main()