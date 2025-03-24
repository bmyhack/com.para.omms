"""
Prometheus API 客户端模块
提供与Prometheus服务交互的功能
"""
from prometheus_api_client import PrometheusConnect
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from .logger import info, debug, error
from .config import settings

class PrometheusClient:
    """Prometheus API客户端封装类"""
    
    def __init__(self, url: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """
        初始化Prometheus客户端
        
        Args:
            url: Prometheus服务器URL，如果为None则使用配置文件中的URL
            headers: 请求头，用于认证等
        """
        self.url = url or settings.PROMETHEUS_URL
        self.headers = headers or {}
        self.client = PrometheusConnect(url=self.url, headers=self.headers, disable_ssl=True)
        info(f"Prometheus客户端已初始化，连接到: {self.url}")
    
    def check_connection(self) -> bool:
        """
        检查与Prometheus服务器的连接
        
        Returns:
            连接成功返回True，否则返回False
        """
        try:
            self.client.check_prometheus_connection()
            info("Prometheus连接检查成功")
            return True
        except Exception as e:
            error(f"Prometheus连接检查失败: {str(e)}")
            return False
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """
        执行PromQL查询
        
        Args:
            query: PromQL查询语句
            
        Returns:
            查询结果列表
        """
        try:
            debug(f"执行Prometheus查询: {query}")
            result = self.client.custom_query(query=query)
            return result
        except Exception as e:
            error(f"Prometheus查询失败: {str(e)}")
            return []
    
    def query_range(self, 
                   query: str, 
                   start_time: Union[datetime, str], 
                   end_time: Union[datetime, str], 
                   step: str = "1m") -> List[Dict[str, Any]]:
        """
        执行PromQL范围查询
        
        Args:
            query: PromQL查询语句
            start_time: 开始时间，可以是datetime对象或ISO格式字符串
            end_time: 结束时间，可以是datetime对象或ISO格式字符串
            step: 步长，例如"1m"表示1分钟
            
        Returns:
            查询结果列表
        """
        try:
            debug(f"执行Prometheus范围查询: {query}, 从 {start_time} 到 {end_time}, 步长 {step}")
            result = self.client.custom_query_range(
                query=query,
                start_time=start_time,
                end_time=end_time,
                step=step
            )
            return result
        except Exception as e:
            error(f"Prometheus范围查询失败: {str(e)}")
            return []
    
    def get_metric_range_data(self, 
                             metric_name: str, 
                             label_config: Optional[Dict[str, str]] = None,
                             start_time: Union[datetime, str] = None, 
                             end_time: Union[datetime, str] = None, 
                             step: str = "1m") -> List[Dict[str, Any]]:
        """
        获取指定指标的范围数据
        
        Args:
            metric_name: 指标名称
            label_config: 标签配置，用于过滤指标
            start_time: 开始时间，默认为1小时前
            end_time: 结束时间，默认为当前时间
            step: 步长，例如"1m"表示1分钟
            
        Returns:
            查询结果列表
        """
        try:
            if start_time is None:
                start_time = datetime.now() - timedelta(hours=1)
            if end_time is None:
                end_time = datetime.now()
                
            debug(f"获取指标范围数据: {metric_name}, 标签: {label_config}")
            result = self.client.get_metric_range_data(
                metric_name=metric_name,
                label_config=label_config or {},
                start_time=start_time,
                end_time=end_time,
                step=step
            )
            return result
        except Exception as e:
            error(f"获取指标范围数据失败: {str(e)}")
            return []
    
    def get_current_metric_value(self, 
                               metric_name: str, 
                               label_config: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        获取指定指标的当前值
        
        Args:
            metric_name: 指标名称
            label_config: 标签配置，用于过滤指标
            
        Returns:
            查询结果列表
        """
        try:
            debug(f"获取指标当前值: {metric_name}, 标签: {label_config}")
            result = self.client.get_current_metric_value(
                metric_name=metric_name,
                label_config=label_config or {}
            )
            return result
        except Exception as e:
            error(f"获取指标当前值失败: {str(e)}")
            return []
    
    def get_all_metrics(self) -> List[str]:
        """
        获取所有可用的指标名称
        
        Returns:
            指标名称列表
        """
        try:
            debug("获取所有可用指标")
            result = self.client.all_metrics()
            return result
        except Exception as e:
            error(f"获取所有可用指标失败: {str(e)}")
            return []
    
    def get_metric_metadata(self, metric_name: str) -> Dict[str, Any]:
        """
        获取指标的元数据
        
        Args:
            metric_name: 指标名称
            
        Returns:
            指标元数据字典
        """
        try:
            debug(f"获取指标元数据: {metric_name}")
            result = self.client.get_metric_metadata(metric_name)
            return result
        except Exception as e:
            error(f"获取指标元数据失败: {str(e)}")
            return {}

# 创建默认客户端实例
prometheus_client = PrometheusClient()

# 导出模块内容
__all__ = ["PrometheusClient", "prometheus_client"]