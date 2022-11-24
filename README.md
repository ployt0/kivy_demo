To run from Linux, see [the github workflow](.github/workflows/python-app.yml).

To run from Windows, which I do worryingly much now:

```shell
set PYTHONPATH=C:\Users\user_name\PycharmProjects\project_name\app;%PYTHONPATH%
cd tests/unit
coverage run --omit="../../app/console_io.py" --source="../../app" -m unittest
coverage report -m --fail-under=90
```
