## How To Run
Follow these line below to run this project
### 1. Clone the project

```bash
  git clone https://github.com/Duy-DaoNg/python-face-recognition
```

### 2. Go to the project directory

```bash
  cd python-face-recognition
```

### 3. Run command to start server

```bash
  docker run -it -p 8080:8080 --name python-face-recognition duydaong/python-face-recognition:v1.0.0

```
If you are using Git Bash on a WinOS, run this command instead:
```bash
  winpty docker run -it -p 8080:8080 --name your-container-name duydaong/python-face-recognition:v1.0.0

```

Then open index.html file

## To Build Image

#### After step 2, run this command

```bash
  docker build -t your-image-name .

```
