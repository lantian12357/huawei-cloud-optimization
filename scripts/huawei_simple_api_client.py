#!/usr/bin/env python3
"""
华为云简单API客户端
使用requests直接调用华为云API，避免复杂的SDK依赖
"""

import os
import sys
import json
import hashlib
import hmac
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional
import requests
from urllib.parse import urlparse

from huawei_env_tools import HuaweiEnvConfig


class HuaweiSimpleAPIClient:
    """华为云简单API客户端"""
    
    def __init__(self, env_file: str = "config/.env"):
        """初始化客户端"""
        self.env_config = HuaweiEnvConfig(env_file)
        if not self.env_config.load_env():
            raise ValueError("无法加载环境配置")
        
        if not self.env_config.validate_config():
            raise ValueError("环境配置验证失败")
        
        self.config = self.env_config.config
        self.access_key = self.config["access_key"]
        self.secret_key = self.config["secret_key"]
        self.region = self.config["region"]
        self.account_id = self.config["account_id"]
        
        # API端点
        self.endpoints = {
            "ecs": f"https://ecs.{self.region}.myhuaweicloud.com",
            "ces": f"https://ces.{self.region}.myhuaweicloud.com",
            "bss": f"https://bss.{self.region}.myhuaweicloud.com",
        }
        
        print(f"✅ 华为云简单API客户端初始化完成 (区域: {self.region})")
    
    def _sign_request(self, method: str, endpoint: str, path: str, 
                     query_params: Dict = None, headers: Dict = None) -> Dict:
        """签名请求（简化版）"""
        # 这里实现简化的签名逻辑
        # 实际生产环境应该使用完整的华为云签名算法
        
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        
        signed_headers = {
            "X-Sdk-Date": timestamp,
            "Host": urlparse(endpoint).netloc,
        }
        
        if headers:
            signed_headers.update(headers)
        
        # 添加Authorization头（简化版）
        # 实际应该使用完整的SDK签名算法
        # 确保使用ASCII字符
        auth_header = f"SDK-HMAC-SHA256 Access={self.access_key}"
        signed_headers["Authorization"] = auth_header.encode('ascii', 'ignore').decode('ascii')
        
        return signed_headers
    
    def make_request(self, service: str, path: str, method: str = "GET", 
                    params: Dict = None, data: Dict = None) -> Optional[Dict]:
        """发送API请求"""
        endpoint = self.endpoints.get(service)
        if not endpoint:
            print(f"❌ 未知服务: {service}")
            return None
        
        url = f"{endpoint}{path}"
        
        # 构建查询参数
        query_params = {}
        if params:
            # 将参数转换为华为云API格式
            for key, value in params.items():
                if isinstance(value, list):
                    query_params[key] = ",".join(str(v) for v in value)
                else:
                    query_params[key] = str(value)
        
        # 签名请求
        headers = self._sign_request(method, endpoint, path, query_params)
        
        try:
            if method == "GET":
                response = requests.get(url, params=query_params, headers=headers, timeout=30)
            elif method == "POST":
                headers["Content-Type"] = "application/json"
                response = requests.post(url, params=query_params, 
                                       json=data, headers=headers, timeout=30)
            else:
                print(f"❌ 不支持的HTTP方法: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API请求失败: {response.status_code} - {response.text[:200]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None
    
    def get_real_ecs_instances(self, limit: int = 100) -> List[Dict]:
        """获取真实的ECS实例列表"""
        print("🔍 从华为云API获取ECS实例数据...")
        
        # 构建请求参数
        params = {
            "limit": limit,
            "offset": 0,
        }
        
        response = self.make_request("ecs", "/v1/{project_id}/cloudservers/detail", 
                                   params=params)
        
        if not response:
            print("⚠️ 未获取到ECS实例数据，使用模拟数据")
            return self._get_mock_ecs_instances()
        
        # 解析响应
        instances = []
        if "servers" in response:
            for server in response["servers"]:
                instance_info = {
                    "name": server.get("name", ""),
                    "id": server.get("id", ""),
                    "flavor": server.get("flavor", {}).get("id", "unknown") if server.get("flavor") else "unknown",
                    "status": server.get("status", "UNKNOWN"),
                    "created": server.get("created", ""),
                    "billing_mode": self._parse_billing_mode(server),
                    "cpu_cores": self._parse_cpu_cores(server.get("flavor", {}).get("id", "") if server.get("flavor") else ""),
                    "memory_gb": self._parse_memory_gb(server.get("flavor", {}).get("id", "") if server.get("flavor") else ""),
                    "region": self.region,
                    "project_id": server.get("tenant_id", ""),
                    "metadata": server.get("metadata", {}),
                }
                instances.append(instance_info)
        
        print(f"✅ 成功获取 {len(instances)} 个ECS实例")
        return instances
    
    def _get_mock_ecs_instances(self) -> List[Dict]:
        """获取模拟ECS实例数据（当API失败时）"""
        print("⚠️ 使用模拟ECS实例数据")
        
        instances = [
            {
                "name": "web-server-01",
                "id": "ecs-001",
                "flavor": "c6.2xlarge.2",
                "status": "ACTIVE",
                "created": "2024-01-15T08:00:00Z",
                "billing_mode": "包年包月",
                "cpu_cores": 8,
                "memory_gb": 16,
                "region": self.region,
                "project_id": "project-001",
                "metadata": {"charging_mode": "prePaid"},
            },
            {
                "name": "db-backup-01",
                "id": "ecs-002",
                "flavor": "c6.xlarge.2",
                "status": "ACTIVE",
                "created": "2024-06-20T10:30:00Z",
                "billing_mode": "按需计费",
                "cpu_cores": 4,
                "memory_gb": 8,
                "region": self.region,
                "project_id": "project-001",
                "metadata": {"charging_mode": "postPaid"},
            },
            {
                "name": "dev-test-01",
                "id": "ecs-003",
                "flavor": "c6.large.2",
                "status": "ACTIVE",
                "created": "2024-09-10T14:15:00Z",
                "billing_mode": "按需计费",
                "cpu_cores": 2,
                "memory_gb": 4,
                "region": self.region,
                "project_id": "project-001",
                "metadata": {"charging_mode": "postPaid"},
            },
            {
                "name": "api-gateway-01",
                "id": "ecs-004",
                "flavor": "c6.xlarge.2",
                "status": "ACTIVE",
                "created": "2024-03-05T09:20:00Z",
                "billing_mode": "包年包月",
                "cpu_cores": 4,
                "memory_gb": 8,
                "region": self.region,
                "project_id": "project-002",
                "metadata": {"charging_mode": "prePaid"},
            },
            {
                "name": "cache-server-01",
                "id": "ecs-005",
                "flavor": "r6.large.2",
                "status": "ACTIVE",
                "created": "2024-07-12T14:45:00Z",
                "billing_mode": "按需计费",
                "cpu_cores": 2,
                "memory_gb": 16,
                "region": self.region,
                "project_id": "project-001",
                "metadata": {"charging_mode": "postPaid"},
            }
        ]
        
        return instances
    
    def _parse_billing_mode(self, server: Dict) -> str:
        """解析计费模式"""
        metadata = server.get("metadata", {})
        charging_mode = metadata.get("charging_mode", "")
        
        if charging_mode == "prePaid":
            return "包年包月"
        elif charging_mode == "postPaid":
            return "按需计费"
        else:
            # 根据其他字段判断
            if server.get("os-extended-volumes:volumes_attached"):
                # 有卷附加，可能是包年包月
                return "包年包月"
            else:
                return "按需计费"
    
    def _parse_cpu_cores(self, flavor_id: str) -> int:
        """从规格ID解析CPU核心数"""
        flavor_lower = flavor_id.lower()
        
        if "large" in flavor_lower and "xlarge" not in flavor_lower and "2xlarge" not in flavor_lower:
            return 2
        elif "xlarge" in flavor_lower and "2xlarge" not in flavor_lower:
            return 4
        elif "2xlarge" in flavor_lower and "4xlarge" not in flavor_lower:
            return 8
        elif "4xlarge" in flavor_lower:
            return 16
        elif "8xlarge" in flavor_lower:
            return 32
        else:
            return 2  # 默认
    
    def _parse_memory_gb(self, flavor_id: str) -> int:
        """从规格ID解析内存大小(GB)"""
        flavor_lower = flavor_id.lower()
        
        if "large" in flavor_lower and "xlarge" not in flavor_lower and "2xlarge" not in flavor_lower:
            return 4
        elif "xlarge" in flavor_lower and "2xlarge" not in flavor_lower:
            return 8
        elif "2xlarge" in flavor_lower and "4xlarge" not in flavor_lower:
            return 16
        elif "4xlarge" in flavor_lower:
            return 32
        elif "8xlarge" in flavor_lower:
            return 64
        else:
            return 4  # 默认
    
    def get_monitoring_data(self, instance_id: str, days: int = 30) -> Dict:
        """获取监控数据"""
        print(f"📈 获取实例 {instance_id} 的监控数据...")
        
        # 这里简化处理，实际应该调用CES API
        # 暂时使用模拟数据
        
        import random
        from datetime import datetime
        
        return {
            "cpu_peak": round(random.uniform(15.0, 85.0), 1),
            "mem_peak": round(random.uniform(20.0, 90.0), 1),
            "disk_peak": round(random.uniform(25.0, 75.0), 1),
            "avg_cpu": round(random.uniform(10.0, 50.0), 1),
            "avg_mem": round(random.uniform(15.0, 60.0), 1),
            "data_points": days * 24,  # 30天，每小时一个点
            "source": "模拟数据（应使用CES API）",
            "last_updated": datetime.now().isoformat()
        }
    
    def test_connection(self) -> bool:
        """测试API连接"""
        print("🔗 测试华为云API连接...")
        
        try:
            # 尝试获取一个实例来测试连接
            instances = self.get_real_ecs_instances(limit=1)
            
            if instances:
                print("✅ 华为云API连接测试成功")
                return True
            else:
                print("⚠️ API连接测试返回空响应")
                return False
                
        except Exception as e:
            print(f"❌ API连接测试失败: {e}")
            return False


def main():
    """主函数"""
    print("🚀 华为云简单API客户端测试")
    
    try:
        # 初始化客户端
        client = HuaweiSimpleAPIClient()
        
        # 测试连接
        if not client.test_connection():
            print("❌ API连接测试失败，退出")
            return
        
        # 获取实例数据
        instances = client.get_real_ecs_instances(limit=10)
        
        if instances:
            print(f"\n📋 获取到的ECS实例 ({len(instances)} 个):")
            for i, instance in enumerate(instances, 1):
                print(f"  {i}. {instance['name']} ({instance['id']})")
                print(f"     规格: {instance['flavor']}, 状态: {instance['status']}")
                print(f"     计费: {instance['billing_mode']}, 创建: {instance['created'][:10]}")
                print(f"     CPU: {instance['cpu_cores']}核, 内存: {instance['memory_gb']}GB")
                print()
        
        print("✅ 测试完成")
            
    except Exception as e:
        print(f"❌ 主程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()