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

# @todo Evaluate if https://github.com/astral-sh/uv can make this use case easier
if ! diff .venv/requirements.txt <(head -n 1000 backend/requirements-*.txt) >/dev/null 2>&1
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
