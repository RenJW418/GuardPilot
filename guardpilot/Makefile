API_PORT ?= 8000
WEB_PORT ?= 5173

.PHONY: replay api web test clean

replay:
	python scripts/replay.py --scenario samples/scenarios/btc_momentum_crash.json

api:
	uvicorn guardpilot.main:app --app-dir apps/api --reload --port $(API_PORT)

web:
	cd apps/web && npm run dev -- --host 0.0.0.0 --port $(WEB_PORT)

test:
	PYTHONPATH=apps/api pytest apps/api/guardpilot/tests

clean:
	rm -f guardpilot.db
	rm -f samples/outputs/*.json samples/outputs/*.jsonl
	rm -f reports/*.json reports/*.html
