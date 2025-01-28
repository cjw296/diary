Chris's Diary
=============

Well, it's more of a journal really...

Setup
-----

In your git clone:

.. code-block:: bash

  uv sync
  cd frontend
  nvm install
  nvm use
  npm install

If the FastAPI routes or functions serving them change:

.. code-block:: bash

  ./generate-client.sh

To get the database into the right shape:

.. code-block:: bash

  uv run alembic upgrade head

Running Scripts
---------------

.. code-block:: bash

  uv run ingest.py --help

Running the backend
-------------------

.. code-block:: bash

  uv run fastapi dev api/

Running the frontend
--------------------

.. code-block:: bash

  cd frontend
  nvm use

  npx vite -d
  # ...or:
  npm run vite
