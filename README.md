# Jonas Manuscript Scraper

Scrape information from Jonas's online database.

- [Get started](#installation)
- [Scrape URLs](#scrape)
- [Export output](#export-output)


## Installation

1. Clone this repository (aka download the software's files) : `git clone git@github.com:LostMa-ERC/JonasScraper.git`
2. Create and activate a virtual Python environment: version 3.12.
3. Install this tool : `pip install .`
4. Test the installation : `jonas --version`

## Scrape

### Step 1.

Scrape metadata from URLs provided in a column (i.e. `jonas_url`) of a CSV file (`example.csv`), progressively save it in a database file and, once finished, write the witnesses to a new CSV file in a directory (i.e. `output_example`).

The URLs in the CSV file should be of a work (_oeuvre_) or manuscript (_manuscrit_). Prints (_imprimé_) are not supported. It is recommended that you clean the set of URLs.

- work's URL looks like this: `https://jonas.irht.cnrs.fr/oeuvre/15841`
- manuscript's URL looks like this: `https://jonas.irht.cnrs.fr/manuscrit/60328`.

Run the `new-urls` command.

```shell
$ jonas new-urls -i example.csv -c jonas_url -o output_example
```

```console
─────────── Results saved in database: 'output_example/jonas.db' ───────────
works        [22]  **************************
manuscripts  [ 6]  *******
witnesses    [34]  ****************************************
Total URLs ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 22/22 0:00:10 • 0:00:00
```

### Step 2.

The URLs provided in the `new-urls` command (see [Step 1](#step-1)) are either a work (_oeuvre_) or manuscript (_manuscrit_), and the command creates the relevant record in the database from the page's scraped metadata. Because work and manuscript pages present witnesses, the `new-urls` command also creates records in the relational witness table, which link works and manuscripts.

The `supplement` command reviews all the witness records created in [Step 1](#step-1) and determines if there is complete metadata for both its associated work and manuscript. It will scrape the missing metadata.

In the [example](./example.csv), as seen in [Step 1](#step-1), we have a list of 22 work URLs. There are 34 witnesses amongst those 22 works, and they are in 6 manuscripts. Because only the work pages' metadata was scraped, the `supplement` command collects the URLs of those 6 related manuscript pages and scrapes them.

```shell
$ jonas supplement -o output_example
```

```console
─────────── Results saved in database: 'output_example/jonas.db' ───────────
works        [22]  **************************
manuscripts  [ 6]  *******
witnesses    [34]  ****************************************
Total URLs ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6/6 0:00:03 • 0:00:00

View a list of witnesses in this CSV file: 'output_example/witnesses_1751380020.239669.csv'
```

id|work_url|ms_url|work_id|work_title|work_author|work_incipit|work_form|work_date|work_language|work_n_verses|work_meter|work_rhyme_scheme|work_scripta|work_keywords|work_links|witness_id|witness_doc_id|witness_work_id|witness_date|witness_siglum|witness_status|witness_foliation|manuscript_id|manuscript_exemplar|manuscript_date|manuscript_language
|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|
temoin36017|http://jonas.irht.cnrs.fr/oeuvre/10000|http://jonas.irht.cnrs.fr/manuscrit/72186|10000|Ballade|Oton de Grandson|Faitez de moy tout ce qu'il vous plaira|vers|2e moitié du 14e s.|oil-français|||||||temoin36017|72186|10000|vers 1430|A|intégral|Folio 134r - 134v|72186|Paris, Bibliothèque nationale de France, Manuscrits, fr. 02201|15e s.|oil-français
temoin36016|http://jonas.irht.cnrs.fr/oeuvre/10000|http://jonas.irht.cnrs.fr/manuscrit/72191|10000|Ballade|Oton de Grandson|Faitez de moy tout ce qu'il vous plaira|vers|2e moitié du 14e s.|oil-français|||||||temoin36016|72191|10000|vers 1430|A|intégral|Folio 134r - 134v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36018|http://jonas.irht.cnrs.fr/oeuvre/10001|http://jonas.irht.cnrs.fr/manuscrit/72186|10001|Ballade|Oton de Grandson|Je n'ay riens fait qu'amours ne me fait faire|vers|2e moitié du 14e s.|oil-français|||||||temoin36018|72186|10001|vers 1430|A|intégral|Folio 135r - 135v|72186|Paris, Bibliothèque nationale de France, Manuscrits, fr. 02201|15e s.|oil-français
temoin36019|http://jonas.irht.cnrs.fr/oeuvre/10001|http://jonas.irht.cnrs.fr/manuscrit/72191|10001|Ballade|Oton de Grandson|Je n'ay riens fait qu'amours ne me fait faire|vers|2e moitié du 14e s.|oil-français|||||||temoin36019|72191|10001|vers 1430|A|intégral|Folio 135r - 135v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36020|http://jonas.irht.cnrs.fr/oeuvre/10001|http://jonas.irht.cnrs.fr/manuscrit/71827|10001|Ballade|Oton de Grandson|Je n'ay riens fait qu'amours ne me fait faire|vers|2e moitié du 14e s.|oil-français|||||||temoin36020|71827|10001|vers 1430|A|intégral|Folio 135r - 135v|71827|Paris, Bibliothèque nationale de France, Manuscrits, Rothschild 2796 (432 a)|milieu 15e s.|oil-français
temoin36029|http://jonas.irht.cnrs.fr/oeuvre/10002|http://jonas.irht.cnrs.fr/manuscrit/72191|10002|Ballade|Oton de Grandson|A ce plaisant premier jour de l'annee|vers|2e moitié du 14e s.|oil-français|||||||temoin36029|72191|10002|vers 1430|A|intégral|Folio 138r - 138v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36030|http://jonas.irht.cnrs.fr/oeuvre/10003|http://jonas.irht.cnrs.fr/manuscrit/72191|10003|Ballade|Oton de Grandson|En grant deduit et en doulce plaisance|vers|2e moitié du 14e s.|oil-français|||||||temoin36030|72191|10003|1826|||Folio 61r - 61r|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin61500|http://jonas.irht.cnrs.fr/oeuvre/10003|http://jonas.irht.cnrs.fr/manuscrit/75963|10003|Ballade|Oton de Grandson|En grant deduit et en doulce plaisance|vers|2e moitié du 14e s.|oil-français|||||||temoin61500|75963|10003|1826|||Folio 61r - 61r|75963|BESANCON, Bibliothèque municipale, 0556|1826|oil-français
temoin36032|http://jonas.irht.cnrs.fr/oeuvre/10004|http://jonas.irht.cnrs.fr/manuscrit/72191|10004|Rondeau|Oton de Grandson|Bien appert, Belle, a vo bonté / Et a vostre maintenement|vers|2e moitié du 14e s.|oil-français|||||||temoin36032|72191|10004|1826|||Folio 61v - 61v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin61501|http://jonas.irht.cnrs.fr/oeuvre/10004|http://jonas.irht.cnrs.fr/manuscrit/75963|10004|Rondeau|Oton de Grandson|Bien appert, Belle, a vo bonté / Et a vostre maintenement|vers|2e moitié du 14e s.|oil-français|||||||temoin61501|75963|10004|1826|||Folio 61v - 61v|75963|BESANCON, Bibliothèque municipale, 0556|1826|oil-français
temoin36033|http://jonas.irht.cnrs.fr/oeuvre/10005|http://jonas.irht.cnrs.fr/manuscrit/72191|10005|Ballade|Oton de Grandson|Car j'ay perdu ma jeunesse et ma joye|prose|2e moitié du 14e s.|oil-français|||||||temoin36033|72191|10005|vers 1430|A|intégral|Folio 139r - 139v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36034|http://jonas.irht.cnrs.fr/oeuvre/10006|http://jonas.irht.cnrs.fr/manuscrit/72191|10006|Rondeau|Oton de Grandson|Comment seroit que je fusse joieulx|vers|2e moitié du 14e s.|oil-français|||||||temoin36034|72191|10006|vers 1430|A|intégral|Folio 139v - 140r|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36036|http://jonas.irht.cnrs.fr/oeuvre/10007|http://jonas.irht.cnrs.fr/manuscrit/72191|10007|Rondeau|Oton de Grandson|Belle, pour hair faulceté / Et vous servir de cuer d'amy|vers|2e moitié du 14e s.|oil-français|||||||temoin36036|72191|10007|vers 1430||intégral|Folio 140v - 140v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36041|http://jonas.irht.cnrs.fr/oeuvre/10008|http://jonas.irht.cnrs.fr/manuscrit/72191|10008|Rondeau|Oton de Grandson|Ce premier jour que l'an se renouvelle|vers|2e moitié du 14e s.|oil-français|||||||temoin36041|72191|10008|vers 1430||intégral|Folio 142r - 142v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36043|http://jonas.irht.cnrs.fr/oeuvre/10009|http://jonas.irht.cnrs.fr/manuscrit/72191|10009|Ballade|Oton de Grandson|En languissant defineront my jour|vers|2e moitié du 14e s.|oil-français|||||||temoin36043|72191|10009|vers 1430||intégral|Folio 142v - 143r|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36045|http://jonas.irht.cnrs.fr/oeuvre/10010|http://jonas.irht.cnrs.fr/manuscrit/72193|10010|Ballade|Oton de Grandson|Pour mieulx garder de ma dame le fort|vers|2e moitié du 14e s.|oil-français|||||||temoin36045|72193|10010|vers 1430|A|intégral|Folio 143r - 143v|72193|PHILADELPHIA, University of Pennsylvania Library, Codex 0902|vers 1390|oil-français
temoin36044|http://jonas.irht.cnrs.fr/oeuvre/10010|http://jonas.irht.cnrs.fr/manuscrit/72191|10010|Ballade|Oton de Grandson|Pour mieulx garder de ma dame le fort|vers|2e moitié du 14e s.|oil-français|||||||temoin36044|72191|10010|vers 1430|A|intégral|Folio 143r - 143v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36047|http://jonas.irht.cnrs.fr/oeuvre/10011|http://jonas.irht.cnrs.fr/manuscrit/72191|10011|Ballade|Oton de Grandson|S'a ma cause perdoit sa bonne fame|vers|2e moitié du 14e s.|oil-français|||||||temoin36047|72191|10011|vers 1430|A|intégral|Folio 143v - 144r|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36046|http://jonas.irht.cnrs.fr/oeuvre/10011|http://jonas.irht.cnrs.fr/manuscrit/72193|10011|Ballade|Oton de Grandson|S'a ma cause perdoit sa bonne fame|vers|2e moitié du 14e s.|oil-français|||||||temoin36046|72193|10011|vers 1430|A|intégral|Folio 143v - 144r|72193|PHILADELPHIA, University of Pennsylvania Library, Codex 0902|vers 1390|oil-français
temoin36048|http://jonas.irht.cnrs.fr/oeuvre/10012|http://jonas.irht.cnrs.fr/manuscrit/72191|10012|Ballade|Oton de Grandson|Quant je pense a vo doulce figure|vers|2e moitié du 14e s.|oil-français|||||||temoin36048|72191|10012|vers 1430|A|intégral|Folio 144r - 144v|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français
temoin36049|http://jonas.irht.cnrs.fr/oeuvre/10013|http://jonas.irht.cnrs.fr/manuscrit/72193|10013|Ballade|Oton de Grandson|Se je m'en dueil, nul ne m'en doyt blasmer|vers|2e moitié du 14e s.|oil-français|||||||temoin36049|72193|10013|vers 1430|A|intégral|Folio 144v - 145r|72193|PHILADELPHIA, University of Pennsylvania Library, Codex 0902|vers 1390|oil-français
temoin36050|http://jonas.irht.cnrs.fr/oeuvre/10013|http://jonas.irht.cnrs.fr/manuscrit/72191|10013|Ballade|Oton de Grandson|Se je m'en dueil, nul ne m'en doyt blasmer|vers|2e moitié du 14e s.|oil-français|||||||temoin36050|72191|10013|vers 1430|A|intégral|Folio 144v - 145r|72191|LAUSANNE, Bibliothèque cantonale et universitaire, Ms 350|vers 1430|oil-français