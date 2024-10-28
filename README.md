# publicisgroupe

Written on Python 3.12.7

### Install dependencies

```bash
python3 -mvenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the application:

```bash
fastapi dev app/main.py
```

### Request example with `curl`

```bash
curl -X POST "http://localhost:8000/upload" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@/path/to/your/file.xlsx"
```

### Requst example with `Postman`

1. Open `Postman`
2. Click on the "New" button or use the `+` tab to create a new request
3. From the dropdown menu next to the URL field select `POST`
4. In the URL field enter `http://localhost:8000/upload`
5. Click on the `Headers` tab below the URL field
6. Add the following headers:
    * `accept: application/json`
    * `Content-Type: multipart/form-data`
7. Click on the `Body` tab below the URL field
8. Select the `form-data` option
9. In the form data section, do the following:
    * In the key field enter: `file`
    * In the value field click on the dropdown (default is `Text`) and select `File`
    * Click on the `Choose Files` button and browse to select your Excel file
10. Click the `Send` button to send the request to the server
11. View the Response
