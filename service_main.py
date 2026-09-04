import logging
from logging.handlers import RotatingFileHandler

from waitress import serve

from app import config as cfg_module
from app.api import create_app


def setup_logging(cfg: dict) -> None:
    level = getattr(logging, str(cfg.get("log_level", "INFO")).upper(), logging.INFO)
    log_file = cfg_module.log_dir() / "service.log"

    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)
    root.addHandler(logging.StreamHandler())


def main() -> None:
    cfg = cfg_module.load_config()
    setup_logging(cfg)

    log = logging.getLogger("photocompressor")
    log.info("Запуск %s v%s на %s:%s", cfg_module.APP_NAME, cfg_module.VERSION, cfg["host"], cfg["port"])
    log.info("Конфіг: %s", cfg_module.config_path())

    app = create_app(cfg)
    serve(app, host=cfg["host"], port=int(cfg["port"]))


if __name__ == "__main__":
    main()
