.PHONY: test demo control-room

test:
	pytest -q

demo:
	python examples/jotun_kanva/run_vertical_slice.py

control-room:
	python -m brain.control_room.app
