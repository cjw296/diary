Chris's Diary
=============

Well, it's more of a journal really...

Setup
-----

In your git clone:

.. code-block:: bash

  uv sync

Running Scripts
---------------

uv run ingest.py --help

Running the backend
-------------------

Put something like the following in a file called ``app.yml`` in the root of your checkout::

    db:
      url: postgres://user:pass@localhost:5432/diary

Now:

.. code-block:: bash

  alembic upgrade head
  uvicorn diary.api:app --reload --port 9000 --lifespan on
