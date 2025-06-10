#!/usr/bin/env python3
"""
AI Chat Service Automation - Logger Module
詳細なログ管理とパフォーマンス計測モジュール
"""

import logging
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager
import functools


class ColoredFormatter(logging.Formatter):
    """カラー付きログフォーマッター"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # シアン
        'INFO': '\033[32m',     # 緑
        'WARNING': '\033[33m',  # 黄
        'ERROR': '\033[31m',    # 赤
        'CRITICAL': '\033[35m', # マゼンタ
        'RESET': '\033[0m'      # リセット
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # カラーコードを追加
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON形式のログフォーマッター"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'filename': record.filename,
            'lineno': record.lineno,
            'funcName': record.funcName,
            'process': record.process,
            'thread': record.thread,
            'threadName': record.threadName
        }
        
        # 追加情報があれば含める
        if hasattr(record, 'extra_data'):
            log_entry['extra'] = record.extra_data
            
        return json.dumps(log_entry, ensure_ascii=False)


class AIAutomationLogger:
    """
    AIチャットサービス自動化専用ロガー
    
    主な機能:
    - 5段階のログレベル管理
    - ファイルとコンソールへの同時出力
    - パフォーマンス計測機能
    - 統計情報の管理
    - カラー付きコンソール出力
    - JSON形式ログ出力
    """
    
    def __init__(self, name: str, log_level: str = "INFO"):
        """
        ロガーの初期化
        
        Args:
            name: ロガー名
            log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # 重複ハンドラー防止
        if self.logger.handlers:
            return
            
        # ログディレクトリの作成
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # パフォーマンス統計
        self.performance_stats = {
            'operations': {},
            'total_operations': 0,
            'total_time': 0.0,
            'start_time': time.time()
        }
        
        # ハンドラーの設定
        self._setup_handlers()
        
        self.logger.info(f"Logger '{name}' initialized with level {log_level}")
    
    def _setup_handlers(self):
        """ログハンドラーの設定"""
        
        # 1. コンソールハンドラー（カラー付き）
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d in %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        
        # 2. ファイルハンドラー（詳細ログ）
        file_handler = logging.FileHandler(
            self.logs_dir / "app.log",
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [PID:%(process)d] [Thread:%(threadName)s] '
            '%(filename)s:%(lineno)d %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        
        # 3. エラー専用ハンドラー
        error_handler = logging.FileHandler(
            self.logs_dir / "error.log",
            encoding='utf-8'
        )
        error_handler.setFormatter(file_formatter)
        error_handler.setLevel(logging.ERROR)
        self.logger.addHandler(error_handler)
        
        # 4. JSON形式ハンドラー
        json_handler = logging.FileHandler(
            self.logs_dir / "app.json",
            encoding='utf-8'
        )
        json_handler.setFormatter(JSONFormatter())
        json_handler.setLevel(logging.INFO)
        self.logger.addHandler(json_handler)
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルの読み込み"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load config: {e}")
        return {}
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """DEBUGレベルログ"""
        self._log_with_extra(logging.DEBUG, message, extra)
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """INFOレベルログ"""
        self._log_with_extra(logging.INFO, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """WARNINGレベルログ"""
        self._log_with_extra(logging.WARNING, message, extra)
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = True):
        """ERRORレベルログ"""
        self._log_with_extra(logging.ERROR, message, extra, exc_info=exc_info)
    
    def critical(self, message: str, extra: Optional[Dict] = None):
        """CRITICALレベルログ"""
        self._log_with_extra(logging.CRITICAL, message, extra)
    
    def _log_with_extra(self, level: int, message: str, extra: Optional[Dict] = None, exc_info: bool = False):
        """追加情報付きログ出力"""
        if extra:
            # LogRecordに追加データを設定
            record = self.logger.makeRecord(
                self.logger.name, level, __file__, 0, message, (), exc_info
            )
            record.extra_data = extra
            self.logger.handle(record)
        else:
            self.logger.log(level, message, exc_info=exc_info)
    
    @contextmanager
    def log_performance(self, operation_name: str):
        """
        パフォーマンス計測コンテキストマネージャー
        
        Args:
            operation_name: 操作名
            
        Usage:
            with logger.log_performance("database_query"):
                # 計測対象の処理
                result = expensive_operation()
        """
        start_time = time.time()
        self.debug(f"Starting operation: {operation_name}")
        
        try:
            yield
        except Exception as e:
            self.error(f"Operation '{operation_name}' failed: {e}")
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            # 統計更新
            if operation_name not in self.performance_stats['operations']:
                self.performance_stats['operations'][operation_name] = {
                    'count': 0,
                    'total_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0,
                    'avg_time': 0.0
                }
            
            stats = self.performance_stats['operations'][operation_name]
            stats['count'] += 1
            stats['total_time'] += duration
            stats['min_time'] = min(stats['min_time'], duration)
            stats['max_time'] = max(stats['max_time'], duration)
            stats['avg_time'] = stats['total_time'] / stats['count']
            
            self.performance_stats['total_operations'] += 1
            self.performance_stats['total_time'] += duration
            
            self.info(
                f"Operation '{operation_name}' completed in {duration:.3f}s",
                extra={
                    'operation': operation_name,
                    'duration': duration,
                    'count': stats['count']
                }
            )
    
    def performance_decorator(self, operation_name: Optional[str] = None):
        """
        パフォーマンス計測デコレーター
        
        Args:
            operation_name: 操作名（Noneの場合は関数名を使用）
            
        Usage:
            @logger.performance_decorator("data_processing")
            def process_data():
                # 処理
                pass
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                with self.log_performance(op_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def log_performance_summary(self):
        """パフォーマンス統計情報の出力"""
        session_duration = time.time() - self.performance_stats['start_time']
        
        self.info("=== Performance Summary ===")
        self.info(f"Session duration: {session_duration:.1f}s")
        self.info(f"Total operations: {self.performance_stats['total_operations']}")
        self.info(f"Total operation time: {self.performance_stats['total_time']:.3f}s")
        
        if self.performance_stats['operations']:
            self.info("Operation breakdown:")
            for op_name, stats in self.performance_stats['operations'].items():
                self.info(
                    f"  {op_name}: {stats['count']} calls, "
                    f"avg: {stats['avg_time']:.3f}s, "
                    f"min: {stats['min_time']:.3f}s, "
                    f"max: {stats['max_time']:.3f}s"
                )
    
    def reset_performance_stats(self):
        """パフォーマンス統計のリセット"""
        self.performance_stats = {
            'operations': {},
            'total_operations': 0,
            'total_time': 0.0,
            'start_time': time.time()
        }
        self.info("Performance statistics reset")


# ロガーインスタンスの管理
_loggers: Dict[str, AIAutomationLogger] = {}


def get_logger(name: str, log_level: Optional[str] = None) -> AIAutomationLogger:
    """
    ロガーのファクトリー関数
    
    Args:
        name: ロガー名
        log_level: ログレベル（Noneの場合は設定ファイルから読み込み）
        
    Returns:
        AIAutomationLoggerインスタンス
        
    Usage:
        logger = get_logger("chatgpt_bot")
        logger.info("Application started")
    """
    # 既存インスタンスがあれば返す
    if name in _loggers:
        return _loggers[name]
    
    # ログレベルの決定
    if log_level is None:
        try:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                log_level = config.get("global_settings", {}).get("log_level", "INFO")
            else:
                log_level = "INFO"
        except Exception:
            log_level = "INFO"
    
    # 新しいロガーを作成
    logger = AIAutomationLogger(name, log_level)
    _loggers[name] = logger
    
    return logger


def get_all_loggers() -> Dict[str, AIAutomationLogger]:
    """すべてのロガーインスタンスを取得"""
    return _loggers.copy()


def reset_all_loggers():
    """すべてのロガーをリセット"""
    global _loggers
    for logger in _loggers.values():
        logger.reset_performance_stats()
    _loggers.clear()


if __name__ == "__main__":
    # テスト実行
    logger = get_logger("test_logger", "DEBUG")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # パフォーマンステスト
    with logger.log_performance("test_operation"):
        time.sleep(0.1)
    
    @logger.performance_decorator("test_function")
    def test_function():
        time.sleep(0.05)
        return "test result"
    
    result = test_function()
    logger.info(f"Function result: {result}")
    
    # 統計出力
    logger.log_performance_summary()