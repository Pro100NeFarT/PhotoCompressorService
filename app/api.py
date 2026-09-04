import base64
import logging

from flask import Flask, jsonify, redirect, render_template, request

from . import config as cfg_module
from . import demo, update_checker
from .compressor import CompressionError, compress_image

log = logging.getLogger("photocompressor")


def _int_param(body: dict, key: str, default: int) -> int:
    value = body.get(key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        raise CompressionError(f"Параметр '{key}' має бути цілим числом")


def create_app(cfg: dict) -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = int(cfg["max_upload_mb"]) * 1024 * 1024
    comp_defaults = cfg["compression"]
    update_cfg = cfg["update"]
    update_cache = update_checker.UpdateCache()

    @app.get("/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": cfg_module.APP_NAME,
            "version": cfg_module.VERSION,
        })

    @app.get("/")
    @app.get("/test")
    def main_page():
        return render_template(
            "test.html",
            defaults=comp_defaults,
            version=cfg_module.VERSION,
            github_url=cfg_module.GITHUB_URL,
            demo=demo.get_demo_pair(),
        )

    @app.post("/compress")
    def compress():
        body = request.get_json(silent=True)
        if body is None or "image_base64" not in body:
            return jsonify({"success": False, "error": "Очікується JSON з полем 'image_base64'"}), 400

        try:
            # 1С Base64Строка() переносить рядок кожні ~76 символів (\r\n) —
            # приймаємо base64 толерантно (без validate), зайві символи ігноруються.
            raw = base64.b64decode(body["image_base64"], validate=False)
        except Exception:
            return jsonify({"success": False, "error": "Некоректний base64 у полі 'image_base64'"}), 400

        try:
            result = compress_image(
                raw,
                max_width=_int_param(body, "max_width", comp_defaults["max_width"]),
                max_height=_int_param(body, "max_height", comp_defaults["max_height"]),
                max_size_kb=_int_param(body, "max_size_kb", comp_defaults["max_size_kb"]),
                quality_start=_int_param(body, "quality_start", comp_defaults["quality_start"]),
                quality_min=_int_param(body, "quality_min", comp_defaults["quality_min"]),
                quality_step=_int_param(body, "quality_step", comp_defaults["quality_step"]),
                force_format=body.get("force_format"),
            )
        except CompressionError as exc:
            return jsonify({"success": False, "error": str(exc)}), 400
        except Exception:
            log.exception("Непередбачена помилка стиснення")
            return jsonify({"success": False, "error": "Внутрішня помилка сервісу"}), 500

        return jsonify({
            "success": True,
            "changed": result.changed,
            "image_base64": base64.b64encode(result.data).decode("ascii"),
            "format": result.output_format,
            "width": result.width,
            "height": result.height,
            "size_kb": round(result.size_kb, 1),
            "quality_used": result.quality_used,
            "original_format": result.original_format,
            "original_width": result.original_width,
            "original_height": result.original_height,
            "original_size_kb": round(result.original_size_kb, 1),
        })

    @app.get("/update-check")
    def update_check():
        if not update_cfg.get("enabled") or not update_cfg.get("github_repo"):
            return jsonify({"enabled": False})

        force = request.args.get("force") == "1"
        interval_seconds = int(update_cfg.get("check_interval_hours", 24)) * 3600
        current_version = tuple(int(x) for x in cfg_module.VERSION.split("."))

        try:
            release = update_cache.get(update_cfg["github_repo"], interval_seconds, force=force)
        except update_checker.UpdateCheckError as exc:
            log.warning("Перевірка оновлень не вдалась: %s", exc)
            return jsonify({"enabled": True, "error": str(exc)}), 502

        available = release["version"] > current_version
        return jsonify({
            "enabled": True,
            "current_version": cfg_module.VERSION,
            "latest_version": release["tag_name"],
            "update_available": available,
            "download_url": "/update-download" if available else None,
            "asset_name": release["asset_name"],
            "asset_size_mb": round(release["asset_size"] / (1024 * 1024), 1),
            "release_notes_url": release["release_notes_url"],
        })

    @app.get("/update-download")
    def update_download():
        if not update_cfg.get("enabled") or not update_cfg.get("github_repo"):
            return jsonify({"error": "Автооновлення вимкнено в config.json"}), 400
        try:
            release = update_cache.get(update_cfg["github_repo"], 0, force=True)
        except update_checker.UpdateCheckError as exc:
            return jsonify({"error": str(exc)}), 502
        return redirect(release["download_url"])

    @app.errorhandler(413)
    def too_large(_exc):
        return jsonify({"success": False, "error": "Файл перевищує максимально дозволений розмір"}), 413

    return app
