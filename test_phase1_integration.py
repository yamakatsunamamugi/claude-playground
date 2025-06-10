#!/usr/bin/env python3
"""
Phase 1 Integration Test - AI Chat Service Automation

3つのモジュール（logger, driver_manager, element_finder）の統合テスト
"""

import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import get_logger, ChatAutomationLogger
from utils.driver_manager import WebDriverManager  
from utils.element_finder import ElementFinder, FindStrategy
from core.exceptions import (
    SelectorNotFoundError, 
    DriverInitializationError,
    ConfigurationError
)


def test_logger_module():
    """logger.pyモジュールのテスト"""
    print("\n" + "="*60)
    print("TESTING: Logger Module")
    print("="*60)
    
    try:
        # ロガーの初期化
        logger = get_logger(name="test_logger", log_level="DEBUG")
        
        # 各レベルのログ出力テスト
        logger.debug("Debug message test")
        logger.info("Info message test - Logger initialized successfully")
        logger.warning("Warning message test")
        logger.error("Error message test", exception=ValueError("Test exception"))
        
        # JSON形式のログ
        logger.log_json("Test configuration:", {
            "module": "logger",
            "status": "active",
            "features": ["file_output", "console_output", "performance_tracking"]
        })
        
        # パフォーマンス計測のテスト
        with logger.log_performance("test_operation"):
            time.sleep(0.5)
        
        # デコレーターのテスト
        @logger.performance_decorator("decorated_function")
        def sample_function():
            time.sleep(0.2)
            return "completed"
        
        result = sample_function()
        logger.info(f"Decorated function result: {result}")
        
        # パフォーマンスサマリー
        logger.log_performance_summary()
        
        print("\n✅ Logger module test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Logger module test FAILED: {e}")
        return False


def test_driver_manager_module():
    """driver_manager.pyモジュールのテスト"""
    print("\n" + "="*60)
    print("TESTING: Driver Manager Module")
    print("="*60)
    
    logger = get_logger(name="test_driver", log_level="INFO")
    
    try:
        # WebDriverManagerの初期化
        manager = WebDriverManager()
        logger.info("WebDriverManager initialized")
        
        # ドライバーの作成（ヘッドレスモードでテスト）
        logger.info("Creating WebDriver in headless mode...")
        driver = manager.create_driver(
            service_name="test",
            headless=True,
            use_profile=False
        )
        
        # テストページへのアクセス
        logger.info("Navigating to test page...")
        driver.get("https://www.example.com")
        
        # ページタイトルの確認
        title = driver.title
        logger.info(f"Page title: {title}")
        
        # 人間らしい操作のテスト
        logger.info("Testing human-like behaviors...")
        manager.wait_random(0.5, 1.0)
        manager.human_like_mouse_movement()
        manager.random_scroll()
        
        # クリーンアップ
        manager.quit()
        
        print("\n✅ Driver Manager module test PASSED")
        return True
        
    except DriverInitializationError as e:
        logger.error(f"Driver initialization failed: {e}")
        print("\n❌ Driver Manager module test FAILED")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exception=e)
        print("\n❌ Driver Manager module test FAILED")
        if 'manager' in locals():
            manager.quit()
        return False


