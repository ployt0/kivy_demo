![python-app workflow](https://github.com/ployt0/quotations_w_unittest/actions/workflows/python-app.yml/badge.svg) [![codecov](https://codecov.io/github/ployt0/quotations_w_unittest/branch/master/graph/badge.svg?token=QB9IXGWLBA)](https://codecov.io/github/ployt0/quotations_w_unittest)

## Running

To run from Linux, see [the github workflow](.github/workflows/python-app.yml).

To run from Windows, which I do worryingly much now:

```shell
set PYTHONPATH=C:\Users\<<user_name>>\PycharmProjects\quotations_w_unittest\app;%PYTHONPATH%
cd tests/unit
coverage run --omit="../../app/console_io.py" --source="../../app" -m unittest
coverage report -m --fail-under=90
```

## Credits

The quotes were pulled from kaggle, which I have trusted and enjoyed for years.

## Purpose

The quotations are in json form with a lot of extra fields and duplication which I have no need for.

Who needs quotations?

Who doesn't want inspiration?

I was hoping to use them to demonstrate how to use the `unittest` module, but they ended up being so malformed, and huge, that I made it my mission here to clean them up.

Even with a script this was arduous. I was going to demo kivy with this but found having 5 keys for 5 solutions to missing punction would be much faster.

As I say arduous. And huge, the unzipped source is 20+ MB. Many of these contain obvious mistakes, especially with spacing. Most notable is a capital in the middle of a word, or more than one. This means several words are joined. Sometimes this happens without a capital. I should run it all through a spell checker. I wonder if the objective of Kaggle here was for us to clean these up.

Anyway they are useful with a meaningful popularity index, that I will discard. In the tests directory I put the top 50 or so for integration testing. There are two occurrences of a capital inside a word. That's pretty dirty for a top 50 quote.

There are 3 methods of cleaning the quotes.

1. `all` - Manually pick what to do with each "middle capital". 5 choices. Progress is saved to the final output, which we pick up from next time.
2. `csv` - Convert to CSV
3. `randomx` - Take random sample of x many.

The default output is a json list of quote: author pairs. Duplicates get removed because they were only duplicated so that they could be entered in multiple categories.

## Usage

Just in case anyone actually wants to try and get some quotation, this is what we should do (taken from [kaggle_normaliser.py](app/kaggle_normaliser.py)):

```shell
cd C:/Users/<<user_name>>/PycharmProjects/quotations_w_unittest
python app/kaggle_normaliser.py all tests/integration/test-quotes.json
```

We run that in the test/workflow pipeline. The `all` method must be tested manually or through a test harness because it requires user input (usually quitting).


https://user-images.githubusercontent.com/25666053/203922336-263d7030-9e7b-4e30-8519-b74980c0f288.mp4

