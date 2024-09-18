# mcr-accidents-analyzer

So, the city (marechal candido rondon) I live has - I think - a problem with too
many accidents on roundabouts. At least, that's my theory.

This scrapes our local news site for accidents for as long as it can, and then
uses AI to try to categorize each, put them in a database, so I can extract
information from it to see whether my hunch is correct or not.

The python code was written by claude and i just made some minor modifications.

PS: this is obviously not 100% accurate.

---

## methodology

- scraped all 2 news websites for traffic accident news (opresente and
  marechalnews)
- then, excluded accidents that happened outside the city (BR-123, PR-123)
- download each news page, scrape content, store in a database
- database is then populated based on some words in its content (e.g. rotatoria,
  pedestre, carro)

## future

- correlate this with population and number of vehicles in the city
- run the dbs through an AI to extract the address and number of victims (like
  the `first_try` folder)