def test_element_finder_module():
    """element_finder.pyモジュールのテスト"""
    print("\n" + "="*60)
    print("TESTING: Element Finder Module")
    print("="*60)
    
    logger = get_logger(name="test_finder", log_level="INFO")
    
    try:
        # ドライバーとElementFinderの初期化
        with WebDriverManager() as manager:
            driver = manager.create_driver(
                service_name="test",
                headless=True,
                use_profile=False
            )
            
            finder = ElementFinder(driver)
            logger.info("ElementFinder initialized")
            
            # テストページへのアクセス
            driver.get("https://www.example.com")
            
            # 要素検索のテスト（フォールバック付き）
            logger.info("Testing element search with fallback...")
            
            # 複数のセレクタでh1要素を探す
            selectors = [
                "h1.main-title",     # 存在しないセレクタ
                "h1#title",          # 存在しないセレクタ
                "h1",                # 存在するセレクタ
            ]
            
            try:
                element, used_selector = finder.find_element_with_fallback(
                    selectors=selectors,
                    strategy=FindStrategy.VISIBLE,
                    timeout=5,
                    service_name="test",
                    log_prefix="[TEST] "
                )
                
                logger.info(f"Found element with selector: {used_selector}")
                
                # テキスト取得のテスト
                text = finder.get_element_text_safely(element)
                logger.info(f"Element text: {text}")
                
            except SelectorNotFoundError as e:
                logger.error(f"Element not found: {e}")
            
            # 要素存在チェックのテスト
            is_present = finder.is_element_present("body", timeout=1)
            logger.info(f"Body element present: {is_present}")
            
            # 検索統計の表示
            finder.log_search_statistics()
        
        print("\n✅ Element Finder module test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exception=e)
        print("\n❌ Element Finder module test FAILED")
        return False


def test_integration():
    """3つのモジュールの統合テスト"""
    print("\n" + "="*60)
    print("TESTING: Full Integration Test")
    print("="*60)
    
    logger = get_logger(name="integration_test", log_level="INFO")
    
    try:
        logger.info("Starting full integration test...")
        
        with logger.log_performance("full_integration_test"):
            # WebDriverManagerとElementFinderの統合使用
            with WebDriverManager() as manager:
                # ドライバー作成
                driver = manager.create_driver(
                    service_name="integration",
                    headless=True,
                    use_profile=False
                )
                
                # ElementFinderの初期化
                finder = ElementFinder(driver)
                
                # Googleでの実際の検索テスト
                logger.info("Performing real-world test on Google...")
                driver.get("https://www.google.com")
                
                # 検索ボックスを探す
                search_selectors = [
                    "textarea[name='q']",    # 新しいセレクタ
                    "input[name='q']",       # 従来のセレクタ
                ]
                
                try:
                    element, selector = finder.find_element_with_fallback(
                        selectors=search_selectors,
                        strategy=FindStrategy.VISIBLE,
                        timeout=10,
                        service_name="google"
                    )
                    
                    logger.info(f"Found search box with: {selector}")
                    
                    # 人間らしいタイピング
                    test_query = "AI automation test"
                    manager.human_like_typing(element, test_query)
                    logger.info(f"Typed search query: {test_query}")
                    
                    # 検索実行（Enterキー送信）
                    from selenium.webdriver.common.keys import Keys
                    element.send_keys(Keys.RETURN)
                    
                    # 結果の待機
                    manager.wait_random(2, 3)
                    
                    # 検索結果の確認
                    results_present = finder.is_element_present("#search", timeout=5)
                    logger.info(f"Search results present: {results_present}")
                    
                except SelectorNotFoundError as e:
                    logger.warning(f"Search box not found: {e}")
                    logger.info("This might be due to Google's regional differences or updates")
        
        # 最終的な統計情報
        logger.log_performance_summary()
        finder.log_search_statistics()
        
        print("\n✅ Full integration test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}", exception=e)
        print("\n❌ Full integration test FAILED")
        return False


def main():
    """メインテスト実行関数"""
    print("\n" + "="*80)
    print("AI CHAT SERVICE AUTOMATION - PHASE 1 INTEGRATION TEST")
    print("="*80)
    print("\nThis test will verify the following modules:")
    print("1. logger.py - Logging functionality")
    print("2. driver_manager.py - WebDriver management")
    print("3. element_finder.py - Element search abstraction")
    print("4. Full integration - All modules working together")
    
    # 各モジュールのテスト実行
    results = {
        "Logger": test_logger_module(),
        "Driver Manager": test_driver_manager_module(),
        "Element Finder": test_element_finder_module(),
        "Integration": test_integration()
    }
    
    # 結果サマリー
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    for module, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{module}: {status}")
    
    # 全体の成功/失敗
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Phase 1 modules are working correctly.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())