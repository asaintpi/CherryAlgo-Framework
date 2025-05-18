import configparser
import os
from pathlib import Path
import logging

APP_NAME = "CherryAlgoFramework"
CONFIG_DIR_NAME = "config"
CONFIG_FILE_NAME = "settings.ini"
CONFIG_TEMPLATE_NAME = "settings_template.ini"

 
module_logger = logging.getLogger(__name__)

def find_config_path() -> Path:
    current_path = Path(__file__).resolve()
    project_root = None
    for parent in current_path.parents:
        if (parent / "src").exists() and (parent / CONFIG_DIR_NAME).exists():
            project_root = parent
            break
    
    if not project_root:
        
        for parent in current_path.parents:
            if (parent / CONFIG_DIR_NAME).exists():
                project_root = parent
                break
        if not project_root:
            raise FileNotFoundError(
                f"Could not determine project root to find '{CONFIG_DIR_NAME}' directory."
            )

    config_file_path = project_root / CONFIG_DIR_NAME / CONFIG_FILE_NAME
    if config_file_path.exists():
        return config_file_path

    template_file_path = project_root / CONFIG_DIR_NAME / CONFIG_TEMPLATE_NAME
    if template_file_path.exists():
        module_logger.warning(
            f"'{CONFIG_FILE_NAME}' not found. Using template '{template_file_path.name}'. "
            "Please create and configure 'settings.ini' for your environment."
        )
        return template_file_path

    raise FileNotFoundError(
        f"Neither '{CONFIG_FILE_NAME}' nor '{CONFIG_TEMPLATE_NAME}' found in '{project_root / CONFIG_DIR_NAME}'"
    )

class Config:
    _instance = None
    _config_parser = None
    _config_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            try:
                cls._config_path = find_config_path()
                cls._config_parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
                cls._config_parser.read(cls._config_path)
                module_logger.info(f"Configuration loaded from: {cls._config_path}")
            except (FileNotFoundError, configparser.Error) as e:
                module_logger.error(f"Failed to load configuration: {e}", exc_info=False)
                 
                cls._config_parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation()) # Empty parser
                module_logger.warning("Operating with an empty configuration due to previous errors.")
        return cls._instance

    def get(self, section: str, key: str, fallback: str = None) -> str | None:
        try:
            value = self._config_parser.get(section, key)
             
            if value and value.startswith("${") and value.endswith("}"):
                env_var_name = value[2:-1]
                env_value = os.getenv(env_var_name)
                if env_value is not None:
                    return env_value
                else:
                    module_logger.warning(f"Environment variable '{env_var_name}' for config {section}.{key} not found.")  
                    if value == f"${{{env_var_name}}}" and fallback is not None:
                        return fallback
                    return value # return the "${...}" string itself
            return value
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            module_logger.warning(f"Config key '{key}' not found in section '{section}' and no fallback provided.")
            return None
        except Exception as e:
            module_logger.error(f"Error getting config {section}.{key}: {e}")
            return fallback

    def getint(self, section: str, key: str, fallback: int = None) -> int | None:
        value_str = self.get(section, key)
        if value_str is not None:
            try:
                return int(value_str)
            except ValueError:
                module_logger.error(f"Config value for {section}.{key} ('{value_str}') is not a valid integer.")
                if fallback is not None: return fallback
                return None
        return fallback

    def getfloat(self, section: str, key: str, fallback: float = None) -> float | None:
        value_str = self.get(section, key)
        if value_str is not None:
            try:
                return float(value_str)
            except ValueError:
                module_logger.error(f"Config value for {section}.{key} ('{value_str}') is not a valid float.")
                if fallback is not None: return fallback
                return None
        return fallback

    def getboolean(self, section: str, key: str, fallback: bool = None) -> bool | None:
        value_str = self.get(section, key)
        if value_str is not None:
            try:
                return self._config_parser.getboolean(section, key)  
            except ValueError:  
                module_logger.error(f"Config value for {section}.{key} ('{value_str}') is not a standard boolean.")
                if fallback is not None: return fallback
                return None
        return fallback

    def get_list(self, section: str, key: str, delimiter: str = ",", fallback: list = None) -> list | None:
        value_str = self.get(section, key)
        if value_str:
            return [item.strip() for item in value_str.split(delimiter)]
        return fallback if fallback is not None else []

    @property
    def config_file_loaded(self) -> Path | None:
        return self._config_path if self._config_path and self._config_path.exists() else None

app_config = Config()

if __name__ == '__main__':
    print(f"Attempting to load configuration from: {app_config.config_file_loaded}")
    if app_config.config_file_loaded:
        print(f"Market Provider: {app_config.get('MarketData', 'PROVIDER_NAME', 'N/A')}")
        print(f"Initial Equity: {app_config.getfloat('BrokerSimulated', 'INITIAL_EQUITY', 0.0)}")
        print(f"Default Tickers: {app_config.get_list('MarketData', 'DEFAULT_TICKERS', fallback=['ERROR'])}")
        print(f"Non-existent key: {app_config.get('MarketData', 'NON_EXISTENT_KEY', 'DefaultValueForMissing')}")
        print(f"Log Level: {app_config.get('Logging', 'LOG_LEVEL', 'INFO')}")
        print(f"Test env var substitution (set TEST_API_KEY env var to see it work): {app_config.get('MarketData', 'API_KEY', 'API_KEY_NOT_SET')}")
    else:
        print("Failed to load any configuration file.")