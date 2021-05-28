# epub-processing-tests
testing various mini-ideas on epub files, might spin one of these out into its own project eventually

## Named Entity Recognition
Using various NLP libraries to attempt NER to recognize characters in a book. Results were not measured, just eyeballed after running multiple trials.

#### NLTK NER
- slowest of all NER I've tries, far slower than all others
- least accurate of all I've tried
- - has different NER models built in: I tried Senna

#### spacy NER
- fastest of all 3
- middle accuracy
- does not require download to run

#### stanza NER
- best accuracy
- middle speed

## Epub reading
Getting text data from epub files.

#### ebooklib
- has many finctions to edit data and metadata of epubs and various files within
- a bit overcomplicated to just get text with it
- still needs HTML processing after getting all text

## Google Docs uploading
Experimenting with saving DataFrames as Google Doc spreadsheets. For linking/sharing, not for frequently accessed or overly large datasets.

#### df2gspread
- very simple for simple uploading and downloading of spreadsheets from and to DataFrames
- seems overly complicated to setup API - may be same for all libraries that do this?
- is the .gdrive_private file needed forever?
