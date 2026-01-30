# TODO

## [Nice-to-have] Automate NYT-S Token Retrieval

Achieved by following along with [these instructions](https://github.com/kesyog/crossword?tab=readme-ov-file#extracting-your-subscription-token).

The API call I actually used was

```sh
https://www.nytimes.com/svc/crosswords/v3/104497248/stats-and-streaks.json?date_start=2014-01-01&start_on_monday=true
```

> Is the `104497248` value after `v3/` user-specific? YES, that

and the string value of `Cookie` in **Request Headers** was copied to local file, `cookies.txt` so that the token could be extracted with the following

```python
from pathlib import Path

cookies_in = Path("cookies.txt")
cookies = cookies_in.read_text()

for cook in cookies.split("; "):
    if cook.startswith("NYT-S="):
        token = cook.removeprefix("NYT-S=")
        print(f"{token=}")
```

Could use [playwright](https://playwright.dev/python/docs/intro).

## Collect Puzzles

With `NYT-S` token, puzzles can be retrieved with

```python
import requests

response = requests.get(
    "https://www.nytimes.com/svc/crosswords/v6/puzzle/daily/2025-01-01.json",
    cookies={"NYT-S": token},
    headers={"Accept": "application/json"},
)
```

the content of which can be dumped with

```python
import json
from pathlib import Path

json_out = Path("2025-01-01.json")
json_out.write_text(json.dumps(response.json(), indent=2))
```

> NOTE that it seems like day-of-the-week isn't explicitly included in the response JSON, but can obviously be determined by the date...

## Train an Agent

- Would there be any value added by exposing a model to the rawest data?
  - What non-obvious patterns may be exposed?

## Host Publically

If personal Github pages site is not sufficient, then can start tinkering with the hosting abilities of the Synology NAS devices.
