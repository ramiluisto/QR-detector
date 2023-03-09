# QR detector endpoints

*What?* A self-contained docker system to create a REST api to find QR codes in pdfs. Both file upload and url-based versions available.

*Why?* Because AFR can't do it directly.

*How?* Use instructions below to run the unit tests and/or start the container.

### Caveats

Doesn't sometimes detect very small pixel qr-codes, see e.g. `./tests/test_data/tight_codes.pdf` for an example where
the system does not (currently) find the qr-code on the first page. Look also at the pagewise counts for `./tests/test_data/Increasing_qr_count.pdf`. Large QR-codes seem to be okay, see e.g. `./tests/test_data/LargeQR.pdf`.



## Docker build and system start

Run:
```
docker build -t qrsystem .
docker run -p 5055:5055 qrsystem
```

Then take your browser to `localhost:5055`, the fastAPI Swagger docs are waiting for you there together with UI for 
endpoint testing.
Alternatively you can just use Postman to call the endpoints at `localhost:5055/QR-detection-via-URL/` and `localhost:5055/QR-detection-via-file-upload/`. Exact input requirements are found from the docs at `localhost:5055`.



## Testing

Run:
```
conda create --name qr_env python=3.9
conda activate qr_env
pip install -r requirements.txt
python -m pytest
```

We run `python -m pytest` because plain `pytest` fails on the current local machine, probably due to 
global package installation stuff.


For coverage, run 
```
coverage run -m pytest
coverage report -im
```

The `m` flag is needed due to some weird error with coverage and maybe openCV? Without `i` the system complains about
`No source for code: '~/QRDocker/config-3.py'.`
