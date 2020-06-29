# parse-medici-torino

Script per trasformare i pdf dei medici di medicina generale della ASL Città di Torino in formato
machine readable.

## Requisiti

Il programma di conversione richiede python 3 installato.

## Uso

Per prima cosa bisogna trasformare i pdf forniti dalla ASL in testo. Due opzioni testate sono:
- `pdftotext`, dal progetto `poppler`
- `Apache PDFBox`, richiede Java

I file in pdf sono scaricabili da questa [pagina](http://www.aslcittaditorino.it/medici-di-medicina-generale-mmg-e-pediatri-di-libera-scelta-pls/)

### Conversione pdf con pdftotext

Da una distribuzione Linux installare il pacchetto di utilities di `poppler`. 

Ad esempio su Debian:

```
sudo apt install poppler-utils
```

Mentre su MacOS si trova su brew:

```
sudo brew install poppler
```

Una volta installato si può convertire il file con:

```
pdftotext miofile.pdf miofile.txt
```

### Conversione pdf con Apache PDFBox

Scaricare la versione `pdfbox-app` dalla pagina di [download](https://pdfbox.apache.org/download.cgi#20x). Al momento l'ultima versione disponibile è la 2.0.20.

Il file pdf si può convertire in testo con:

```
java -jar pdfbox-app-2.0.20.jar miofile.pdf miofile.txt
```

### Creazione dei dati machine readable

Una volta convertito il pdf in testo è possibile trasformarlo in formato `json`:

```
cat miofile.txt | python3 parse.py > miofile.json
```
