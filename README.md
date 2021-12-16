# Parse medici ASL Torino

Script per trasformare i pdf dei medici di medicina generale della ASL Città di Torino in formato
machine readable.

I file in formato JSON sono disponibili nel repository [medici-asl-torino](https://github.com/xrmx/medici-asl-torino).

## Requisiti

Il programma di conversione richiede Python 3 installato e la libreria requests.

Su Debian si installano con:

```
sudo apt install python3 python3-requests
```

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

Scaricare la versione `pdfbox-app` dalla pagina di [download](https://pdfbox.apache.org/download.html). Al momento l'ultima versione stabile è la 2.0.24.

Il file pdf si può convertire in testo con:

```
java -jar pdfbox-app-2.0.24.jar ExtractText miofile.pdf miofile.txt
```

### Creazione dei dati machine readable

Una volta convertito il pdf in testo è possibile trasformarlo in formato `json`:

```
cat miofile.txt | python3 parse.py > miofile.json
```

E` possibile fare il geocoding degli indirizzi tramite l'API di [Mapbox](https://mapbox.com) passando
un token (va bene quello pubblico di default) tramite variabile di ambiente da esportare prima della
conversione con:

```
export MAPBOX_ACCESS_TOKEN=ilmiotoken
```

### Creazione GeoJSON


python3 json2geojson.py miofile.json miofile2.json > miofile.geojson
