"""
AI Chat Service Automation - WebDriver Manager
"""

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import random
import json
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging

from ..core.exceptions import DriverInitializationError, ConfigurationError


class WebDriverManager:
    """
    WebDriver Manager for AI Chat Services
    
    Features:
    - Stealth mode with undetected-chromedriver
    - Service-specific profiles
    - Human-like behavior simulation
    - Context manager support
    - Robust error handling
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize WebDriverManager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or "config/config.json"
        self.config = self._load_config()
        self.global_settings = self.config.get('global_settings', {})
        self.drivers: Dict[str, webdriver.Chrome] = {}
        self.logger = logging.getLogger(__name__)
        
        # Create profiles directory
        self.profiles_dir = Path("profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.logger.info("WebDriverManager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        Returns:
            Dict containing configuration
            
        Raises:
            ConfigurationError: If config file cannot be loaded
        """
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                raise ConfigurationError(
                    "config_file", 
                    f"Configuration file not found: {self.config_path}"
                )
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required sections
            required_sections = ['global_settings']
            for section in required_sections:
                if section not in config:
                    raise ConfigurationError(
                        section, 
                        f"Required section '{section}' not found in config"
                    )
            
            return config
            
        except json.JSONDecodeError as e:
            raise ConfigurationError("json_parse", f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigurationError("config_load", f"Failed to load config: {e}")
    
    def create_driver(
        self, 
        service_name: str, 
        headless: Optional[bool] = None
    ) -> webdriver.Chrome:
        """
        Create WebDriver instance for specified service
        
        Args:
            service_name: Service name (chatgpt, gemini, claude)
            headless: Override headless mode setting
            
        Returns:
            Chrome WebDriver instance
            
        Raises:
            DriverInitializationError: If driver creation fails
        """
        try:
            self.logger.info(f"Creating driver for service: {service_name}")
            
            # Validate service
            if service_name not in ['chatgpt', 'gemini', 'claude']:
                raise DriverInitializationError(
                    service_name, 
                    Exception(f"Unsupported service: {service_name}")
                )
            
            # Create options
            options = self.create_profile_options(service_name, headless)
            
            # Create driver with undetected-chromedriver
            driver = uc.Chrome(
                options=options,
                version_main=None,  # Auto-detect Chrome version
                driver_executable_path=None,  # Auto-download if needed
            )
            
            # Apply stealth mode
            self.setup_stealth_mode(driver)
            
            # Set window size
            window_size = self.global_settings.get('window_size', {})
            width = window_size.get('width', 1280)
            height = window_size.get('height', 720)
            driver.set_window_size(width, height)
            
            # Store driver reference
            self.drivers[service_name] = driver
            
            self.logger.info(f"Driver created successfully for {service_name}")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to create driver for {service_name}: {e}")
            raise DriverInitializationError(service_name, e)
    
    def setup_stealth_mode(self, driver: webdriver.Chrome) -> None:
        """
        Setup stealth mode to avoid detection
        
        Args:
            driver: Chrome WebDriver instance
        """
        try:
            self.logger.debug("Setting up stealth mode")
            
            # Remove webdriver property
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
            """)
            
            # Remove chrome-specific properties
            driver.execute_script("""
                // Remove chrome property
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                    configurable: true
                });
                
                // Remove chrome automation indicators
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Override permissions API
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # Set realistic viewport
            driver.execute_script("""
                Object.defineProperty(screen, 'availHeight', {
                    get: () => 1080
                });
                Object.defineProperty(screen, 'availWidth', {
                    get: () => 1920
                });
            """)
            
            self.logger.debug("Stealth mode setup completed")
            
        except Exception as e:
            self.logger.warning(f"Stealth mode setup failed: {e}")
    
    def create_profile_options(
        self, 
        service_name: str, 
        headless: Optional[bool] = None
    ) -> Options:
        """
        Create Chrome options with service-specific profile
        
        Args:
            service_name: Service name
            headless: Override headless mode
            
        Returns:
            Chrome options instance
        """
        options = Options()
        
        # Determine headless mode
        if headless is None:
            # GitHub Actions環境検出
            import os
            if os.getenv('GITHUB_ACTIONS') or os.getenv('HEADLESS'):
                headless = True
            else:
                headless = self.global_settings.get('headless', False)
        
        if headless:
            options.add_argument('--headless=new')
            self.logger.info("Running in headless mode")
        
        # Service-specific profile directory
        profile_dir = self.profiles_dir / f"{service_name}_profile"
        profile_dir.mkdir(exist_ok=True)
        options.add_argument(f'--user-data-dir={profile_dir}')
        
        # Stealth arguments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        user_agent = self.global_settings.get(
            'user_agent',
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        options.add_argument(f'--user-agent={user_agent}')
        
        # Additional options for stability
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # Performance options
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        self.logger.debug(f"Profile options created for {service_name}")
        return options
    
    def human_like_typing(
        self, 
        element, 
        text: str, 
        min_delay: float = 0.03, 
        max_delay: float = 0.1
    ) -> None:
        """
        Type text with human-like patterns
        
        Args:
            element: Selenium WebElement
            text: Text to type
            min_delay: Minimum delay between keystrokes
            max_delay: Maximum delay between keystrokes
        """
        try:
            self.logger.debug(f"Human-like typing: {len(text)} characters")
            
            for i, char in enumerate(text):
                # Gaussian distribution for natural timing
                delay = np.random.normal(
                    (min_delay + max_delay) / 2, 
                    (max_delay - min_delay) / 6
                )
                delay = max(min_delay, min(max_delay, delay))
                
                # Occasional typos and corrections (1% chance)
                if random.random() < 0.01 and i > 0:
                    # Type wrong character
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    element.send_keys(wrong_char)
                    time.sleep(delay)
                    
                    # Backspace and correct
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(delay * 0.5)
                
                # Type actual character
                element.send_keys(char)
                
                # Variable delay based on character type
                if char in ' \n\t':
                    time.sleep(delay * 1.5)  # Longer pause after spaces
                elif char in '.,!?;:':
                    time.sleep(delay * 2.0)  # Longer pause after punctuation
                else:
                    time.sleep(delay)
            
            self.logger.debug("Human-like typing completed")
            
        except Exception as e:
            self.logger.error(f"Human-like typing failed: {e}")
            # Fallback to simple send_keys
            element.send_keys(text)
    
    def human_like_mouse_movement(self, driver: webdriver.Chrome) -> None:
        """
        Perform human-like mouse movements
        
        Args:
            driver: Chrome WebDriver instance
        """
        try:
            action = ActionChains(driver)
            
            # Get window size
            window_size = driver.get_window_size()
            max_x = window_size['width'] - 100
            max_y = window_size['height'] - 100
            
            # Random destination
            target_x = random.randint(100, max_x)
            target_y = random.randint(100, max_y)
            
            # Move in curved path
            steps = random.randint(5, 10)
            for step in range(steps):
                # Calculate intermediate position with some randomness
                progress = (step + 1) / steps
                current_x = int(target_x * progress + random.randint(-20, 20))
                current_y = int(target_y * progress + random.randint(-20, 20))
                
                # Ensure coordinates are within bounds
                current_x = max(0, min(max_x, current_x))
                current_y = max(0, min(max_y, current_y))
                
                action.move_by_offset(current_x, current_y)
                time.sleep(random.uniform(0.01, 0.03))
            
            action.perform()
            self.logger.debug("Human-like mouse movement completed")
            
        except Exception as e:
            self.logger.warning(f"Mouse movement failed: {e}")
    
    def random_scroll(self, driver: webdriver.Chrome) -> None:
        """
        Perform random scrolling to simulate human behavior
        
        Args:
            driver: Chrome WebDriver instance
        """
        try:
            # Random scroll direction and amount
            scroll_directions = ['up', 'down']
            direction = random.choice(scroll_directions)
            
            if direction == 'down':
                scroll_amount = random.randint(100, 500)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            else:
                scroll_amount = random.randint(100, 300)
                driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
            
            # Small pause after scrolling
            time.sleep(random.uniform(0.5, 1.5))
            
            self.logger.debug(f"Random scroll: {direction} {scroll_amount}px")
            
        except Exception as e:
            self.logger.warning(f"Random scroll failed: {e}")
    
    def random_wait(
        self, 
        min_seconds: float = 0.5, 
        max_seconds: float = 2.0
    ) -> None:
        """
        Wait for a random duration to simulate human behavior
        
        Args:
            min_seconds: Minimum wait time
            max_seconds: Maximum wait time
        """
        wait_time = random.uniform(min_seconds, max_seconds)
        self.logger.debug(f"Random wait: {wait_time:.2f}s")
        time.sleep(wait_time)
    
    def cleanup_driver(self, driver: webdriver.Chrome) -> None:
        """
        Clean up driver resources
        
        Args:
            driver: Chrome WebDriver instance
        """
        try:
            if driver:
                self.logger.debug("Cleaning up driver")
                driver.quit()
                
                # Remove from tracked drivers
                for service, tracked_driver in list(self.drivers.items()):
                    if tracked_driver == driver:
                        del self.drivers[service]
                        break
                
                self.logger.debug("Driver cleanup completed")
                
        except Exception as e:
            self.logger.warning(f"Driver cleanup failed: {e}")
    
    def cleanup_all_drivers(self) -> None:
        """Clean up all managed drivers"""
        for service, driver in list(self.drivers.items()):
            self.cleanup_driver(driver)
        self.drivers.clear()
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """
        Get configuration for specific service
        
        Args:
            service_name: Service name
            
        Returns:
            Service configuration dict
            
        Raises:
            ConfigurationError: If service config not found
        """
        if service_name not in self.config:
            raise ConfigurationError(
                service_name, 
                f"Service '{service_name}' not found in configuration"
            )
        
        return self.config[service_name]
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup all drivers"""
        self.cleanup_all_drivers()
        
        # Log any exceptions
        if exc_type:
            self.logger.error(f"Exception in context: {exc_type.__name__}: {exc_val}")
        
        return False  # Don't suppress exceptions