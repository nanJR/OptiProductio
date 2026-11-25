"""Small web server: serves the dashboard page and its JSON API."""
from __future__ import annotations

import os

from flask import Flask, Response, jsonify, request, send_from_directory

STATIC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")


def make_app(engine):
    app = Flask(__name__, static_folder=None)

    @app.get("/")
    def index():
        return send_from_directory(STATIC, "index.html")

    @app.get("/report")
    def report():
        return send_from_directory(STATIC, "report.html")

    @app.get("/static/<path:name>")
    def static_files(name):
        return send_from_directory(STATIC, name)

    @app.get("/api/state")
    def state():
        return jsonify(engine.snapshot())

    @app.get("/api/runs")
    def runs():
        return jsonify(engine.run_summaries())

    @app.post("/api/limit")
    def limit():
        n = int((request.get_json(silent=True) or {}).get("limit", 0))
        engine.set_limit(n)
        return jsonify(ok=True, limit=n)

    @app.post("/api/buffer")
    def buffer():
        d = request.get_json(silent=True) or {}
        n = max(1, min(3600, int(d.get("buffer_s", 10))))
        st = int(d.get("station", 0))          # 0 = all stations, 1..3 = one station
        engine.set_buffer(n, st)
        return jsonify(ok=True, buffer_s=n, station=st if st in (1, 2, 3) else 0)

    @app.post("/api/reset")
    def reset():
        engine.reset_line()
        return jsonify(ok=True)

    @app.post("/api/ping")
    def ping():
        engine.ping()
        return jsonify(ok=True)

    @app.post("/api/run")
    def new_run():
        label = (request.get_json(silent=True) or {}).get("label")
        return jsonify(ok=engine.new_run(label))

    @app.post("/api/scrap")
    def scrap():
        return jsonify(ok=engine.mark_scrap())

    @app.post("/api/config")
    def config():
        engine.update_cfg(request.get_json(silent=True) or {})
        return jsonify(ok=True, cfg=engine.cfg)

    @app.get("/api/export/<int:run_id>.csv")
    def export(run_id):
        return Response(engine.export_events_csv(run_id), mimetype="text/csv",
                        headers={"Content-Disposition": f"attachment; filename=optiproductio_run_{run_id}.csv"})

    return app
