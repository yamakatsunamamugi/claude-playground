"""
AI Chat Service Automation - Element Finder Module
高度な要素検索・操作モジュール
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, ElementNotInteractableException
)
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum
import logging

# Import custom exceptions and logger
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.exceptions import SelectorNotFoundError
from .logger import get_logger


class FindStrategy(Enum):
    """要素検索戦略の定義"""
    PRESENCE = "presence_of_element_located"
    VISIBLE = "visibility_of_element_located"
    CLICKABLE = "element_to_be_clickable"
    TEXT_PRESENT = "text_to_be_present_in_element"
    ATTRIBUTE_PRESENT = "presence_of_element_attribute"


class ElementFinder:
    """
    Seleniumを使用した高度な要素検索・操作クラス
    
    主な機能:
    - 複数セレクタによるフォールバック検索
    - リトライ機構付き安全操作
    - 統計情報の収集と管理
    - 人間らしい操作パターン
    """
    
    def __init__(self, driver: webdriver.Chrome, default_timeout: int = 10):
        """
        ElementFinderの初期化
        
        Args:
            driver: WebDriverインスタンス
            default_timeout: デフォルトタイムアウト（秒）
        """
        self.driver = driver
        self.default_timeout = default_timeout
        self.logger = get_logger("element_finder")
        
        # 統計情報の初期化
        self.statistics = {
            'total_searches': 0,
            'successful_searches': 0,
            'failed_searches': 0,
            'selector_usage': {},
            'strategy_success_rate': {},
            'retry_counts': {
                'click': 0,
                'send_keys': 0,
                'get_text': 0
            },
            'timing': {
                'fastest_search': float('inf'),
                'slowest_search': 0,
                'average_search_time': 0
            }
        }
        
        # 各戦略の初期化
        for strategy in FindStrategy:
            self.statistics['strategy_success_rate'][strategy.value] = {
                'attempts': 0,
                'successes': 0
            }
    
    def find_element_with_fallback(
        self, 
        selectors: List[str], 
        strategy: FindStrategy = FindStrategy.PRESENCE,
        timeout: int = None
    ) -> Tuple[Optional[Any], Optional[str]]:
        """
        複数セレクタを使用したフォールバック要素検索
        
        Args:
            selectors: 試行するセレクタのリスト
            strategy: 検索戦略
            timeout: タイムアウト（秒）
            
        Returns:
            Tuple[WebElement, str]: 発見された要素と使用されたセレクタ
            
        Raises:
            SelectorNotFoundError: すべてのセレクタで要素が見つからない場合
        """
        search_start_time = time.time()
        timeout = timeout or self.default_timeout
        
        self.statistics['total_searches'] += 1
        self.statistics['strategy_success_rate'][strategy.value]['attempts'] += 1
        
        self.logger.debug(f"Starting element search with {len(selectors)} selectors using {strategy.value}")
        
        for i, selector in enumerate(selectors):
            try:
                self.logger.debug(f"Trying selector {i+1}/{len(selectors)}: {selector}")
                
                # セレクタ使用統計を更新
                if selector not in self.statistics['selector_usage']:
                    self.statistics['selector_usage'][selector] = {'attempts': 0, 'successes': 0}
                self.statistics['selector_usage'][selector]['attempts'] += 1
                
                # 戦略に応じた要素検索
                element = self._find_element_by_strategy(selector, strategy, timeout)
                
                if element:
                    # 成功統計を更新
                    search_time = time.time() - search_start_time
                    self._update_success_statistics(selector, strategy, search_time)
                    
                    self.logger.info(f"Element found with selector: {selector} (attempt {i+1})")
                    return element, selector
                    
            except TimeoutException:
                self.logger.debug(f"Timeout for selector: {selector}")
                continue
            except Exception as e:
                self.logger.warning(f"Error with selector {selector}: {e}")
                continue
        
        # すべてのセレクタで失敗
        self.statistics['failed_searches'] += 1
        self.logger.error(f"All selectors failed: {selectors}")
        raise SelectorNotFoundError(selectors, "unknown")
    
    def find_elements_with_fallback(
        self, 
        selectors: List[str], 
        strategy: FindStrategy = FindStrategy.PRESENCE,
        timeout: int = None
    ) -> Tuple[List[Any], Optional[str]]:
        """
        複数セレクタを使用した複数要素検索
        
        Args:
            selectors: 試行するセレクタのリスト
            strategy: 検索戦略
            timeout: タイムアウト（秒）
            
        Returns:
            Tuple[List[WebElement], str]: 発見された要素リストと使用されたセレクタ
        """
        timeout = timeout or self.default_timeout
        
        for selector in selectors:
            try:
                if strategy == FindStrategy.PRESENCE:
                    elements = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                elif strategy == FindStrategy.VISIBLE:
                    elements = WebDriverWait(self.driver, timeout).until(
                        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                else:
                    # その他の戦略では単一要素検索を使用してリスト化
                    element, _ = self.find_element_with_fallback([selector], strategy, timeout)
                    elements = [element] if element else []
                
                if elements:
                    self.logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    return elements, selector
                    
            except TimeoutException:
                continue
            except Exception as e:
                self.logger.warning(f"Error finding elements with selector {selector}: {e}")
                continue
        
        self.logger.warning(f"No elements found with any selector: {selectors}")
        return [], None
    
    def safe_click(
        self, 
        element_or_selectors: Union[Any, List[str]], 
        retry_count: int = 3,
        scroll_to_element: bool = True
    ) -> bool:
        """
        安全なクリック操作（リトライ機構付き）
        
        Args:
            element_or_selectors: WebElement または セレクタリスト
            retry_count: リトライ回数
            scroll_to_element: 要素までスクロールするか
            
        Returns:
            bool: クリック成功フラグ
        """
        element = self._resolve_element(element_or_selectors)
        if not element:
            return False
        
        for attempt in range(retry_count + 1):
            try:
                if scroll_to_element:
                    self.scroll_to_element(element)
                
                # 要素がクリック可能になるまで待機
                WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(element)
                )
                
                # JavaScript を使用した安全なクリック
                self.driver.execute_script("arguments[0].click();", element)
                
                self.logger.info(f"Click successful on attempt {attempt + 1}")
                return True
                
            except StaleElementReferenceException:
                self.logger.warning(f"Stale element on click attempt {attempt + 1}, re-finding element")
                element = self._resolve_element(element_or_selectors)
                if not element:
                    break
                continue
                
            except ElementNotInteractableException:
                self.logger.warning(f"Element not interactable on attempt {attempt + 1}")
                time.sleep(0.5)
                continue
                
            except Exception as e:
                self.logger.warning(f"Click failed on attempt {attempt + 1}: {e}")
                if attempt == retry_count:
                    break
                time.sleep(0.5)
        
        self.statistics['retry_counts']['click'] += retry_count
        self.logger.error(f"Click failed after {retry_count + 1} attempts")
        return False
    
    def safe_send_keys(
        self, 
        element_or_selectors: Union[Any, List[str]], 
        text: str,
        clear_first: bool = True,
        retry_count: int = 3
    ) -> bool:
        """
        安全なテキスト入力操作（人間らしいタイピング）
        
        Args:
            element_or_selectors: WebElement または セレクタリスト
            text: 入力するテキスト
            clear_first: 入力前にクリアするか
            retry_count: リトライ回数
            
        Returns:
            bool: 入力成功フラグ
        """
        element = self._resolve_element(element_or_selectors)
        if not element:
            return False
        
        for attempt in range(retry_count + 1):
            try:
                # 要素をクリックしてフォーカス
                if not self.safe_click(element, scroll_to_element=True):
                    continue
                
                # 既存テキストをクリア
                if clear_first:
                    element.clear()
                    # 追加のクリア処理（一部のサイトで必要）
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.DELETE)
                
                # 人間らしいタイピングでテキスト入力
                self._human_like_typing(element, text)
                
                self.logger.info(f"Text input successful on attempt {attempt + 1}")
                return True
                
            except StaleElementReferenceException:
                self.logger.warning(f"Stale element on send_keys attempt {attempt + 1}")
                element = self._resolve_element(element_or_selectors)
                if not element:
                    break
                continue
                
            except Exception as e:
                self.logger.warning(f"Send keys failed on attempt {attempt + 1}: {e}")
                if attempt == retry_count:
                    break
                time.sleep(0.5)
        
        self.statistics['retry_counts']['send_keys'] += retry_count
        self.logger.error(f"Send keys failed after {retry_count + 1} attempts")
        return False
    
    def safe_get_text(
        self, 
        element_or_selectors: Union[Any, List[str]], 
        retry_count: int = 3
    ) -> Optional[str]:
        """
        安全なテキスト取得操作
        
        Args:
            element_or_selectors: WebElement または セレクタリスト
            retry_count: リトライ回数
            
        Returns:
            Optional[str]: 取得されたテキスト
        """
        element = self._resolve_element(element_or_selectors)
        if not element:
            return None
        
        for attempt in range(retry_count + 1):
            try:
                text = element.text.strip()
                if text:
                    self.logger.debug(f"Text retrieved successfully: {text[:50]}...")
                    return text
                
                # innerTextも試行
                text = self.driver.execute_script("return arguments[0].innerText;", element)
                if text:
                    return text.strip()
                
                # textContentも試行
                text = self.driver.execute_script("return arguments[0].textContent;", element)
                if text:
                    return text.strip()
                    
            except StaleElementReferenceException:
                self.logger.warning(f"Stale element on get_text attempt {attempt + 1}")
                element = self._resolve_element(element_or_selectors)
                if not element:
                    break
                continue
                
            except Exception as e:
                self.logger.warning(f"Get text failed on attempt {attempt + 1}: {e}")
                if attempt == retry_count:
                    break
                time.sleep(0.2)
        
        self.statistics['retry_counts']['get_text'] += retry_count
        self.logger.warning(f"Text retrieval failed after {retry_count + 1} attempts")
        return None
    
    def wait_for_element_to_disappear(
        self, 
        selectors: List[str], 
        timeout: int = None
    ) -> bool:
        """
        要素の消失を待機
        
        Args:
            selectors: 監視するセレクタリスト
            timeout: タイムアウト（秒）
            
        Returns:
            bool: 消失確認フラグ
        """
        timeout = timeout or self.default_timeout
        
        for selector in selectors:
            try:
                WebDriverWait(self.driver, timeout).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                self.logger.info(f"Element disappeared: {selector}")
                return True
            except TimeoutException:
                continue
            except Exception as e:
                self.logger.warning(f"Error waiting for disappearance of {selector}: {e}")
                continue
        
        self.logger.warning(f"Elements did not disappear within timeout: {selectors}")
        return False
    
    def scroll_to_element(self, element: Any) -> bool:
        """
        要素までスクロール
        
        Args:
            element: スクロール対象の要素
            
        Returns:
            bool: スクロール成功フラグ
        """
        try:
            # JavaScriptを使用したスムーズスクロール
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                element
            )
            time.sleep(0.5)  # スクロール完了を待機
            return True
        except Exception as e:
            self.logger.warning(f"Scroll to element failed: {e}")
            return False
    
    def log_search_statistics(self) -> None:
        """検索統計情報をログ出力"""
        stats = self.statistics
        
        self.logger.info("=== ElementFinder Statistics ===")
        self.logger.info(f"Total searches: {stats['total_searches']}")
        self.logger.info(f"Successful searches: {stats['successful_searches']}")
        self.logger.info(f"Failed searches: {stats['failed_searches']}")
        
        if stats['total_searches'] > 0:
            success_rate = (stats['successful_searches'] / stats['total_searches']) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        # タイミング統計
        timing = stats['timing']
        if timing['fastest_search'] != float('inf'):
            self.logger.info(f"Fastest search: {timing['fastest_search']:.3f}s")
            self.logger.info(f"Slowest search: {timing['slowest_search']:.3f}s")
            self.logger.info(f"Average search time: {timing['average_search_time']:.3f}s")
        
        # セレクタ使用統計（上位5つ）
        self.logger.info("Top 5 selectors by usage:")
        sorted_selectors = sorted(
            stats['selector_usage'].items(),
            key=lambda x: x[1]['attempts'],
            reverse=True
        )[:5]
        
        for selector, usage_stats in sorted_selectors:
            success_rate = (usage_stats['successes'] / usage_stats['attempts']) * 100
            self.logger.info(
                f"  {selector}: {usage_stats['attempts']} attempts, "
                f"{success_rate:.1f}% success rate"
            )
        
        # 戦略別成功率
        self.logger.info("Strategy success rates:")
        for strategy, strategy_stats in stats['strategy_success_rate'].items():
            if strategy_stats['attempts'] > 0:
                success_rate = (strategy_stats['successes'] / strategy_stats['attempts']) * 100
                self.logger.info(f"  {strategy}: {success_rate:.1f}%")
        
        # リトライ統計
        retry_counts = stats['retry_counts']
        total_retries = sum(retry_counts.values())
        if total_retries > 0:
            self.logger.info(f"Total retries performed: {total_retries}")
            for operation, count in retry_counts.items():
                self.logger.info(f"  {operation}: {count} retries")
    
    def reset_statistics(self) -> None:
        """統計情報をリセット"""
        self.__init__(self.driver, self.default_timeout)
        self.logger.info("Statistics reset")
    
    def save_statistics(self, filepath: str) -> bool:
        """
        統計情報をファイルに保存
        
        Args:
            filepath: 保存先ファイルパス
            
        Returns:
            bool: 保存成功フラグ
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.statistics, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Statistics saved to: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save statistics: {e}")
            return False
    
    def load_statistics(self, filepath: str) -> bool:
        """
        統計情報をファイルから読み込み
        
        Args:
            filepath: 読み込み元ファイルパス
            
        Returns:
            bool: 読み込み成功フラグ
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.statistics = json.load(f)
            self.logger.info(f"Statistics loaded from: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load statistics: {e}")
            return False
    
    # プライベートメソッド
    
    def _find_element_by_strategy(
        self, 
        selector: str, 
        strategy: FindStrategy, 
        timeout: int
    ) -> Optional[Any]:
        """
        指定された戦略で要素を検索
        
        Args:
            selector: CSSセレクタ
            strategy: 検索戦略
            timeout: タイムアウト
            
        Returns:
            Optional[WebElement]: 発見された要素
        """
        wait = WebDriverWait(self.driver, timeout)
        
        try:
            if strategy == FindStrategy.PRESENCE:
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif strategy == FindStrategy.VISIBLE:
                return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
            elif strategy == FindStrategy.CLICKABLE:
                return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            elif strategy == FindStrategy.TEXT_PRESENT:
                # テキスト存在確認は特別な処理が必要
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif strategy == FindStrategy.ATTRIBUTE_PRESENT:
                # 属性存在確認も特別な処理が必要
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            else:
                # デフォルトはPRESENCE
                return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                
        except TimeoutException:
            return None
    
    def _resolve_element(self, element_or_selectors: Union[Any, List[str]]) -> Optional[Any]:
        """
        要素またはセレクタリストから要素を解決
        
        Args:
            element_or_selectors: WebElement または セレクタリスト
            
        Returns:
            Optional[WebElement]: 解決された要素
        """
        if isinstance(element_or_selectors, list):
            # セレクタリストの場合は検索実行
            element, _ = self.find_element_with_fallback(element_or_selectors)
            return element
        else:
            # 既にWebElementの場合はそのまま返す
            return element_or_selectors
    
    def _human_like_typing(self, element: Any, text: str) -> None:
        """
        人間らしいタイピングパターンで文字入力
        
        Args:
            element: 入力対象の要素
            text: 入力するテキスト
        """
        import random
        
        for char in text:
            element.send_keys(char)
            # ランダムな遅延（30-100ms）で人間らしさを演出
            delay = random.uniform(0.03, 0.1)
            time.sleep(delay)
    
    def _update_success_statistics(
        self, 
        selector: str, 
        strategy: FindStrategy, 
        search_time: float
    ) -> None:
        """
        成功統計情報を更新
        
        Args:
            selector: 成功したセレクタ
            strategy: 使用した戦略
            search_time: 検索にかかった時間
        """
        # 基本統計
        self.statistics['successful_searches'] += 1
        
        # セレクタ統計
        self.statistics['selector_usage'][selector]['successes'] += 1
        
        # 戦略統計
        self.statistics['strategy_success_rate'][strategy.value]['successes'] += 1
        
        # タイミング統計
        timing = self.statistics['timing']
        timing['fastest_search'] = min(timing['fastest_search'], search_time)
        timing['slowest_search'] = max(timing['slowest_search'], search_time)
        
        # 平均時間の更新
        total_searches = self.statistics['successful_searches']
        current_avg = timing['average_search_time']
        new_avg = ((current_avg * (total_searches - 1)) + search_time) / total_searches
        timing['average_search_time'] = new_avg