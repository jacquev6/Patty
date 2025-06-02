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
done < <(find . -name '*.template' -not -path './.venv/*' -not -path './support/dev-env/backend/pip-packages/*')
$ok

# @todo Evaluate if https://github.com/astral-sh/uv can make this use case easier
if ! diff .venv/requirements.txt <(head -n 1000 backend/requirements-*.txt) >/dev/null 2>&1
then
  rm -rf .venv
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip
  for req in backend/requirements-*.txt
  do
    pip install -r $req
  done
  head -n 1000 backend/requirements-*.txt >.venv/requirements.txt
fi

. .venv/bin/activate

PYTHONPATH=support python -m tool "$@"
