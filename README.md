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

In example:

```console
$ jonas url "https://jonas.irht.cnrs.fr/consulter/manuscrit/detail_manuscrit.php?projet=72048"
Scraping... ⠏
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Manuscript(                                                                                                   │
│     id='72048',                                                                                               │
│     exemplar='Paris, Bibliothèque nationale de France, Manuscrits, nouv. acq. fr. 01158',                     │
│     date='c. 1545-1550',                                                                                      │
│     language=None                                                                                             │
│ )                                                                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
─────────────────────────────────────────────────── Witnesses ───────────────────────────────────────────────────
Witness(
    id='temoin79902',
    doc_id='72048',
    work_id='3379',
    date=None,
    siglum=None,
    status=None,
    foliation='Folio 2r - 12v'
)
Witness(
    id='temoin78974',
    doc_id='72048',
    work_id='3381',
    date=None,
    siglum=None,
    status=None,
    foliation='Folio 13r - 23r'
)
```

### CSV Batch

When scraping a batch of URLs, the in-file needs to be a CSV with a column containing the URL of a manuscript or work record in Jonas's online database. The column can contain both. The program will sort them accordingly.

|jonas_url|
|--|
|http://jonas.irht.cnrs.fr/manuscrit/72924|
|http://jonas.irht.cnrs.fr/oeuvre/10453|
|http://jonas.irht.cnrs.fr/manuscrit/60326|

Run the following command:

```console
jonas scrape -i CSV -c COLUMN -d DATABASE
```
