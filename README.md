# Jonas Manuscript Scraper

Scrape information from Jonas's online database.

- [Get started](#install-program)
- [Scrape URLs](#run-program)
- [Export output](#export-output)

## Install Program

1. Clone this repository (aka download the software's files) : `git clone git@github.com:LostMa-ERC/JonasScraper.git`
2. Create and activate a virtual Python environment: version 3.12.
3. Install this tool : `pip install .`
4. Test the installation : `jonas --version`

## Run Program

Users can [scrape a single URL](#single-url), directly from the command line, or a [batch of URLs](#csv-batch) in a CSV.

Because webpages of works and manuscripts from Jonas contain links to multiple other entities, such as witnesses, it is recommended to save the SQL database that the program creates internally to a persistent file. This also allows you to do the following:

1. Stop and restart the data collection without redoing URLs the program already scraped and saved in the database.

2. Access all the information after scraping more than one URL.

### Single URL

To scrape a single URL from the command line, run the following command:

```shell
jonas url URL
```

In example (manuscript URL):

```console
$ jonas url "http://jonas.irht.cnrs.fr/manuscrit/72035"
Scraping... ⠧
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Manuscript(                                                                                                   │
│     id='72035',                                                                                               │
│     exemplar='Paris, Bibliothèque nationale de France, Manuscrits, fr. 00842',                                │
│     date=None,                                                                                                │
│     language=None                                                                                             │
│ )                                                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Fetching URLs... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 46/46 0:00:07
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Witness                           ┃ Work                                                                      ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Witness(                          │ Work(                                                                     │
│     id='temoin77336',             │     id='29538',                                                           │
│     doc_id='72035',               │     title='Epitaphe de Guillaume Budé',                                   │
│     work_id='29538',              │     author='Mellin de Saint-Gelais',                                      │
│     date=None,                    │     incipit="Qui est ce corps qu'un si grand peuple suyt",                │
│     siglum=None,                  │     form='vers',                                                          │
│     status=None,                  │     date='peu après le 21 août 1540, date de la mort de Guillaume Budé',  │
│     foliation='Folio 114r - 114r' │     language='oil-français',                                              │
│ )                                 │     n_verses='8',                                                         │
│                                   │     meter='Décasyllabes',                                                 │
│                                   │     rhyme_scheme='ABABBCBC',                                              │
│                                   │     scripta=None,                                                         │
│                                   │     keywords=[],                                                          │
│                                   │     links=[]                                                              │
│                                   │ )                                                                         │
```

In example (work URL):

```console
jonas url "http://jonas.irht.cnrs.fr/oeuvre/29538"
Scraping... ⠸
╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Work(                                                                                                       │
│     id='29538',                                                                                             │
│     title='Epitaphe de Guillaume Budé',                                                                     │
│     author='Mellin de Saint-Gelais',                                                                        │
│     incipit="Qui est ce corps qu'un si grand peuple suyt",                                                  │
│     form='vers',                                                                                            │
│     date='peu après le 21 août 1540, date de la mort de Guillaume Budé',                                    │
│     language='oil-français',                                                                                │
│     n_verses='8',                                                                                           │
│     meter='Décasyllabes',                                                                                   │
│     rhyme_scheme='ABABBCBC',                                                                                │
│     scripta=None,                                                                                           │
│     keywords=[],                                                                                            │
│     links=[]                                                                                                │
│ )                                                                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
Fetching URLs... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 9/9 0:00:05
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Witness                      ┃ Manuscript                                                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Witness(                     │ Manuscript(                                                                  │
│     id='temoin105132',       │     id='84066',                                                              │
│     doc_id='84066',          │     exemplar='Paris, Bibliothèque nationale de France, Manuscrits, Dupuy     │
│     work_id='29538',         │ 843',                                                                        │
│     date=None,               │     date=None,                                                               │
│     siglum=None,             │     language='oil-français'                                                  │
│     status=None,             │ )                                                                            │
│     foliation='Page 68 - 68' │                                                                              │
│ )                            │                                                                              │
```

### CSV Batch

When scraping a batch of URLs, the in-file needs to be a CSV with a column containing the URL of a manuscript or work record in Jonas's online database. The column can contain both. The program will sort them accordingly.

|jonas_url|
|--|
|http://jonas.irht.cnrs.fr/manuscrit/72924|
|http://jonas.irht.cnrs.fr/oeuvre/10453|
|http://jonas.irht.cnrs.fr/manuscrit/60326|

Run the following command:

```shell
jonas scrape -i CSV -c COLUMN -o OUTDIR
```

In example:

```console
$ jonas scrape -i example.csv -c jonas_url -o output_example/
Fetching URLs... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3/3 0:00:02
Fetching discovered URLs... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11/11 0:00:03
Find a list of witnesses in the file: './output_example/example_witnesses.csv'
```