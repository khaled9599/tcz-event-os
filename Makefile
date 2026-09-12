.PHONY: test demo

test:
	pytest -q

demo:
	python examples/jotun_kanva/run_vertical_slice.py
