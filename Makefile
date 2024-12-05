initialize:
	uv venv --python 3.12
	mkdir dependencies
	git clone --branch v0.15.0 https://github.com/openmc-dev/openmc.git dependencies/openmc
	git clone --branch v1.1 https://github.com/luca-fiorito-11/sandy.git dependencies/sandy
	CC=gcc CXX=gcc cd dependencies/openmc && \
	   mkdir build && \
	   cd build && \
	   cmake -DCMAKE_BUILD_TYPE=Release .. && \
	   make -j
	CC=gcc CXX=gcc uv pip install dependencies/openmc
	uv pip install dependencies/sandy
	uv pip install -e .
	uv pip install ruff pylint pytest pytest-env pytest-cov
	uv pip install build twine
	uv pip install sphinx pydata_sphinx_theme sphinx_design sphinx-autodoc-typehints sphinx-copybutton
clean:
	rm -rf dependencies .venv
format:
	uv run ruff format ndmanager
lint:
	uv run ruff check ndmanager
pylint:
	uv run pylint ndmanager
