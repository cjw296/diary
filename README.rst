Chris's Diary
=============

Well, it's more of a journal really...

Setup
-----

In your git clone:

.. code-block:: bash

  poetry install

Running the backend
-------------------

Put something like the following in a file called ``app.yml`` in the root of your checkout::

    db:
      url: postgres://user:pass@localhost:5432/diary

Now:

.. code-block:: bash

  alembic upgrade head
  uvicorn diary:app --reload --port 9000
