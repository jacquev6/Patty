set -o errexit
set -o nounset
set -o pipefail


ok=true
while read template
do
  file=${template%.template}
  if ! [ -f "$file" ]
  then
    echo "Please create '$file' according to '$template'"
    ok=false
  fi
done < <(find . -name '*.template')
$ok

if ! (diff .venv/requirements-dev.txt backend/requirements-dev.txt && diff .venv/requirements-run.txt backend/requirements-run.txt) >/dev/null 2>&1
then
  rm -rf .venv
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip
  pip install -r backend/requirements-dev.txt -r backend/requirements-run.txt
  cp backend/requirements-dev.txt backend/requirements-run.txt .venv/
fi

. .venv/bin/activate

PYTHONPATH=support python -m tool "$@"
